# Bike Reliability Studio

An interactive portfolio reporting app: journey overview, station explorer, availability technical pilot, experiment lab, and methods/evidence. Dusty blue, rose pink and warm cream/peach palette, following the owner's preferences.

The app contains only aggregate analytical cells. It does not load raw trips, impersonate an operator service or poll live GBFS. Month, bicycle type and published category filters apply to historical sections. Pilot sensitivities use the saved 95-second sample; the experiment calculator is illustrative and separate from the stored synthetic simulation.

## Run locally

From the repository root:

```bash
python3 -m http.server 8765 --directory dashboard --bind 127.0.0.1
# Open http://127.0.0.1:8765
node dashboard/check.mjs
```

Rebuild data from the validated local models:

```bash
uv run python scripts/export_dashboard.py dashboard/data.json
node dashboard/check.mjs
```

The export reconciles daily/hourly cells and station endpoints to the fact model. It preserves actual start-month cohort attribution, direction-specific missing-station denominators and evidence-class labels. Station CSV export is an aggregate analysis of the current filters/search, not a standalone source dataset. Print report prints the currently selected view.

## Live version

**https://bike-reliability-studio.pages.dev** — public portfolio site on Cloudflare Pages; no visitor sign-in required. The source repository stays private.

Cloudflare is connected only to `bikeshare-product-analytics`. Production branch: `main`; root directory: `dashboard`; framework: `None`; build command: blank; output directory: `.`. Git pushes trigger automatic deployments. This is static hosting with no Functions, database or paid runtime services. No paid plan, domain purchase or payment details were enabled during setup.

`reports/deployment.json` records the verified URL, source commit, served asset hashes and browser checks. An older owner-private Sites preview also exists, but this Cloudflare URL is the portfolio version.
