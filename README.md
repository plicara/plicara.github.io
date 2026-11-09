# plicara.github.io

The plicara labs website — a hand-written static site, served by GitHub Pages at <https://plicara.github.io/>.

## Brand

The visual system is defined in [`plicara-brand`](https://github.com/plicara/plicara-brand), not here. The *rules* — naming, voice, usage, the decision log — stay in the lab's private notebook; the buildable half is public:

| | |
| --- | --- |
| Values and drawings | [`plicara-brand`](https://github.com/plicara/plicara-brand) |
| Logo files | [`logo/`](https://github.com/plicara/plicara-brand/tree/main/logo) |
| Rules | `docs/brand.md` in the private notebook |

**`assets/tokens.css`, `assets/tokens.json`, the favicon, the marks and the plane glyphs are copies, not sources.** They come from `plicara-brand`. `tools/vendor.py` holds the manifest and does the copying:

```sh
uv run --locked python tools/vendor.py --check    # fail if any copy has drifted
uv run --locked python tools/vendor.py --sync     # refresh the copies from upstream
```

Both take `--upstream PATH`, defaulting to `../plicara-brand`. To change a colour, a typeface or the mark, change it **there**, regenerate, then `--sync` here. The JSON carries the generated contrast matrix and fill guards, so the "generated rather than asserted" claim in the CSS header holds next to the copy too. `assets/style.css` holds only site-specific layout and components, and reads everything else from tokens.

Saying that was not enough on its own. The copies drifted twice: the site hand-edited `favicon.svg` and the small marks to restore the back range and never sent it upstream, so for three days the two repos disagreed about what the logo was; and the harbour repaint landed upstream while the site went on shipping the previous palette, because "vendor the new tokens" was a step someone had to remember. `.github/workflows/vendor-parity.yml` now runs `--check` on every push and pull request, so drift fails CI instead of shipping.

The guard's first version read the private notebook and needed a token secret that was never set, so it skipped every real step and reported success — inert from the day it landed. `plicara-brand` is public, so the job now needs no secret and has no skip path.

**One direction only.** `--sync` copies upstream → here and never the reverse. An edit to a vendored file in this repo is the thing that broke last time; `--check` will catch it and tell you to go upstream.

### One scheme: cut paper

Since 2026-11 every page uses **one scheme and one type system**, so the lab, the essays, the benchmarks and the tools read as one site. The old split (twilight/cel for the lab, a "technical" blueprint/notepad band with its own typeset for benchmarks and tools) is retired. No page sets `data-scheme`.

| | |
| --- | --- |
| **Daylight** (default) | Kraft ground, ink text, pine accent |
| **Lamplight** (`prefers-color-scheme: dark`) | Umber ground, cream text, orange accent |
| **Display** | Hedvig Letters Serif, lowercase |
| **Body, labels, UI** | Figtree; labels lowercase at weight 600 |
| **Figures and code** | JetBrains Mono |

Colour arrives as **flat paper blocks** with torn edges: `.torn` plus one of `.block-fired`, `.block-pine`, `.block-pink`, `.block-butter` (or `.block-empty`, a dashed outline for things that are not here yet). The block colour sits on a `::before` layer with the `#torn` displacement filter, so the text above it stays sharp. Each block takes its ink from the brand's `--pl-on-*` guard. Fired holds ink, never cream. Cards and the contact card are linen sheets torn the same way. Nothing moves on hover; titles underline.

**Every page carries the filter once**, as `<svg class="paper-defs">` right after `<body>`. `research/build.py` writes it into generated pages; hand-written pages carry it in their markup. A page without it shows square blocks, not broken ones.

A light paper grain sits over the whole page (`body::after`), multiplied by day and screened at a third of the strength under lamplight. Print drops it.

### Case

| | |
| --- | --- |
| **Display roles** (`h1`–`h3`, the brand lockup, data-table row headers) | Lowercase, `text-transform: lowercase` |
| **Labels** (nav, buttons, tags, eyebrows, column heads, footer) | Lowercase, Figtree 600 |
| **Body text and pull quotes** | Keep their capitals |

A quotation keeps its capitals even when set in the display face. `.mission-statement` does not inherit the heading rule. Package names such as `regexbench` are unchanged by the lowercase transform, which is one reason the labels moved off uppercase.

### Fonts

Self-hosted in `assets/fonts/`, no external requests. Hedvig Letters Serif and Figtree are preloaded because they render above the fold on every page; JetBrains Mono loads normally. Hedvig Letters Serif and Figtree are SIL OFL 1.1, JetBrains Mono is Apache-2.0.

### Illustration

The house mark and the paper-plane glyphs are the characters. The home page sets the mark large beside the title card and uses the planes on the tiles, beside the tools, and as icons for the principles. Where a glyph sits on the page ground it uses `<picture>` to swap in the `-dark` build under lamplight; on a coloured block it keeps the light build. `assets/brand/waves.py` is retained for reference but is no longer used by any page.


### The house mark

**The mark is shown in colour**, so it is a `background-image` rather than a masked shape: a mask can only take one colour, and the colour build carries rust, orange and teal facets under the line. That costs two builds, because the outline is sumi on light grounds and cream on dark ones and a single file cannot be both. `style.css` resolves `--pl-mark` and `--pl-mark-small` from the reader's light or dark preference, so markup just asks for the token. The home page hero uses `<picture>` for the same swap.

| Where | File |
| --- | --- |
| Hero, ~132 px | `mark-colour.svg` / `mark-colour-dark.svg` |
| Header, 30 px | `mark-colour-small.svg` / `mark-colour-small-dark.svg` — same drawing, heavier stroke |
| Favicon | `assets/favicon.svg` — the small build inside the rounded badge |
| Anything CSS must recolour | `mark.svg` — monoline, takes `currentColor` |

**Every build draws the same mountains**: three peaks in front, two behind. The small build differs from the hero in stroke weight alone, which is what keeps the line from thinning away at 30 px. Nothing is dropped from the drawing. An earlier small build cut the back range on the theory that it silted up below 40 px; it does not, and the site shipped two logos as a result, one in the header and favicon and another in the hero.

This is now the rule **upstream** too, rather than a local correction the site kept re-applying to vendored files. The brand repo retired its reduced cut on 2026-08-15 and its generator emits the full drawing at every size; print was measured before adopting, and the small cut's minimum moved 4.6 mm → 5.2 mm on typical coated offset. So these files now arrive correct from `--sync` and no longer need touching here.

If a size ever does need a reduced cut, cut it in *all* the places that size is used — header, favicon and touch icon together — or the mark stops being one mark again.

**Never inline the mark's path data into a page.** An earlier hero did, and the next rebrand swapped `mark.svg` underneath it: the header updated and the hero kept drawing the previous logo, because an inlined copy is a copy and not a reference.

### Model glyphs

`assets/brand/marks/` holds the four paper-plane glyphs, generated in `plicara-brand` and vendored here. They are applied as CSS masks so they take the scheme's accent colour:

```html
<span class="peak" style="--g: url(/assets/brand/marks/plane-delta-mono.svg); ..."></span>
```

The path **must be root-relative**. A `url()` inside a custom property resolves against the stylesheet that consumes it, not the document, so a relative path here resolves against `assets/` and 404s.

## Research

The homepage leads with selected research, then tools and benchmarks. Primary navigation points to Research, Essays, Tools, Benchmarks, About and Follow. Keep selected homepage links deliberate; the complete article list and RSS feed are generated.

The lab site stands on its own as the research record. `/models/` remains reachable for old links but is not promoted until there is a release. Editorial decisions are recorded in [docs/decision-log.md](docs/decision-log.md).


The one part of the site that is written in markdown. `research/articles/` holds the sources; `research/build.py` compiles them:

```sh
make setup                     # install the locked authoring environment
uv run --locked python research/build.py       # pages + PDFs + index + sitemap
```

Commit everything it writes. Each article becomes `/research/<slug>/` plus a PDF of the same page, printed through the print stylesheet (Chromium is found via `$CHROME` or the Playwright install; without one, pages retain links to PDFs already on disk). The index at `/research/` and the research entries in `sitemap.xml` and `research/feed.xml` are regenerated on every run, so neither is ever edited by hand — the generated pages all share one header/footer template inside `build.py`, unlike the five hand-written pages, which still carry copies.

Essays live in a second section built by the same script: sources in `essays/articles/`, output at `/essays/<slug>/`, with its own index and `essays/feed.xml`. Research holds studies and analyses that report evidence; essays hold arguments and working notes. To move an article between sections, move its markdown file, add its slug to `REDIRECTS` in `research/build.py` so the old URL becomes a redirect page, and rebuild. The old PDF stays at its original path so existing links keep working.

`research/articles/_template.md` documents the front matter and the two conventions that matter: asset paths are root-relative, and whitepaper PDFs are hand-dropped into `research/papers/` and linked from the article body.

`uv run --locked python research/build.py --no-pdf` updates the HTML and RSS feed while preserving links to existing PDFs. It does not regenerate those PDFs. The feed uses published article summaries and stable article URLs; drafts stay excluded by the same build loop as the index.

To take an article down, delete its markdown source and PDF and add it to `WITHDRAWN` in `research/build.py`. Its URL then serves a short noindex notice instead of a 404, and it leaves the index, feed and sitemap. To fold one article into another, add a `REDIRECTS` entry of the form `(section, new_slug, fragment)`.

Run `uv run --locked python -m unittest discover -s research` after rebuilding. Run `make setup` and `make setup-browser`, serve the site on port 4001, and run `uv run --locked python tools/check_browser.py` for mobile/desktop layout and keyboard-scrolling checks. Pull requests run both checks and reject uncommitted generated-page changes. When article wording changes, regenerate its downloadable PDF as well. Archived whitepapers under `research/papers/` remain versioned historical artifacts; an article that revises their interpretation should say so explicitly.

## How this repo gets online

This repo is an **organization Pages site**, which is a special case in GitHub Pages:

- The repo name must be exactly `<org>.github.io`. It is.
- Because the name matches, GitHub enables Pages automatically on the first push to the **default branch** (`main`) and serves the **repository root**. There is normally no setting to flip.
- The site is served at the org root, `https://plicara.github.io/` — not under a `/repo-name/` path the way project sites are.

So the deploy story is: **merge to `main`, wait a minute, reload.** Pushing to any other branch changes nothing that's live.

If the site ever doesn't appear, check **Settings → Pages** and confirm the source is `Deploy from a branch` → `main` → `/ (root)`.

### No Jekyll

The `.nojekyll` file at the root tells Pages to publish the files verbatim instead of running them through Jekyll. That means no Gemfile, no build step, and nothing that can fail at deploy time — but it also means no Jekyll templating, includes, or `_layouts`. Plain HTML and CSS only.

If the site later outgrows hand-written HTML, the two options are to delete `.nojekyll` and adopt Jekyll, or to add a GitHub Actions workflow that builds whatever generator you prefer and publishes with `actions/deploy-pages`. That second path also requires switching **Settings → Pages → Source** to `GitHub Actions`.

## Layout

```
index.html        Landing page
models/           Existing URL retained as a short research-direction note
tools/            /tools/ — install examples and documentation for released tools
  vendor.py       Refreshes the vendored brand files from plicara-brand
benchmarks/       /benchmarks/ — index of published runs, one subpage per run
                  (mirrors /research/; regexeval-2026 is the first)
research/         /research/ — articles and analyses, generated from markdown
essays/          /essays/ — essays, generated from markdown by research/build.py
404.html          Custom not-found page (Pages serves this automatically)
assets/
  style.css       All styling; light and dark via prefers-color-scheme
  tokens.css      Palette, schemes and typesets — vendored, never edited here
  favicon.svg     Site icon
robots.txt        Crawler policy, points at the sitemap
sitemap.xml       Sitemap: the landing page, the section pages, the articles
.nojekyll         Publish files as-is, skip the Jekyll build
```

Everything is self-contained: no CDNs, no external fonts, no JavaScript.

### Source conventions

**One line per paragraph, in markdown and in HTML alike. Do not hard-wrap prose.** A `<p>` or a markdown paragraph is one source line, however long; the newlines a hard wrap adds are collapsed to spaces before anyone sees them, so all they do is rewrap on every edit and turn a one-word change into a diff of the whole block. `research/build.py` emits pages this way, and the hand-written pages match it so the two are read the same way. Structure still gets its own lines: table rows, list items, code fences, and every tag that opens a block.

## Working on it locally

There's no build step, so opening `index.html` in a browser mostly works. Absolute paths (`/assets/...` in `404.html`) only resolve over HTTP, so prefer:

```sh
make serve
# then visit http://localhost:8000
```

## Custom domain

The site is served at **`plicara.ai`**, declared by the `CNAME` file at the repo root. DNS is managed at Cloudflare. `github.io` redirects to it.

### DNS records

All records are **DNS only (grey cloud)** — see the warning below.

| Type | Name | Value |
| --- | --- | --- |
| `CNAME` | `@` | `plicara.github.io` |
| `CNAME` | `www` | `plicara.github.io` |
| `TXT` | `_github-pages-challenge-plicara` | (token from the org's Pages settings) |

Cloudflare flattens the apex `CNAME` to A records automatically, so there is no need to hard-code GitHub's four Pages IPs — and the record keeps working if those IPs ever change. If you ever do need them literally: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`, plus `2606:50c0:8000::153` through `:8003::153` for AAAA.

### The Cloudflare trap

> **Keep the cloud grey.** Cloudflare proxies new records by default (orange cloud). While a record is proxied, GitHub cannot see the DNS it needs to issue the Let's Encrypt certificate, so **Enforce HTTPS** stays greyed out with "your domain is not properly configured to support HTTPS" — and once issued, a proxied record breaks the automatic 90-day renewal too.

Leaving it grey is the recommendation, not just a setup step. GitHub Pages already fronts the site with a CDN and its own TLS, so proxying buys little and adds a recurring renewal failure.

If you ever do enable the orange cloud, set **SSL/TLS → Full (strict)** first. `Flexible` makes Cloudflare talk HTTP to GitHub, which already redirects to HTTPS, and the result is an infinite redirect loop.

### Order of operations

The `CNAME` file makes GitHub redirect `plicara.github.io` to the custom domain. Commit it **before** DNS resolves and both addresses are dark — the redirect target does not answer. So:

1. Add the DNS records at Cloudflare, grey cloud.
2. Confirm they resolve: `dig +short plicara.ai`.
3. Merge the `CNAME` file to `main`.
4. **Settings → Pages** shows the domain with a DNS check. Wait for the certificate, then tick **Enforce HTTPS**.

### Verify the domain

Org **Settings → Pages → Verified domains** gives a TXT record to add. Worth doing: an unverified domain can be claimed by another GitHub account if the `CNAME` is ever removed while the DNS still points at GitHub.

## License

Code is Apache-2.0; see [LICENSE](LICENSE).
Article text, figures and the Plicara marks are not covered by that licence; all rights reserved.

## Working in this repository

Project metadata and research context live in [.plicara/README.md](.plicara/README.md); agent constraints live in [AGENTS.md](AGENTS.md). Use `make setup` and `make check` for the default local environment and verification. Expensive experiments, model downloads, and publication are separate explicit steps. Project status is authoritative in `.plicara/project.yaml`; no central board update is required.
