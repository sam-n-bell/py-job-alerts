"""
Entry point for py-job-alerts.

Pipeline:
  1. Scrape   — fetch raw job postings from all configured boards
  2. Filter   — drop contracts, startups, wrong location, non-fulltime
  3. Dedup    — drop anything already seen in seen_jobs.csv
  4. Notify   — push summary to ntfy
  5. Persist  — append new job IDs to seen_jobs.csv
"""

from .dedup import filter_new_jobs, mark_seen
from .filters import apply_filters
from .scraper import scrape_all
from .writer import write_jobs


def main() -> None:
    print("[main] Starting job alert run…")

    print("[main] Scraping job boards…")
    raw = scrape_all()
    print(f"[main] {len(raw)} raw postings retrieved")

    if raw.empty:
        print("[main] No postings found — exiting.")
        return

    filtered = apply_filters(raw)

    if filtered.empty:
        print("[main] All postings filtered out — nothing to report.")
        return

    new_jobs = filter_new_jobs(filtered)

    if new_jobs.empty:
        print("[main] No new jobs since last run — nothing to report.")
        return

    write_jobs(new_jobs)
    mark_seen(new_jobs)

    print(f"[main] Done — notified about {len(new_jobs)} new job(s).")
