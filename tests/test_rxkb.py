# NB these tests are intended to check whether the python bindings are
# working, not whether libxkbregistry itself is working!

# We assume that the xkb-data package is installed

from unittest import TestCase

from xkbregistry import rxkb

import os

# A directory that is guaranteed to exist — the one containing this file
testdir = os.path.dirname(os.path.abspath(__file__))
# A path that is guaranteed not to exist
nonexistent = os.path.join(testdir, "must-not-exist")
# A file that is guaranteed to exist
testfile = os.path.abspath(__file__)


class TestContext(TestCase):
    def test_create(self):
        self.assertIsInstance(rxkb.Context(), rxkb.Context)
        self.assertIsInstance(rxkb.Context(no_default_includes=True),
                              rxkb.Context)
        self.assertIsInstance(rxkb.Context(load_exotic_rules=True),
                              rxkb.Context)

    def test_include_path_append(self):
        ctx = rxkb.Context(no_default_includes=True)
        self.assertIsNone(ctx.include_path_append(testdir))
        with self.assertRaises(rxkb.RXKBPathError):
            ctx.include_path_append(nonexistent)
        with self.assertRaises(rxkb.RXKBPathError):
            ctx.include_path_append(testfile)

    def test_include_path_append_default(self):
        ctx = rxkb.Context(no_default_includes=True)
        self.assertIsNone(ctx.include_path_append_default())
        # I can't figure out a way to get the library call to fail to
        # test the failure case!

    def test_parse(self):
        ctx = rxkb.Context()
        ctx.parse("base")
        with self.assertRaises(rxkb.RXKBAlreadyParsed):
            ctx.parse("base")

    def test_parse_default_ruleset(self):
        ctx = rxkb.Context()
        ctx.parse_default_ruleset()
        with self.assertRaises(rxkb.RXKBAlreadyParsed):
            ctx.parse_default_ruleset()

    def test_set_log_level(self):
        ctx = rxkb.Context()
        self.assertEqual(ctx.get_log_level(), rxkb.lib.RXKB_LOG_LEVEL_ERROR)
        ctx.set_log_level(rxkb.lib.RXKB_LOG_LEVEL_DEBUG)
        self.assertEqual(ctx.get_log_level(), rxkb.lib.RXKB_LOG_LEVEL_DEBUG)

    def test_set_log_handler(self):
        messages = []

        def handler(context, level, message):
            messages.append(message)

        ctx = rxkb.Context()
        ctx.set_log_level(rxkb.lib.RXKB_LOG_LEVEL_DEBUG)
        ctx.set_log_fn(handler)
        ctx.parse_default_ruleset()
        self.assertNotEqual(len(messages), 0)

    def test_models(self):
        ctx = rxkb.Context(no_default_includes=True)
        ctx.include_path_append(testdir)
        ctx.parse("test-base")
        self.assertIn("pc102", ctx.models)
        self.assertEqual(ctx.models["pc102"].description,
                         "Generic 102-key PC")
        self.assertEqual(ctx.models["pc102"].vendor, "Generic")
        self.assertEqual(ctx.models["pc102"].popularity,
                         rxkb.Popularity.RXKB_POPULARITY_STANDARD)

    def test_layouts(self):
        ctx = rxkb.Context(no_default_includes=True)
        ctx.include_path_append(testdir)
        ctx.parse("test-base")
        self.assertIn("us", ctx.layouts)
        x = ctx.layouts["us"]
        self.assertIsNone(x.variant)
        self.assertEqual(x.fullname, "us")
        self.assertEqual(x.brief, "en")
        self.assertEqual(x.description, "English (US)")
        self.assertSetEqual(x.iso639_codes, {"eng"})
        self.assertEqual(x.popularity,
                         rxkb.Popularity.RXKB_POPULARITY_STANDARD)
        self.assertIn("nec_vndr/jp", ctx.layouts)
        self.assertEqual(ctx.layouts["nec_vndr/jp"].iso3166_codes, {"JP"})

    def test_layout_variant(self):
        ctx = rxkb.Context(no_default_includes=True)
        ctx.include_path_append(testdir)
        ctx.parse("test-base")
        self.assertIn("us(chr)", ctx.layouts)
        x = ctx.layouts["us(chr)"]
        self.assertEqual(x.fullname, "us(chr)")
        self.assertEqual(x.variant, "chr")
        self.assertEqual(x.brief, "chr")
        self.assertEqual(x.description, "Cherokee")
        self.assertSetEqual(x.iso639_codes, {"chr"})

    def test_groups(self):
        ctx = rxkb.Context(no_default_includes=True)
        ctx.include_path_append(testdir)
        ctx.parse("test-base")
        # Groups are not required to have names. We are looking for
        # the group called "lv2", because it is short!
        for group in ctx.option_groups:
            if group.name == "lv2":
                self.assertEqual(
                    group.description, "Key to choose the 2nd level")
                self.assertEqual(group.popularity,
                                 rxkb.Popularity.RXKB_POPULARITY_STANDARD)
                self.assertIn("lv2:lsgt_switch", group.options)
                x = group.options["lv2:lsgt_switch"]
                self.assertEqual(x.description, 'The "< >" key')
                self.assertEqual(x.popularity,
                                 rxkb.Popularity.RXKB_POPULARITY_STANDARD)
                break
        else:
            self.fail(msg="lv2 option group not found")
