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

Hosting uses a separate private Sites source repository with the same static assets. Its deployment identity is intentionally separate from this analysis repository. No source credential is stored in either checkout. The private preview was successfully deployed. The owner now prefers another free host; see `docs/hosting_options.md` for the shortlist. No provider-specific runtime code is needed.
