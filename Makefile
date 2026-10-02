.PHONY: setup metadata check build serve setup-browser

setup:
	uv sync --locked

metadata:
	uv run --python 3.12 --locked --script .plicara/check.py

check: metadata
	uv lock --check
	uv run --locked python -m unittest discover -s research

build:
	uv run --locked python research/build.py --no-pdf

serve:
	uv run --locked python -m http.server 8000

setup-browser:
	uv run --locked python -m playwright install chromium
