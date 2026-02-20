"""
Scrapes job postings via python-jobspy.

Two passes are made for each search term:
  1. Austin, TX — picks up on-site and hybrid local roles.
  2. Remote-only — nationwide remote Python backend roles.

Results from all passes are combined and deduplicated by job URL.
"""

import pandas as pd
from jobspy import scrape_jobs

from .config import (
    AUSTIN_LOCATION,
    HOURS_OLD,
    RESULTS_WANTED,
    SEARCH_TERMS,
    SITES,
)


def _scrape(search_term: str, location: str, *, is_remote: bool) -> pd.DataFrame:
    try:
        return scrape_jobs(
            site_name=SITES,
            search_term=search_term,
            location=location,
            results_wanted=RESULTS_WANTED,
            hours_old=HOURS_OLD,
            country_indeed="USA",
            is_remote=is_remote,
            verbose=0,
        )
    except Exception as exc:
        print(f"[scraper] Warning — '{search_term}' ({location}): {exc}")
        return pd.DataFrame()


def scrape_all() -> pd.DataFrame:
    """Return a deduplicated DataFrame of all scraped job postings."""
    frames: list[pd.DataFrame] = []

    for term in SEARCH_TERMS:
        # Pass 1: Austin area (captures hybrid + on-site)
        local = _scrape(term, AUSTIN_LOCATION, is_remote=False)
        if not local.empty:
            frames.append(local)

        # Pass 2: Remote-only, nationwide
        remote = _scrape(term, "United States", is_remote=True)
        if not remote.empty:
            frames.append(remote)

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)

    # Deduplicate by URL; fall back to title+company if URL is missing.
    if "job_url" in combined.columns:
        combined = combined.drop_duplicates(subset=["job_url"])
    else:
        combined = combined.drop_duplicates(subset=["title", "company"])

    return combined.reset_index(drop=True)
