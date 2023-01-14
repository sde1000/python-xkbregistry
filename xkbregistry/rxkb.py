import enum

from xkbregistry._ffi import ffi, lib


class _keepref:
    """Function wrapper that keeps a reference to another object."""
    def __init__(self, ref, func):
        self.ref = ref
        self.func = func

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)


def _string_or_none(r):
    if r != ffi.NULL:
        return ffi.string(r).decode('utf8')


class RXKBError(Exception):
    """Base for all RXKB exceptions"""
    pass


class RXKBAlreadyParsed(RXKBError):
    """The context has already parsed a ruleset."""
    pass


class RXKBPathError(RXKBError):
    """There was a problem altering the include path of a Context."""
    pass


class RXKBParseError(RXKBError):
    """The ruleset could not be parsed."""
    pass


# Internal helper for logging callback
def _onerror_do_nothing(exception, exc_value, traceback):
    return


@ffi.def_extern(onerror=_onerror_do_nothing)
def _log_handler(user_data, level, message):
    context = ffi.from_handle(user_data)
    if context._log_fn:
        context._log_fn(context, level, ffi.string(message).decode('utf8'))


@enum.unique
class Popularity(enum.IntEnum):
    """Describes the popularity of an item.

    Historically, some highly specialized or experimental definitions
    are excluded from the default list and shipped in separate
    files. If these extra definitions are loaded (see
    Context(load_exotic_rules=True)), the popularity of the item is
    set accordingly.

    If the exotic items are not loaded, all items will have the
    standard popularity.
    """
    RXKB_POPULARITY_STANDARD = lib.RXKB_POPULARITY_STANDARD
    RXKB_POPULATITY_EXOTIC = lib.RXKB_POPULARITY_EXOTIC


class Context:
    """xkbregistry library context

    The context contains general library state, like include paths and
    parsed data. Objects are created in a specific context, and
    multiple contexts may coexist simultaneously. Objects from
    different contexts are completely separated and do not share any
    memory or state.
    """
    def __init__(self, no_default_includes=False, load_exotic_rules=False):
        flags = lib.RXKB_CONTEXT_NO_FLAGS
        if no_default_includes:
            flags = flags | lib.RXKB_CONTEXT_NO_DEFAULT_INCLUDES
        if load_exotic_rules:
            flags = flags | lib.RXKB_CONTEXT_LOAD_EXOTIC_RULES
        context = lib.rxkb_context_new(flags)
        if not context:
            raise RXKBError("Couldn't create RXKB context")
        self._context = ffi.gc(context, _keepref(lib, lib.rxkb_context_unref))
        self._log_fn = None
        # We keep a reference to the handle to keep it alive
        self._userdata = ffi.new_handle(self)
        lib.rxkb_context_set_user_data(self._context, self._userdata)
        self._parsed = False

    def include_path_append(self, path):
        "Append a new entry to the context's include path."
        if self._parsed:
            raise RXKBAlreadyParsed()
        r = lib.rxkb_context_include_path_append(
            self._context, path.encode('utf8'))
        if r != 1:
            raise RXKBPathError("Failed to append to include path")

    def include_path_append_default(self):
        "Append the default include paths to the context's include path."
        if self._parsed:
            raise RXKBAlreadyParsed()
        r = lib.rxkb_context_include_path_append_default(self._context)
        if r != 1:
            raise RXKBPathError("Failed to append default include paths")

    def set_log_level(self, level):
        """Set the current logging level.

        The default level is RXKB_LOG_LEVEL_ERROR. The environment
        variable RXKB_LOG_LEVEL, if set at the time the context was
        created, overrides the default value.  It may be specified as
        a level number or name.
        """
        lib.rxkb_context_set_log_level(self._context, level)

    def get_log_level(self):
        """Return the current logging level."""
        return lib.rxkb_context_get_log_level(self._context)

    def set_log_fn(self, handler):
        """Set a custom function to handle logging messages.

        By default, log messages from this library are printed to
        stderr. This function allows you to replace the default
        behavior with a custom handler. The handler is only called
        with messages which match the current logging level and
        verbosity settings for the context.

        The handler is called with the following arguments:
        - context: this object
        - level: the logging level of the message
        - message: the message itself

        Passing None as the handler restores the default function,
        which logs to stderr.

        NB this implementation uses rxkb_context_set_user_data() on the
        context.  Don't call rxkb_context_set_user_data() if you intend
        to install a custom function to handle logging messages.
        """
        if handler:
            lib._set_log_handler_internal(self._context)
            self._log_fn = handler
        else:
            lib.rxkb_context_set_log_fn(self._context, ffi.NULL)

    def parse(self, ruleset):
        "Parse the given ruleset"
        if self._parsed:
            raise RXKBAlreadyParsed()
        r = lib.rxkb_context_parse(self._context, ruleset.encode('utf8'))
        if r != 1:
            raise RXKBParseError()
        self._parsed = True

    def parse_default_ruleset(self):
        "Parse the default ruleset as configured at build time"
        if self._parsed:
            raise RXKBAlreadyParsed()
        r = lib.rxkb_context_parse_default_ruleset(self._context)
        if r != 1:
            raise RXKBParseError()
        self._parsed = True

    @property
    def models(self):
        "Dictionary mapping model name to Model object"
        if not hasattr(self, '_models'):
            self._models = {}
            if not self._parsed:
                self.parse_default_ruleset()
            model = lib.rxkb_model_first(self._context)
            while model != ffi.NULL:
                x = Model(model)
                self._models[x.name] = x
                model = lib.rxkb_model_next(model)
        return self._models

    @property
    def layouts(self):
        "Dictionary mapping layout fullname to Layout object"
        if not hasattr(self, '_layouts'):
            self._layouts = {}
            if not self._parsed:
                self.parse_default_ruleset()
            layout = lib.rxkb_layout_first(self._context)
            while layout != ffi.NULL:
                x = Layout(layout)
                self._layouts[x.fullname] = x
                layout = lib.rxkb_layout_next(layout)
        return self._layouts

    @property
    def option_groups(self):
        "List of OptionGroup objects"
        if not hasattr(self, '_option_groups'):
            self._option_groups = []
            if not self._parsed:
                self.parse_default_ruleset()
            option_group = lib.rxkb_option_group_first(self._context)
            while option_group != ffi.NULL:
                self._option_groups.append(OptionGroup(option_group))
                option_group = lib.rxkb_option_group_next(option_group)
        return self._option_groups


class Model:
    """An XKB model
    """
    def __init__(self, model):
        self.name = ffi.string(
            lib.rxkb_model_get_name(model)).decode('ascii')
        self.description = _string_or_none(
            lib.rxkb_model_get_description(model))
        self.vendor = _string_or_none(
            lib.rxkb_model_get_vendor(model))
        self.popularity = Popularity(lib.rxkb_model_get_popularity(model))

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"rxkb.Model('{self.name}')"


class Layout:
    """An XKB layout, including an optional variant

    Where the variant is None, the layout is the base layout.

    For example, "us" is the base layout, "us(intl)" is the "intl"
    variant of the layout "us".
    """
    def __init__(self, layout):
        self.name = ffi.string(
            lib.rxkb_layout_get_name(layout)).decode('ascii')
        self.variant = _string_or_none(
            lib.rxkb_layout_get_variant(layout))
        self.brief = _string_or_none(
            lib.rxkb_layout_get_brief(layout))
        self.description = _string_or_none(
            lib.rxkb_layout_get_description(layout))
        self.popularity = Popularity(lib.rxkb_layout_get_popularity(layout))
        self.iso639_codes = frozenset(self._codes(
            layout,
            lib.rxkb_layout_get_iso639_first,
            lib.rxkb_iso639_code_next,
            lib.rxkb_iso639_code_get_code))
        self.iso3166_codes = frozenset(self._codes(
            layout,
            lib.rxkb_layout_get_iso3166_first,
            lib.rxkb_iso3166_code_next,
            lib.rxkb_iso3166_code_get_code))

    @staticmethod
    def _codes(layout, first_fn, next_fn, get_fn):
        code = first_fn(layout)
        while code != ffi.NULL:
            yield ffi.string(get_fn(code)).decode('ascii')
            code = next_fn(code)

    @property
    def fullname(self):
        return f"{self.name}({self.variant})" if self.variant else self.name

    def __str__(self):
        return self.fullname

    def __repr__(self):
        return f"rxkb.Layout('{self.fullname}')"


class OptionGroup:
    """An XKB option group

    Option groups divide the individual options into logical
    groups. Their main purpose is to indicate whether some options are
    mutually exclusive or not.

    Option groups may have a name, but are not required to.
    """
    def __init__(self, option_group):
        self.name = _string_or_none(
            lib.rxkb_option_group_get_name(option_group))
        self.description = _string_or_none(
            lib.rxkb_option_group_get_description(option_group))
        self.allows_multiple = bool(
            lib.rxkb_option_group_allows_multiple(option_group))
        self.popularity = Popularity(
            lib.rxkb_option_group_get_popularity(option_group))
        self.options = {}
        option = lib.rxkb_option_first(option_group)
        while option != ffi.NULL:
            x = Option(option)
            self.options[x.name] = x
            option = lib.rxkb_option_next(option)

    def __repr__(self):
        if self.name:
            return f"rxkb.OptionGroup('{self.name}')"
        return super().__repr__()


class Option:
    """An XKB option
    """
    def __init__(self, option):
        self.name = ffi.string(
            lib.rxkb_option_get_name(option)).decode('ascii')
        self.brief = _string_or_none(
            lib.rxkb_option_get_brief(option))
        self.description = _string_or_none(
            lib.rxkb_option_get_description(option))
        self.popularity = Popularity(lib.rxkb_option_get_popularity(option))

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"rxkb.Option('{self.name}')"
