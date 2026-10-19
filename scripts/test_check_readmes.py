#!/usr/bin/env python3
"""Tests the banned-word check in check_readmes.py. Run: python3 -I scripts/test_check_readmes.py"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from check_readmes import banned  # noqa: E402


def hits(text):
    return banned(text.splitlines())


class Banned(unittest.TestCase):
    def test_filler_word_in_prose(self):
        self.assertEqual(hits("You just run it."), [(1, "just")])

    def test_each_listed_word(self):
        text = "It is simply fast.\nA powerful tool.\nA seamless install."
        self.assertEqual(hits(text), [(1, "simply"), (2, "powerful"), (3, "seamless")])

    def test_capital_at_sentence_start(self):
        self.assertEqual(hits("Just run it."), [(1, "Just")])

    def test_word_inside_another_word(self):
        self.assertEqual(hits("Adjust the cap. It is justified. Simplify it. Seamlessness."), [])

    def test_abbreviations(self):
        self.assertEqual(hits("A tool, e.g. a hook.\nThe mod, i.e. the hook."), [(1, "e.g."), (2, "i.e.")])

    def test_abbreviation_in_capitals_and_before_comma(self):
        self.assertEqual(hits("E.g., a hook."), [(1, "E.g.")])

    def test_letters_without_dots_are_not_abbreviations(self):
        self.assertEqual(hits("The eg flag and the ie folder."), [])

    def test_code_span(self):
        self.assertEqual(hits("The mod blocks `just fixed` and `e.g.`."), [])

    def test_unclosed_backtick_is_prose(self):
        self.assertEqual(hits("A ` sign, just one."), [(1, "just")])

    def test_fenced_block(self):
        self.assertEqual(hits("```\njust e.g.\n```\nText."), [])

    def test_indented_fence_in_a_list(self):
        self.assertEqual(hits("1. Run:\n   ```\n   just run\n   ```\n2. Done."), [])

    def test_line_after_fence_is_checked(self):
        self.assertEqual(hits("```\nx\n```\nJust that."), [(4, "Just")])

    def test_link_target(self):
        self.assertEqual(hits("See [the guide](https://example.com/just-simply)."), [])

    def test_link_text(self):
        self.assertEqual(hits("See [a powerful guide](guide.md)."), [(1, "powerful")])

    def test_table_cell_and_table_rule(self):
        self.assertEqual(hits("| A | B |\n|---|:--:|\n| x | just y |"), [(3, "just")])

    def test_heading(self):
        self.assertEqual(hits("## Just the start"), [(1, "Just")])

    def test_every_hit_on_one_line(self):
        self.assertEqual(hits("Just add it, e.g. simply."), [(1, "Just"), (1, "e.g."), (1, "simply")])

    def test_emoji(self):
        self.assertEqual(hits("Done \U0001F680 now."), [(1, "\U0001F680")])

    def test_symbols_that_are_not_emoji(self):
        self.assertEqual(hits("Mark it ✓ or ✗, then go → next."), [])

    def test_emoji_presentation_selector(self):
        self.assertEqual(hits("Warn ⚠️ here."), [(1, "⚠️")])


if __name__ == "__main__":
    unittest.main()
