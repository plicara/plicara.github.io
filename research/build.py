#!/usr/bin/env python3
"""Build the research and essays sections from markdown sources.

The site has no server-side build step by design (.nojekyll, plain HTML and
CSS), so this follows the house pattern set by assets/brand/waves.py: the
generator is checked in, its output is checked in, and the output is never
hand-edited. Drop a markdown file in research/articles/, run this, commit
what it writes.

    python3 research/build.py          # pages + index + sitemap + PDFs
    python3 research/build.py --no-pdf # skip PDF generation (no Chromium)

What it writes, per article research/articles/<name>.md:

    research/<slug>/index.html   the article page
    research/<slug>/<slug>.pdf   the article as a PDF, printed from the page
    research/index.html          the index, newest first
    research/feed.xml            RSS summaries of published articles
    sitemap.xml                  research and essays URLs replaced in place

Essays are built the same way from essays/articles/ into essays/. A section
is a small record in SECTIONS below; moving an article between sections is a
file move plus a redirect (see REDIRECTS).

Authoring-time dependencies (never shipped to readers):

    pip install markdown         # the only Python dependency
    Chromium                     # for PDFs; found via $CHROME or the
                                 # Playwright install, else PDFs are skipped
                                 # and article pages link to existing PDFs if available

Front matter is a block of `key: value` lines between two `---` lines at the
top of the file. See articles/_template.md for the keys and the conventions
(root-relative asset paths, whitepapers in research/papers/).

Files whose names start with `_` are ignored; `draft: true` builds nothing
and says so. Markdown is rendered with the `extra` extension set (tables,
fenced code, footnotes) and deliberately WITHOUT `smarty`: it would turn
`--` into em-dashes, and the site's copy carries none by decision.
"""

import argparse
import functools
import html
import http.server
import os
import re
import shutil
import subprocess
import sys
import threading
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("This generator needs the markdown package: pip install markdown")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = os.path.join(ROOT, "research")
ARTICLES = os.path.join(RESEARCH, "articles")
ESSAYS = os.path.join(ROOT, "essays")
ESSAY_ARTICLES = os.path.join(ESSAYS, "articles")
SITE = "https://plicara.ai"


def sections():
    """The two sections, read at call time so tests can point them elsewhere."""
    return [
        {
            "key": "research", "dir": RESEARCH, "articles": ARTICLES,
            "name": "Research", "feed_title": "plicara labs research",
            "feed_description": "Studies, tools and perspectives from Adrian Tame’s independent AI research lab.",
            "eyebrow": "research", "index_eyebrow": "research &middot; the notebook",
            "index_description": "Articles, analyses and whitepapers from plicara labs.",
            "lede": "Articles and analyses from the lab, with the whitepapers behind them. "
                    "Articles link to methods and evidence where available. "
                    "Each study states what can be reproduced and where records or checks are missing.",
            "back": "All research", "follow": "Follow new research via RSS",
        },
        {
            "key": "essays", "dir": ESSAYS, "articles": ESSAY_ARTICLES,
            "name": "Essays", "feed_title": "plicara labs essays",
            "feed_description": "Essays and arguments from Adrian Tame’s independent AI research lab.",
            "eyebrow": "essay", "index_eyebrow": "essays &middot; arguments and working notes",
            "index_description": "Essays from plicara labs: arguments, opinions and working notes that are not studies.",
            "lede": "Arguments, opinions and working notes from the lab. "
                    "Essays are written to make a case, not to report a study; "
                    "where one leans on evidence, it links to it, and the studies themselves live under Research.",
            "back": "All essays", "follow": "Follow new essays via RSS",
        },
    ]


# Old article URLs that moved between sections: slug -> section key it now lives in.
# The old path keeps working as a static redirect page (GitHub Pages has no
# server-side redirects). The stale PDF at the old path is left in place so
# existing links to it do not break.
REDIRECTS = {"harness-is-signal": "essays", "pi-audit-loop": "essays"}

REQUIRED = ("title", "date", "summary")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")


# --- front matter ------------------------------------------------------------

def parse_front_matter(text, name):
    """The `key: value` block between two --- lines at the top of the file."""
    if not text.startswith("---"):
        sys.exit(f"{name}: no front matter block (file must start with ---)")
    try:
        _, block, body = text.split("---", 2)
    except ValueError:
        sys.exit(f"{name}: front matter block never closes (need a second ---)")
    meta = {}
    for line in block.strip().splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            sys.exit(f"{name}: front matter line without a colon: {line!r}")
        key, value = line.split(":", 1)
        meta[key.strip().lower()] = value.strip()
    for key in REQUIRED:
        if not meta.get(key):
            sys.exit(f"{name}: front matter is missing {key!r}")
    if not DATE_RE.match(meta["date"]):
        sys.exit(f"{name}: date must be YYYY-MM-DD, got {meta['date']!r}")
    return meta, body.lstrip("\n")


def strip_hard_breaks(body_md, name):
    """Remove prose trailing whitespace without modifying fenced code."""
    lines, fence, stripped = [], None, 0
    for line in body_md.split("\n"):
        opener = FENCE_RE.match(line)
        if opener:
            token = opener.group(1)
            fence = token if fence is None else (None if token == fence else fence)
            lines.append(line)
            continue
        if fence is not None:
            lines.append(line)
            continue
        trimmed = line.rstrip()
        stripped += trimmed != line
        lines.append(trimmed)
    if stripped:
        print(f"  NOTE  {name}: stripped trailing whitespace from {stripped} line(s)")
    return "\n".join(lines)


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        sys.exit(f"cannot make a slug out of {value!r}")
    return slug


# --- page chrome -------------------------------------------------------------
# One copy of the header and footer for every generated page. The five
# hand-written pages carry their own copies (the accepted cost of a
# no-build-step site); everything under research/ comes from here instead,
# so at least the generated half cannot drift.

def chrome_head(title, description, canonical, feed_title="plicara research", feed_href="/research/feed.xml"):
    return f"""<!DOCTYPE html>
<!-- GENERATED by research/build.py. Do not hand-edit: change the markdown
     in research/articles/ or essays/articles/, or the templates in build.py, and re-run it. -->
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{html.escape(title)} &middot; plicara labs</title>
    <meta name="description" content="{html.escape(description)}" />
    <link rel="canonical" href="{canonical}" />
    <meta name="theme-color" content="#05192B" />

    <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
    <link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon-180.png" />

    <!-- Research reads in the warm typeset; the mono sets the nav, eyebrows
         and data. Same preload discipline as the rest of the site: hint
         exactly what renders above the fold. -->
    <link rel="preload" as="font" type="font/woff2"
          href="/assets/fonts/fraunces.woff2" crossorigin />
    <link rel="preload" as="font" type="font/woff2"
          href="/assets/fonts/newsreader.woff2" crossorigin />
    <link rel="preload" as="font" type="font/woff2"
          href="/assets/fonts/jetbrains-mono-400.woff2" crossorigin />
    <link rel="preload" as="font" type="font/woff2"
          href="/assets/fonts/jetbrains-mono-700.woff2" crossorigin />

    <link rel="stylesheet" href="/assets/tokens.css" />
    <link rel="alternate" type="application/rss+xml" title="{html.escape(feed_title)}" href="{feed_href}" />
    <link rel="stylesheet" href="/assets/style.css?v=20260929" />
  </head>
  <body>
    <a class="skip-link" href="#main">Skip to content</a>

    <header class="site-header">
      <div class="wrap">
        <a class="brand" href="/">
          <span class="brand-mark" aria-hidden="true"></span>
          plicara labs
        </a>
        <nav class="site-nav" aria-label="Primary">
          <a href="/research/">Research</a>
          <a href="/essays/">Essays</a>
          <a href="/tools/">Tools</a>
          <a href="/benchmarks/">Benchmarks</a>
          <a href="/about/">About</a>
          <a href="/#contact">Follow</a>
        </nav>
      </div>
    </header>
"""


CHROME_FOOT = """
    <footer class="site-footer">
      <div class="wrap">
        <span>&copy; plicara labs</span>
        <div class="footer-links">
          <a href="mailto:info@plicara.ai">info@plicara.ai</a>
          <a href="https://github.com/plicara">GitHub</a>
          <a href="/">Home</a>
        </div>
      </div>
    </footer>
  </body>
</html>
"""


# --- rendering ---------------------------------------------------------------

MD = markdown.Markdown(extensions=["extra"], output_format="html5")


def render_article(meta, body_md, slug, pdf_ok, sec=None):
    sec = sec or sections()[0]
    base = f"/{sec['key']}"
    MD.reset()
    body_html = MD.convert(body_md)
    body_html = body_html.replace("<table>", '<table tabindex="0">').replace("<pre>", '<pre tabindex="0">')
    author = meta.get("author", meta.get("authors", "plicara labs"))
    author_html = html.escape(author)
    if meta.get("author_url"):
        author_html = (f'<a class="article-author" href="{html.escape(meta["author_url"], quote=True)}">'
                       f'{author_html}</a>')
    publisher = meta.get("publisher")
    if publisher:
        author_html += f", writing for {html.escape(publisher)}"
    pdf_link = (
        f' &middot; <a class="article-pdf-link"'
        f' href="{base}/{slug}/{slug}.pdf">Download PDF</a>'
        if pdf_ok else ""
    )
    head = chrome_head(meta["title"], meta["summary"], f"{SITE}{base}/{slug}/",
                       sec["feed_title"], f"{base}/feed.xml")
    return f"""{head}
    <main id="main">
      <article class="wrap article">
        <header class="article-head">
          <p class="eyebrow">{sec["eyebrow"]} &middot; {meta["date"]}</p>
          <h1>{html.escape(meta["title"])}</h1>
          <p class="article-meta">
            {author_html} &middot;
            <time datetime="{meta["date"]}">{meta["date"]}</time>{pdf_link}
          </p>
        </header>

        <div class="article-body">
{body_html}
        </div>

        <p class="article-back"><a href="{base}/">&larr; {sec["back"]}</a> &middot; <a href="{base}/feed.xml">{sec["follow"]}</a></p>
      </article>
    </main>
{CHROME_FOOT}"""


def render_index(entries, pdf_ok, sec=None):
    sec = sec or sections()[0]
    base = f"/{sec['key']}"
    head = chrome_head(
        sec["name"],
        sec["index_description"],
        f"{SITE}{base}/",
        sec["feed_title"], f"{base}/feed.xml",
    )
    if entries:
        rows = []
        for meta, slug in entries:
            pdf = (
                f' &middot; <a class="mono" href="{base}/{slug}/{slug}.pdf">pdf</a>'
                if pdf_ok or os.path.isfile(os.path.join(sec["dir"], slug, f"{slug}.pdf")) else ""
            )
            rows.append(f"""        <li class="research-entry">
          <p class="research-date mono">{meta["date"]}</p>
          <div>
            <h2><a href="{base}/{slug}/">{html.escape(meta["title"])}</a></h2>
            <p>{html.escape(meta["summary"])}{pdf}</p>
          </div>
        </li>""")
        listing = ('      <ul class="research-list">\n'
                   + "\n".join(rows) + "\n      </ul>")
    else:
        listing = ('      <p class="section-intro">Nothing published yet; '
                   "the first pieces are being written.</p>")
    return f"""{head}
    <main class="wrap preflight" id="main">
      <p class="eyebrow">{sec["index_eyebrow"]}</p>
      <h1>{sec["name"]}</h1>
      <p class="lede">
        {sec["lede"]}
      </p>

{listing}
      <p class="note"><a href="{base}/feed.xml">{sec["follow"]}</a> &middot; <a href="https://x.com/plicaralabs">plicara on X</a></p>
    </main>
{CHROME_FOOT}"""


def render_redirect(slug, section_key, title):
    """A static stand-in at an article's old URL, pointing at its new home."""
    target = f"{SITE}/{section_key}/{slug}/"
    return f"""<!DOCTYPE html>
<!-- GENERATED by research/build.py. Do not hand-edit. -->
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{html.escape(title)} &middot; plicara labs</title>
    <meta http-equiv="refresh" content="0; url=/{section_key}/{slug}/" />
    <link rel="canonical" href="{target}" />
    <meta name="robots" content="noindex" />
  </head>
  <body>
    <p>This article has moved to <a href="/{section_key}/{slug}/">/{section_key}/{slug}/</a>.</p>
  </body>
</html>
"""


# --- RSS ---------------------------------------------------------------------

def render_feed(entries, sec=None):
    sec = sec or sections()[0]
    base = f"/{sec['key']}"
    """RSS summaries for the same published entries as the research index."""
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    for key, value in (("title", sec["feed_title"]),
                       ("link", f"{SITE}{base}/"),
                       ("description", sec["feed_description"]),
                       ("language", "en")):
        ET.SubElement(channel, key).text = value
    for meta, slug in entries:
        item = ET.SubElement(channel, "item")
        url = f"{SITE}{base}/{slug}/"
        for key, value in (("title", meta["title"]), ("link", url),
                           ("description", meta["summary"])):
            ET.SubElement(item, key).text = value
        ET.SubElement(item, "guid", isPermaLink="true").text = url
        date = datetime.strptime(meta["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        ET.SubElement(item, "pubDate").text = format_datetime(date, usegmt=True)
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(rss, encoding="unicode") + '\n'


# --- PDFs --------------------------------------------------------------------

def find_chromium():
    """$CHROME first, then the Playwright install, then the PATH."""
    for candidate in (os.environ.get("CHROME"), "/opt/pw-browsers/chromium",
                      shutil.which("chromium"), shutil.which("chromium-browser"),
                      shutil.which("google-chrome")):
        if candidate and os.path.exists(candidate):
            return candidate
    return None


def serve_site():
    """A throwaway HTTP server rooted at the repo, for printing.

    Printing from file:// would silently produce an unstyled PDF: the pages
    reference their stylesheets root-relatively (/assets/...), which resolves
    to the filesystem root under file:// and loads nothing. Serving the repo
    the way GitHub Pages does makes the printed page identical to the live
    one, self-hosted fonts included.
    """
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    handler = functools.partial(Quiet, directory=ROOT)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


def print_pdf(chromium, url, pdf_path):
    """Print the article page to PDF through the print stylesheet."""
    result = subprocess.run(
        [chromium, "--headless", "--disable-gpu", "--no-sandbox",
         "--no-pdf-header-footer", "--virtual-time-budget=4000",
         f"--print-to-pdf={pdf_path}", url],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0 or not os.path.exists(pdf_path):
        sys.exit(f"PDF generation failed for {url}:\n{result.stderr[-800:]}")


# --- sitemap -----------------------------------------------------------------

def update_sitemap(slugs_by_section):
    """Replace this site's section entries, leaving everything else alone.

    The match is anchored to the full site prefix: a bare "/research/"
    substring match would silently delete any future unrelated URL that
    happens to contain it (say, /blog/research-notes/methodology/).
    """
    path = os.path.join(ROOT, "sitemap.xml")
    text = Path(path).read_text(encoding="utf-8")
    urls = []
    for key, slugs in slugs_by_section:
        text = re.sub(
            rf"[ \t]*<url>\s*<loc>{re.escape(SITE)}/{key}/[^<]*</loc>.*?</url>\n",
            "", text, flags=re.S)
        urls += [f"{SITE}/{key}/"] + [f"{SITE}/{key}/{s}/" for s in slugs]
    block = "".join(
        f"  <url>\n    <loc>{u}</loc>\n    <changefreq>monthly</changefreq>\n"
        f"    <priority>0.6</priority>\n  </url>\n"
        for u in urls
    )
    text = text.replace("</urlset>", block + "</urlset>")
    Path(path).write_text(text, encoding="utf-8")


# --- main --------------------------------------------------------------------

def build_section(sec, pdf_ok, chromium, port):
    if not os.path.isdir(sec["articles"]):
        return []
    entries = []
    seen = []
    base = f"/{sec['key']}"
    for name in sorted(os.listdir(sec["articles"])):
        if not name.endswith(".md") or name.startswith("_"):
            continue
        path = os.path.join(sec["articles"], name)
        raw = Path(path).read_text(encoding="utf-8")
        meta, body_md = parse_front_matter(raw, name)
        body_md = strip_hard_breaks(body_md, name)
        # body_md is a suffix of raw, so the difference in newline counts is
        # exactly the lines front matter consumed. Reported line numbers have
        # to match the file, or "go fix line 4" points at the wrong line.
        first_line = raw.count("\n") - body_md.count("\n") + 1
        if meta.get("draft", "").lower() == "true":
            print(f"  skip  {name} (draft)")
            continue
        # An em-dash is on-brand in exactly one place: an empty table
        # cell, meaning "no comparable number" (brand.md's results-table
        # rule). Anywhere else it is prose, and the site's prose carries
        # none by decision.
        # Fenced code is exempt: inside a fence an em-dash is content, not
        # prose, and on a site that publishes regex articles it is exactly
        # the payload you must not rewrite. Same reasoning that keeps
        # strip_hard_breaks out of fences.
        stray, fence = [], None
        for n, ln in enumerate(body_md.splitlines(), first_line):
            opener = re.match(r"^\s{0,3}(```|~~~)", ln)
            if opener:
                token = opener.group(1)
                fence = token if fence is None else (None if token == fence else fence)
                continue
            if fence is not None:
                continue
            if "—" in "|".join(c for c in ln.split("|") if c.strip() != "—"):
                stray.append(n)
        if stray or "—" in str(meta):
            sys.exit(f"{name}: em-dash outside an empty table cell "
                     f"(line(s) {', '.join(map(str, stray)) or 'front matter'});"
                     " write around it")
        # The override goes through slugify too: it is the one field
        # that reaches a filesystem path and an href, so it is
        # normalized to [a-z0-9-] rather than trusted.
        slug = slugify(meta.get("slug") or name[:-3])
        taken = {s: n for n, s in seen}
        if slug in taken:
            sys.exit(f"{name}: slug {slug!r} is already used by"
                     f" {taken[slug]!r}; two articles cannot share a URL")
        seen.append((name, slug))
        out_dir = os.path.join(sec["dir"], slug)
        os.makedirs(out_dir, exist_ok=True)
        out_html = os.path.join(out_dir, "index.html")
        existing_pdf = os.path.isfile(os.path.join(out_dir, f"{slug}.pdf"))
        Path(out_html).write_text(render_article(meta, body_md, slug, pdf_ok or existing_pdf, sec), encoding="utf-8")
        if pdf_ok:
            print_pdf(chromium, f"http://127.0.0.1:{port}{base}/{slug}/",
                      os.path.join(out_dir, f"{slug}.pdf"))
        entries.append((meta, slug))
        print(f"  built {name} -> {sec['key']}/{slug}/"
              + (f" (+ {slug}.pdf)" if pdf_ok else ""))

    entries.sort(key=lambda e: e[0]["date"], reverse=True)
    Path(sec["dir"], "index.html").write_text(render_index(entries, pdf_ok, sec), encoding="utf-8")
    Path(sec["dir"], "feed.xml").write_text(render_feed(entries, sec), encoding="utf-8")
    print(f"  built {sec['key']}/index.html ({len(entries)} article(s))")
    return entries


def write_redirects(built):
    """Stand-in pages at old URLs for articles that moved sections."""
    for slug, key in REDIRECTS.items():
        entry = next((m for m, s in built.get(key, []) if s == slug), None)
        if entry is None:
            continue
        for sec in sections():
            old_dir = os.path.join(sec["dir"], slug)
            if sec["key"] == key or not os.path.isdir(old_dir):
                continue
            Path(old_dir, "index.html").write_text(
                render_redirect(slug, key, entry["title"]), encoding="utf-8")
            print(f"  redirect {sec['key']}/{slug}/ -> {key}/{slug}/")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-pdf", action="store_true",
                    help="skip PDF generation; preserve links to existing PDFs")
    args = ap.parse_args()

    chromium = None if args.no_pdf else find_chromium()
    if not args.no_pdf and not chromium:
        print("NOTE: no Chromium found ($CHROME unset, no Playwright install);"
              " building without new PDFs. Existing PDF links are preserved.")
    pdf_ok = chromium is not None
    server = port = None
    if pdf_ok:
        server, port = serve_site()

    built = {}
    for sec in sections():
        built[sec["key"]] = build_section(sec, pdf_ok, chromium, port)

    if server:
        server.shutdown()

    write_redirects(built)
    update_sitemap([(k, [slug for _, slug in e]) for k, e in built.items()])
    print("  refreshed sitemap.xml")

    # Stale output check: a slug directory with no matching source is most
    # likely a renamed or deleted article whose old page would keep serving.
    for sec in sections():
        live = {slug for _, slug in built[sec["key"]]}
        if not os.path.isdir(sec["dir"]):
            continue
        for name in sorted(os.listdir(sec["dir"])):
            full = os.path.join(sec["dir"], name)
            if os.path.isdir(full) and name not in ("articles", "papers") \
                    and name not in live and REDIRECTS.get(name) is None:
                print(f"  NOTE  {sec['key']}/{name}/ has no matching source article;"
                      " delete it if the article was renamed or removed")


if __name__ == "__main__":
    main()
