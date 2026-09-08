"""Regression checks for the research article renderer."""

import importlib.util
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch


BUILD_PATH = Path(__file__).with_name("build.py")
SPEC = importlib.util.spec_from_file_location("research_build", BUILD_PATH)
build = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(build)


class ArticleRenderingTest(unittest.TestCase):
    def test_build_excludes_drafts_from_feed_and_index(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            research = root / "research"
            articles = research / "articles"
            articles.mkdir(parents=True)
            (root / "sitemap.xml").write_text('<urlset>\n</urlset>')
            for name, draft in (("published", "false"), ("private-draft", "true")):
                (articles / f"{name}.md").write_text(
                    f"---\ntitle: {name}\ndate: 2026-09-08\nsummary: Example\ndraft: {draft}\n---\nBody"
                )
            with patch.multiple(build, ROOT=str(root), RESEARCH=str(research), ARTICLES=str(articles)), \
                    patch.object(build.sys, "argv", ["build.py", "--no-pdf"]), \
                    contextlib.redirect_stdout(io.StringIO()):
                build.main()
            titles = [item.findtext("title") for item in ET.parse(research / "feed.xml").findall("channel/item")]
            self.assertEqual(titles, ["published"])
            self.assertNotIn("private-draft", (research / "index.html").read_text())
            self.assertFalse((research / "private-draft").exists())

    def test_feed_preserves_text_and_uses_stable_urls_and_dates(self):
        meta = {"title": "Tools & <limits>", "date": "2026-09-08", "summary": "A < B & C"}
        item = ET.fromstring(build.render_feed([(meta, "limits")])).find("channel/item")
        self.assertEqual(item.findtext("title"), meta["title"])
        self.assertEqual(item.findtext("description"), meta["summary"])
        self.assertEqual(item.findtext("guid"), "https://plicara.ai/research/limits/")
        self.assertEqual(item.findtext("pubDate"), "Tue, 08 Sep 2026 00:00:00 GMT")

    def test_index_keeps_existing_pdf_without_generating_one(self):
        entry = ({"title": "Test", "date": "2026-09-08", "summary": "Test"}, "test")
        with patch.object(build.os.path, "isfile", return_value=True):
            self.assertIn('href="/research/test/test.pdf"', build.render_index([entry], False))
        with patch.object(build.os.path, "isfile", return_value=False):
            self.assertNotIn('href="/research/test/test.pdf"', build.render_index([entry], False))

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
