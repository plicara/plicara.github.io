# plicara.github.io

The Plicara Labs website — a hand-written static site, served by GitHub Pages at <https://plicara.github.io/>.

## Brand

The visual system is defined in [`plicara-brand`](https://github.com/plicara/plicara-brand), not here. The *rules* — naming, voice, usage, the decision log — stay in the lab's private notebook; the buildable half is public:

| | |
| --- | --- |
| Values and drawings | [`plicara-brand`](https://github.com/plicara/plicara-brand) |
| Logo files | [`logo/`](https://github.com/plicara/plicara-brand/tree/main/logo) |
| Rules | `docs/brand.md` in the private notebook |

**`assets/tokens.css`, `assets/tokens.json`, the favicon, the marks and the plane glyphs are copies, not sources.** They come from `plicara-brand`. `tools/vendor.py` holds the manifest and does the copying:

```sh
python3 tools/vendor.py --check    # fail if any copy has drifted
python3 tools/vendor.py --sync     # refresh the copies from upstream
```

Both take `--upstream PATH`, defaulting to `../plicara-brand`. To change a colour, a typeface or the mark, change it **there**, regenerate, then `--sync` here. The JSON carries the generated contrast matrix and fill guards, so the "generated rather than asserted" claim in the CSS header holds next to the copy too. `assets/style.css` holds only site-specific layout and components, and reads everything else from tokens.

Saying that was not enough on its own. The copies drifted twice: the site hand-edited `favicon.svg` and the small marks to restore the back range and never sent it upstream, so for three days the two repos disagreed about what the logo was; and the harbour repaint landed upstream while the site went on shipping the previous palette, because "vendor the new tokens" was a step someone had to remember. `.github/workflows/vendor-parity.yml` now runs `--check` on every push and pull request, so drift fails CI instead of shipping.

The guard's first version read the private notebook and needed a token secret that was never set, so it skipped every real step and reported success — inert from the day it landed. `plicara-brand` is public, so the job now needs no secret and has no skip path.

**One direction only.** `--sync` copies upstream → here and never the reverse. An edit to a vendored file in this repo is the thing that broke last time; `--check` will catch it and tell you to go upstream.

### Schemes on this site

Four schemes, paired by area of the lab, so a reader can tell which half they are in before reading a word:

| Scheme | Where |
| --- | --- |
| **Twilight** (dark) / **Cel** (light) | Default — the hero, mission, models, principles, contact, and `/models/`. Warm typeset: Fraunces + Newsreader. |
| **Blueprint** (dark) / **Notepad** (light) | Benchmarks and tools — the band holding `#tools`, `/tools/`, and `/benchmarks/*`. Applied as `data-scheme="technical"`, which resolves Blueprint at night and Notepad by day, so neither area pins a mode on the reader. Typeset: Archivo. |

**`data-scheme` goes on `<body>`, not `<html>`, on the pages that set one.** `tokens.css` declares its default `:root` block *after* the scheme blocks, so a scheme on the root element loses the custom-property tie-break and the page renders Twilight regardless. Moving that default above the scheme blocks upstream would remove the constraint.

Apply with `data-scheme` on any element. Schemes nest and paint their own ground, so a results table can sit inside a lab page in its own scheme.

**A scheme that paints a ground must be full-bleed and must sit in `.wrap`.** Use `.band`, which does both. An inset rectangle with text flush to its edge reads as a mistake rather than a register change — the ground has to run to the edge of the viewport and the content has to keep the same measure as everything above it.

### Seams

Where two schemes meet, the ground changes along a **squiggle**: the incoming scheme's ground is filled to a smooth wave edge, the edge itself is inked, and one lower-opacity echo rides above it. Entering the band (`.seam-down`), the tools' paper ground rises into the lab's sky inked in the band's own accent (`--pl-band-ink`); leaving it (`.seam-up`), the lab's own ground rises back inked in the page's accent (`--pl-accent`), so no line ever sits on its own colour. Both are tokens rather than literals, so the seam follows the band's light/dark switch instead of needing a retune whenever the palette is repainted.

The register is the one Material 3 uses for its wavy dividers and progress tracks: one wavelength held across the whole drawing, generous amplitude, round caps. It replaces two earlier attempts — terrain contours, then origami pleats — both of which read as noise at page width.

The seam's ground path carries `fill="currentColor"` as a presentation attribute as well as its class. That is deliberate: if this stylesheet is ever served stale against newer markup, the fill degrades to the inherited text colour instead of SVG's black default. An earlier pleated seam had no such guard, and a cached stylesheet rendered it as solid black sawteeth.

### Case

The display rule changed in 2026-08 and `style.css` now follows it:

| | |
| --- | --- |
| **Display roles** (`h1`–`h3`, the brand lockup, data-table row headers) | **Lowercase** — `text-transform: lowercase`, so it is a property of the role rather than a thing to remember per heading |
| **Mono labels** (nav, buttons, tags, pills, column heads) | Uppercase, `0.2em` tracking |
| **Eyebrows** | Lowercase mono — `01. the mission`, not `01. THE MISSION` |
| **Body text and pull quotes** | Keep their capitals |

That last row is the one that is easy to get wrong. `brand.md` is explicit that **a quotation keeps its capitals even when set in the display face**, because a pull quote is body voice printed large rather than a display role. The mission statement on the home page is styled by `.mission-statement`, which deliberately does *not* inherit the `h1`–`h3` lowercase rule.

Uppercase still marks a label as a label, and it would still wreck the package names — `regexbench` and `labloop` are identifiers, and `REGEXBENCH` is a different string — which is why the mono label role never contains one.

### Fonts

Self-hosted in `assets/fonts/`, no external requests. Fraunces and Newsreader are preloaded because they render the hero; Archivo and JetBrains Mono load normally. All four are open licence — Fraunces, Newsreader and Archivo are SIL OFL 1.1, JetBrains Mono is Apache-2.0.

### Illustration

Line not fill, and drawn in the same language as the mark. The hero band is a **wave field**: one wavelength, one gap, one amplitude law, and a constant phase step from line to line, so the set nests and no two lines can ever cross. Tidiness is enforced by construction rather than by taste.

The bands are **generated, not hand-drawn**, following the same rule as the marks in `plicara-brand`: change `assets/brand/waves.py` and re-run it, never the path data.

```sh
python3 assets/brand/waves.py   # paste the output into index.html
```

Curves are exact cubic-Bezier sine arches, one per half wavelength: for an arch of amplitude `A` over a half period `L/2`, control points at `L/6` and `L/3` at height `4A/3` put the curve's midpoint at exactly `A`. That is the closest a single cubic gets to a sinusoid, and it keeps the whole file near 5 KB.

They have to be inline SVG rather than `<img>`, because they read `currentColor` and the scheme custom properties.

### The house mark

**The mark is shown in colour**, so it is a `background-image` rather than a masked shape: a mask can only take one colour, and the colour build carries rust, orange and teal facets under the line. That costs two builds, because the outline is sumi on light grounds and cream on dark ones and a single file cannot be both. `style.css` resolves `--pl-mark` and `--pl-mark-small` per scheme, so markup just asks for the token.

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

The one part of the site that is written in markdown. `research/articles/` holds the sources; `research/build.py` compiles them:

```sh
pip install markdown            # once; the only authoring dependency
python3 research/build.py       # pages + PDFs + index + sitemap
```

Commit everything it writes. Each article becomes `/research/<slug>/` plus a PDF of the same page, printed through the print stylesheet (Chromium is found via `$CHROME` or the Playwright install; without one, pages build without the PDF link). The index at `/research/` and the research entries in `sitemap.xml` are regenerated on every run, so neither is ever edited by hand — the generated pages all share one header/footer template inside `build.py`, unlike the five hand-written pages, which still carry copies.

`research/articles/_template.md` documents the front matter and the two conventions that matter: asset paths are root-relative, and whitepaper PDFs are hand-dropped into `research/papers/` and linked from the article body.

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
models/           /models/ — preflight page for the model range
tools/            /tools/ — preflight page for the shipped tools (Notepad)
  vendor.py       Refreshes the vendored brand files from plicara-brand
benchmarks/       /benchmarks/ — index of published runs, one subpage per run
                  (mirrors /research/; regexeval-2026 is the first)
research/         /research/ — articles and analyses, generated from markdown
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
python3 -m http.server 8000
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
