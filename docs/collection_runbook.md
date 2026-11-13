# Local collection runbook

From the repository root, after installation:

```bash
uv run bikeshare collect --count 1
uv run bikeshare collect --count 10 --interval 120
```

The second command is a bounded technical session, not a continuous service. The collector defaults to a two-minute interval and honours the largest observed TTL with a persistent next-request deadline; repeated one-shot invocations before the deadline skip safely. Network failures use bounded retries and are logged; after failure the CLI exits nonzero. An advisory file lock rejects overlapping collector processes. The project is supported on macOS/Linux; the lock uses fcntl.

For a practical local option, add a cron entry manually with `crontab -e`, substituting the absolute checkout path:

```cron
*/2 * * * * /bin/bash /absolute/path/bikeshare-product-analytics/scripts/collect_local.sh
```

The script resolves the repository root and uses its pinned virtual environment. Inspect `work/collector.log`, cron execution logs, latest successful retrieval, source report ages and growing `collection_runs`. Cron scheduling is a local convenience, not an uptime guarantee. Laptop sleep, network failure, permission changes and competing DuckDB processes create gaps. An always-on host is preferable for sustained collection. Do not schedule a tight loop to compensate for missed periods. Confirm disk space; raw JSON snapshots grow with every run, so monitor growth daily before choosing a retention policy. Preserve any retained source data locally under the licence; never commit the archive.

DuckDB has a single-process writer constraint. Stop/pause scheduled collection while running ingestion/dbt builds or the report, then resume; errors or gaps must be recorded, not hidden. The collector lock prevents two collectors, but does not coordinate all analysis processes. For production monitoring, stage immutable response files and batch database writes separately; this small local implementation deliberately does not claim that operational robustness.

Pilot: collect about two weeks to inspect coverage, stale stations, closures and possible repeated patterns. Do not wait in a tool session for this. For future-week uncertainty and recurring weekday effects, aim for 8–12 weeks across ordinary operating conditions, extending if data coverage or event counts are inadequate. Record collection interruptions and changes in feed, metadata, universe, TTL or request policy. Alerts/calendar responses are retained, but automated per-station schedule interpretation is not implemented; unexpected closures require manual review and documented eligibility changes.

After pausing collection:

```bash
uv run bikeshare report
bash scripts/validate.sh
```

The committed pilot is a short technical baseline. New snapshots change its horizon and coverage; update the written narrative and source-manifest reference before committing a refreshed report. A full mature station/day/window report requires interval splitting and the pre-specified coverage/weighting analyses described in the methodology. Current tooling does not pretend that those future conclusions already exist.
