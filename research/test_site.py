"""Checks for the public navigation and research-claim boundaries."""

from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Navigation(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.in_nav = False
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "nav":
            self.in_nav = True
        if self.in_nav and tag == "a":
            self.links.append(attrs.get("href"))

    def handle_endtag(self, tag):
        if tag == "nav":
            self.in_nav = False


class PublicSiteTest(unittest.TestCase):
    def test_primary_navigation_does_not_promote_unreleased_models(self):
        for path in ROOT.rglob("*.html"):
            with self.subTest(page=str(path.relative_to(ROOT))):
                self.assertNotIn("/models/", Navigation(path.read_text()).links)
        self.assertTrue((ROOT / "models/index.html").exists())

    def test_regex_article_states_inference_limits(self):
        article = (ROOT / "research/articles/whether-anyone-ever-ran-it.md").read_text()
        self.assertIn("observational comparison", article)
        self.assertIn("does not establish equivalence", article)
        self.assertNotIn("the two are indistinguishable", article)
        self.assertNotIn("the variable is execution, not authorship", article)


if __name__ == "__main__":
    unittest.main()
