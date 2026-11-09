## DEC-003: Withdraw the two Jev articles and merge the Pi essay

- **Date:** 2026-11-09
- **Status:** decided
- **Context:** A review of the site found two Jev articles whose framing read like a vendor demo ("incredibly accurate", "breaking the benchmark"), one of them very long and heavily caveated, and an October review found the first's provenance footnote did not fully back its tone. The two Pi profiles essays were published the same day as parts 1 and 2 of one idea.
- **Decision:** Withdraw `research/jev-decisions` and `research/model-that-only-chooses`. Their URLs now carry a short noindex notice (see `WITHDRAWN` in `research/build.py`) pointing at the evidence in the `articles` repository; the articles are out of the index, feed and sitemap, and their sources and PDFs are removed. Merge the two Pi essays into one essay at `/essays/pi-profiles/` with Part 1 and Part 2 sections; `/essays/agents-plural/` redirects to `#part-2`.
- **Consequences:** The old PDF links for the two Jev articles and for `agents-plural` no longer resolve. The authoritative drafts in `articles-workbench` are unchanged and still hold the withdrawn text and the two separate Pi pieces. An article can be restored by returning its markdown source and removing its `WITHDRAWN` entry.
