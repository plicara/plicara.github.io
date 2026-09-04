---
# Copy this file to <anything>.md in this folder and fill it in; files whose
# names start with _ are never built. Then, from the repo root:
#
#     python3 research/build.py
#
# and commit everything it writes (the article page, its PDF, the research
# index, and the sitemap). Nothing under research/<slug>/ is hand-edited.
#
# Required keys:
title: A short, specific title
date: 2026-01-01
summary: One or two sentences for the index page and search results.
# Optional keys:
#   author: Adrian Tame           (defaults to "Plicara Labs")
#   author_url: https://github.com/AdrianTJ
#   publisher: Plicara Labs       (renders as "writing for ...")
#   authors: Adrian Tame          (legacy alias for author)
#   slug: custom-url-name         (defaults to the file name)
#   draft: true                   (build nothing until it is removed)
---

Write standard markdown here. Tables, fenced code blocks and footnotes work (the `extra` extension set); raw HTML passes through if you need it. One renderer quirk worth knowing: nested list items need a four-space indent, not two, or they flatten into the parent list.

Three conventions, all load-bearing:

1. **One line per paragraph. Do not hard-wrap.** Markdown collapses those newlines to spaces, so a reader never sees them, but they make every later edit rewrap a whole block, and they turn a one-word change into a diff of the entire paragraph. Let the editor soft-wrap.
2. **Asset paths are root-relative.** Link whitepapers and images as `/research/papers/your-paper.pdf` or `/assets/...`, never relatively. The article page lives at `/research/<slug>/`, so a relative path would resolve somewhere you do not expect.
3. **Whitepaper PDFs go in `research/papers/`**, committed like any other file, and linked from the article body. The article's own PDF is generated for you; the whitepapers are yours to drop in.
