# py-job-alerts

Scrapes LinkedIn and ZipRecruiter for Python backend roles and writes new
postings to a CSV you can check at your leisure.

Filters for:
- Hybrid in **Austin, TX** or fully **remote**
- **Full-time** only — no contracts, 1099, consulting, or temp roles
- **Python required** — must appear in title or description
- Established companies only — no startups
- No Microsoft, Google, Amazon, Netflix, GitLab, Apple, Meta, or LinkedIn postings
- Drops Java-only titles, full-stack-only titles, Dice/Indeed sourced postings

Each run deduplicates against `data/seen_jobs.csv` so the same posting never
appears twice.

---

## Setup

```bash
uv sync        # install dependencies (one time)
make run       # verify it works
make cron      # register cron job — runs every 4 hours
```

## Output

Results are appended to `data/jobs.csv` after each run:

| column | description |
|---|---|
| `title` | job title |
| `company` | company name |
| `location` | posted location |
| `is_remote` | true/false |
| `job_url` | direct link |

Check logs anytime: `tail -f /tmp/py-job-alerts.log`

## Configuration

All tuneable settings are in `src/py_job_alerts/config.py`:

- `SEARCH_TERMS` — queries sent to each board
- `SITES` — job boards to scrape (linkedin, zip_recruiter)
- `SITES_EXCLUDE` — board names to drop from results
- `HOURS_OLD` — only surface postings newer than N hours (default: 24)
- `RESULTS_WANTED` — max results per search term per run
- `CONTRACT_KEYWORDS` — substrings in title/description that flag a non-fulltime role
- `STARTUP_KEYWORDS` — description substrings that suggest a startup
- `MIN_COMPANY_SIZE` — drop companies below this headcount when data is available
- `COMPANY_EXCLUDE` — companies to always drop
- `COMPANY_DENYLIST` — companies always treated as startups

## Project structure

```
src/py_job_alerts/
  config.py    — all settings
  scraper.py   — jobspy wrapper (Austin + remote passes per search term)
  filters.py   — filtering pipeline
  dedup.py     — CSV-based seen-job tracking
  writer.py    — appends new jobs to data/jobs.csv
  main.py      — pipeline entry point
data/
  jobs.csv       (results, gitignored)
  seen_jobs.csv  (dedup state, gitignored)
```
