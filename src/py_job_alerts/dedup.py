"""
CSV-based deduplication.

seen_jobs.csv stores a record of every job we have already notified about,
keyed by a stable MD5 hash of (job_url, title, company).  New jobs are those
whose hash does not appear in the file.
"""

import hashlib

import pandas as pd

from .config import SEEN_JOBS_CSV


def _job_id(row: pd.Series) -> str:
    """Return a stable hex digest that uniquely identifies a job posting."""
    key = "|".join([
        str(row.get("job_url", "")),
        str(row.get("title", "")),
        str(row.get("company", "")),
    ])
    return hashlib.md5(key.encode()).hexdigest()


def _load_seen_ids() -> set[str]:
    if not SEEN_JOBS_CSV.exists():
        return set()
    df = pd.read_csv(SEEN_JOBS_CSV, dtype=str, usecols=["id"])
    return set(df["id"].dropna())


def filter_new_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows from *df* that have not been seen before."""
    if df.empty:
        return df

    seen = _load_seen_ids()
    df = df.copy()
    df["_id"] = df.apply(_job_id, axis=1)
    new = df[~df["_id"].isin(seen)].reset_index(drop=True)
    print(f"[dedup] {len(new)} new / {len(df)} total after dedup")
    return new


def mark_seen(df: pd.DataFrame) -> None:
    """Append newly notified jobs to the seen-jobs CSV."""
    if df.empty or "_id" not in df.columns:
        return

    SEEN_JOBS_CSV.parent.mkdir(parents=True, exist_ok=True)

    cols = {"_id": "id", "title": "title", "company": "company", "job_url": "job_url"}
    available = {k: v for k, v in cols.items() if k in df.columns}
    new_records = df[list(available.keys())].rename(columns=available)

    if SEEN_JOBS_CSV.exists():
        existing = pd.read_csv(SEEN_JOBS_CSV, dtype=str)
        combined = pd.concat([existing, new_records], ignore_index=True).drop_duplicates(subset=["id"])
    else:
        combined = new_records

    combined.to_csv(SEEN_JOBS_CSV, index=False)
    print(f"[dedup] Marked {len(new_records)} job(s) as seen → {SEEN_JOBS_CSV}")
