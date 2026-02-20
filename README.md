# py-job-alerts

Automated Python backend job alerts delivered to your phone via [ntfy](https://ntfy.sh).

Searches LinkedIn, Indeed, Glassdoor, and ZipRecruiter for Python backend roles that are:
- Hybrid in **Austin, TX** or fully **remote**
- **Full-time** permanent positions (no contracts, no 1099)
- At established companies (no startups)

New postings are deduplicated against `data/seen_jobs.csv` so you only get notified once per posting.

---

## Requirements

- [uv](https://docs.astral.sh/uv/) installed
- Python 3.14t (free-threaded) — uv uses it automatically via `.python-version`
- ntfy app on your phone subscribed to `sam-bell-job-alerts-2026`

## Setup

```bash
uv sync
uv run job-alerts   # test run
```

## Running on a schedule (cron)

```bash
crontab -e
```

Add (adjust path if needed):

```
0 */4 * * * cd /Users/sambell/Code/py-job-alerts && /Users/sambell/.local/bin/uv run job-alerts >> /tmp/py-job-alerts.log 2>&1
```

Check logs: `tail -f /tmp/py-job-alerts.log`

## Configuration

All tuneable settings are in `src/py_job_alerts/config.py`:

- `SEARCH_TERMS` — queries sent to each board
- `HOURS_OLD` — only surface postings newer than N hours (default: 24)
- `RESULTS_WANTED` — max results per search term per run
- `CONTRACT_KEYWORDS` — substrings that flag a contract role
- `STARTUP_KEYWORDS` — description substrings that suggest a startup
- `MIN_COMPANY_SIZE` — drop companies below this headcount when size data is available
- `COMPANY_ALLOWLIST` — companies always kept regardless of startup signals
- `COMPANY_DENYLIST` — companies always dropped

## Project structure

```
src/py_job_alerts/
  config.py    — all settings
  scraper.py   — jobspy wrapper (Austin + remote passes per search term)
  filters.py   — drop contracts / startups / wrong location / non-fulltime
  dedup.py     — CSV-based seen-job tracking
  notifier.py  — ntfy push notification
  main.py      — pipeline entry point
data/
  seen_jobs.csv  (created on first run, gitignored)
```
