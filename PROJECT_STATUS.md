# Project status · 13 November 2026

**Delivered implementation and historical analysis; prospective service evidence remains a technical pilot.** No real operator experiment or stable reliability ranking is claimed.

## Completed

- Inspected empty workspace and applicable instructions; verified GitHub authentication and absence of existing remotes/repository.
- Verified official sources, actual trip/GBFS schema, licence, TTL/report clocks and public app functionality; performed a small feasibility ingestion before full ingestion.
- Ingested three complete published archives (August–October 2026), 2,000,497 source rows; analysed 1,999,232 eligible rentals using actual local start month and an explicit exclusion waterfall.
- Built Python collection/analysis, DuckDB storage, three dbt models and eight dbt data tests, with a frozen uv dependency graph.
- Collected two real GBFS snapshots for 875 monitored stations across 95 seconds; froze the station cohort and retained source clocks, metadata versions, operating flags and type counts locally.
- Implemented capped availability intervals, coverage, closure handling, zero-run support and sensitivity summaries. No pilot reliability rankings or future-week intervals.
- Produced six evidence-labelled charts, product recommendation, methodology, measurement, experiment/tracking plans, repeated synthetic simulation, interview notes, decision log and sceptical review.
- Ran 23 offline fixture/integration tests, lint and output checks; ran the real-data dbt build. Reviewed exclusions, month boundaries, DST, joins, denominators, uncertainty and chart rendering.
- Prepared credential-free CI checks and practical local scheduling instructions. No scheduler is installed or left running.
- Created and pushed the private repository: https://github.com/stephanieboyle/bikeshare-product-analytics. GitHub CI passed on Linux/Python 3.11: https://github.com/stephanieboyle/bikeshare-product-analytics/actions/runs/43404163212 (reviewed implementation commit 2487416).

## Evidence still required

1. Two-week exploratory collection for coverage/logging; aim for 8–12 weeks before recurring weekday questions and possible block-based inference, extending if necessary.
2. Mature interval splitting by day/window; coverage/ranking/coarser-polling sensitivities and nearby-alternative analysis. These require new observations.
3. Hands-on current-app audit and rider research; official help alone does not establish missing functionality or rider value.
4. Operator account/intent/rental linkage, instrumentation A/A pilot and field power/design calibration, including inventory interference. Public trips cannot supply these.

## Operation and next actions

Run commands from the repository root; installation and source downloads require network. See README for reproducibility and `docs/collection_runbook.md` for a local cron option. Pause collection during DuckDB analysis/writes. Do not commit source data or make the repository public without instruction.

GitHub delivery is complete and the repository is verified private. Source observations remain local. The remaining work is evidence collection and operator/research access for a real field experiment, not a missing implementation or credential step.
