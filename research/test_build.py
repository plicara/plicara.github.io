"""Regression checks for the research article renderer."""

import importlib.util
from pathlib import Path
import unittest


BUILD_PATH = Path(__file__).with_name("build.py")
SPEC = importlib.util.spec_from_file_location("research_build", BUILD_PATH)
build = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(build)


class ArticleRenderingTest(unittest.TestCase):
    def test_trailing_whitespace_does_not_create_a_hard_break(self):
        body = build.strip_hard_breaks("First line  \nSecond line", "test.md")
        rendered = build.render_article(
            {"title": "Test", "date": "2026-09-04", "summary": "Test"},
            body,
            "test",
            False,
        )
        self.assertNotIn("<br", rendered)

    def test_fenced_code_preserves_trailing_whitespace(self):
        body = build.strip_hard_breaks("```text\nvalue  \n```", "test.md")
        self.assertEqual(body, "```text\nvalue  \n```")

    def test_article_uses_the_versioned_stylesheet(self):
        rendered = build.render_article(
            {"title": "Test", "date": "2026-09-04", "summary": "Test"},
            "Body",
            "test",
            False,
        )
        self.assertIn('href="/assets/style.css?v=20260904"', rendered)


if __name__ == "__main__":
    unittest.main()
