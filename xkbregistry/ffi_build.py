from cffi import FFI
ffibuilder = FFI()

# Currently implemented with reference to libxkbcommon-1.0

ffibuilder.set_source("xkbregistry._ffi", """
#include <stdarg.h>
#include <xkbcommon/xkbregistry.h>

static void _log_handler(void *user_data,
                         enum rxkb_log_level level,
                         const char *message);

static void _log_handler_internal(
    struct rxkb_context *context,
    enum rxkb_log_level level,
    const char *format,
    va_list args)
{
  char buf[1024];
  void *user_data;

  user_data=rxkb_context_get_user_data(context);
  vsnprintf(buf, 1024, format, args);
  buf[1023]=0;
  _log_handler(user_data, level, buf);
}

void _set_log_handler_internal(struct rxkb_context *context)
{
  rxkb_context_set_log_fn(context, _log_handler_internal);
}

""",
                      libraries=['xkbregistry'])

ffibuilder.cdef("""
typedef ... FILE;
typedef ... va_list;

struct rxkb_context;
struct rxkb_model;
struct rxkb_layout;
struct rxkb_option_group;
struct rxkb_option;
struct rxkb_iso639_code;
struct rxkb_iso3166_code;

enum rxkb_popularity {
    RXKB_POPULARITY_STANDARD = ...,
    RXKB_POPULARITY_EXOTIC = ...
};

enum rxkb_context_flags {
  RXKB_CONTEXT_NO_FLAGS = ...,
  RXKB_CONTEXT_NO_DEFAULT_INCLUDES = ...,
  RXKB_CONTEXT_LOAD_EXOTIC_RULES = ...,
};

enum rxkb_log_level {
  RXKB_LOG_LEVEL_CRITICAL = ...,
  RXKB_LOG_LEVEL_ERROR = ...,
  RXKB_LOG_LEVEL_WARNING = ...,
  RXKB_LOG_LEVEL_INFO = ...,
  RXKB_LOG_LEVEL_DEBUG = ...
};

struct rxkb_context *
rxkb_context_new(enum rxkb_context_flags flags);

void
rxkb_context_set_log_level(struct rxkb_context *ctx,
                           enum rxkb_log_level level);

enum rxkb_log_level
rxkb_context_get_log_level(struct rxkb_context *ctx);

void
rxkb_context_set_log_fn(struct rxkb_context *ctx,
                         void(*log_fn)(struct rxkb_context *ctx,
                                       enum rxkb_log_level level,
                                       const char *format, va_list args));

bool
rxkb_context_parse(struct rxkb_context *ctx, const char *ruleset);

bool
rxkb_context_parse_default_ruleset(struct rxkb_context *ctx);

struct rxkb_context *
rxkb_context_ref(struct rxkb_context *ctx);

struct rxkb_context *
rxkb_context_unref(struct rxkb_context *ctx);

void
rxkb_context_set_user_data(struct rxkb_context *ctx, void *user_data);

void *
rxkb_context_get_user_data(struct rxkb_context *ctx);

bool
rxkb_context_include_path_append(struct rxkb_context *ctx, const char *path);

bool
rxkb_context_include_path_append_default(struct rxkb_context *ctx);

struct rxkb_model *
rxkb_model_first(struct rxkb_context *ctx);

struct rxkb_model *
rxkb_model_next(struct rxkb_model *m);

struct rxkb_model *
rxkb_model_ref(struct rxkb_model *m);

struct rxkb_model *
rxkb_model_unref(struct rxkb_model *m);

const char *
rxkb_model_get_name(struct rxkb_model *m);

const char *
rxkb_model_get_description(struct rxkb_model *m);

const char *
rxkb_model_get_vendor(struct rxkb_model *m);

enum rxkb_popularity
rxkb_model_get_popularity(struct rxkb_model *m);

struct rxkb_layout *
rxkb_layout_first(struct rxkb_context *ctx);

struct rxkb_layout *
rxkb_layout_next(struct rxkb_layout *l);

struct rxkb_layout *
rxkb_layout_ref(struct rxkb_layout *l);

struct rxkb_layout *
rxkb_layout_unref(struct rxkb_layout *l);

const char *
rxkb_layout_get_name(struct rxkb_layout *l);

const char *
rxkb_layout_get_variant(struct rxkb_layout *l);

const char *
rxkb_layout_get_brief(struct rxkb_layout *l);

const char *
rxkb_layout_get_description(struct rxkb_layout *l);

enum rxkb_popularity
rxkb_layout_get_popularity(struct rxkb_layout *l);

struct rxkb_option_group *
rxkb_option_group_first(struct rxkb_context *ctx);

struct rxkb_option_group *
rxkb_option_group_next(struct rxkb_option_group *g);

struct rxkb_option_group *
rxkb_option_group_ref(struct rxkb_option_group *g);

struct rxkb_option_group *
rxkb_option_group_unref(struct rxkb_option_group *g);

const char *
rxkb_option_group_get_name(struct rxkb_option_group *m);

const char *
rxkb_option_group_get_description(struct rxkb_option_group *m);

bool
rxkb_option_group_allows_multiple(struct rxkb_option_group *g);

enum rxkb_popularity
rxkb_option_group_get_popularity(struct rxkb_option_group *g);

struct rxkb_option *
rxkb_option_first(struct rxkb_option_group *group);

struct rxkb_option *
rxkb_option_next(struct rxkb_option *o);

struct rxkb_option *
rxkb_option_ref(struct rxkb_option *o);

struct rxkb_option *
rxkb_option_unref(struct rxkb_option *o);

const char *
rxkb_option_get_name(struct rxkb_option *o);

const char *
rxkb_option_get_brief(struct rxkb_option *o);

const char *
rxkb_option_get_description(struct rxkb_option *o);

enum rxkb_popularity
rxkb_option_get_popularity(struct rxkb_option *o);

struct rxkb_iso639_code *
rxkb_iso639_code_ref(struct rxkb_iso639_code *iso639);

struct rxkb_iso639_code *
rxkb_iso639_code_unref(struct rxkb_iso639_code *iso639);

const char *
rxkb_iso639_code_get_code(struct rxkb_iso639_code *iso639);

struct rxkb_iso639_code *
rxkb_layout_get_iso639_first(struct rxkb_layout *layout);

struct rxkb_iso639_code *
rxkb_iso639_code_next(struct rxkb_iso639_code *iso639);

struct rxkb_iso3166_code *
rxkb_iso3166_code_ref(struct rxkb_iso3166_code *iso3166);

struct rxkb_iso3166_code *
rxkb_iso3166_code_unref(struct rxkb_iso3166_code *iso3166);

const char *
rxkb_iso3166_code_get_code(struct rxkb_iso3166_code *iso3166);

struct rxkb_iso3166_code *
rxkb_layout_get_iso3166_first(struct rxkb_layout *layout);

struct rxkb_iso3166_code *
rxkb_iso3166_code_next(struct rxkb_iso3166_code *iso3166);

void _set_log_handler_internal(struct rxkb_context *context);

extern "Python" void _log_handler(void *user_data,
                                  enum rxkb_log_level level,
                                  const char *message);

void free(void *ptr);

""")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
