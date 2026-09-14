"""Check responsive pages and keyboard access against a local preview."""

import os

from playwright.sync_api import sync_playwright


BASE = os.environ.get("SITE_URL", "http://127.0.0.1:4001")
ROUTES = ("/", "/research/", "/research/whether-anyone-ever-ran-it/", "/benchmarks/adventurebench/", "/tools/")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=os.environ.get("CHROME"))
    for width in (390, 1280):
        for theme in ("light", "dark"):
            context = browser.new_context(viewport={"width": width, "height": 844}, color_scheme=theme, reduced_motion="reduce")
            page = context.new_page()
            for route in ROUTES:
                response = page.goto(BASE + route, wait_until="networkidle")
                assert response.status == 200, route
                assert page.evaluate("document.documentElement.scrollWidth") <= width, (route, width, theme)
                for region in page.locator(".table-wrap, .article-body table, .article-body pre").all():
                    if region.evaluate("el => el.scrollWidth > el.clientWidth"):
                        assert region.get_attribute("tabindex") == "0", route
                        region.focus()
                        page.keyboard.press("ArrowRight")
                        page.wait_for_function("el => el.scrollLeft > 0", arg=region.element_handle())
            page.emulate_media(media="print")
            page.goto(BASE + "/research/whether-anyone-ever-ran-it/", wait_until="networkidle")
            assert page.locator(".article-body blockquote").first.evaluate("el => getComputedStyle(el).color") == "rgb(5, 25, 43)"
            context.close()
    browser.close()
print("Responsive layout, keyboard scrolling, and print text checks passed.")
