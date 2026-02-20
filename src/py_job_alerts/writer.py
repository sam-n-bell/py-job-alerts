"""
Writes new job postings to data/jobs.csv.

Each run appends newly found jobs so the file grows over time.
Open it in Excel, Numbers, or any CSV viewer to browse results.
"""

import pandas as pd

from .config import JOBS_CSV

def write_jobs(df: pd.DataFrame) -> None:
    """Append *df* rows to jobs.csv, keeping only the most useful columns."""
    if df.empty:
        return

    JOBS_CSV.parent.mkdir(parents=True, exist_ok=True)

    out = pd.DataFrame()
    out["title"] = df.get("title", "")
    out["company"] = df.get("company", "")
    out["location"] = df.get("location", "")
    out["is_remote"] = df.get("is_remote", "")
    out["job_url"] = df.get("job_url", "")

    write_header = not JOBS_CSV.exists()
    out.to_csv(JOBS_CSV, mode="a", index=False, header=write_header)
    print(f"[writer] Appended {len(out)} job(s) → {JOBS_CSV}")
