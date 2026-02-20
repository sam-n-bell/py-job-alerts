"""
Central configuration for py-job-alerts.
Edit this file to tune search terms, filters, and notification settings.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# ntfy
# ---------------------------------------------------------------------------
NTFY_TOPIC = "sam-bell-job-alerts-2026"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).parent.parent.parent  # repo root
DATA_DIR = _ROOT / "data"
SEEN_JOBS_CSV = DATA_DIR / "seen_jobs.csv"
JOBS_CSV = DATA_DIR / "jobs.csv"

# ---------------------------------------------------------------------------
# Job search
# ---------------------------------------------------------------------------
SEARCH_TERMS: list[str] = [
    "Python backend engineer",
    "Python software engineer",
    "Python developer",
    "backend engineer Python",
]

# Used for Austin-local (hybrid) searches
AUSTIN_LOCATION = "Austin, TX"

# Job boards to query
SITES: list[str] = ["linkedin", "zip_recruiter"]

# Job board sources to exclude from results (matched against the 'site' column).
SITES_EXCLUDE: list[str] = ["dice", "indeed"]

# Only return postings newer than this many hours
HOURS_OLD = 24

# Max results per (site × search_term) call
RESULTS_WANTED = 20

# ---------------------------------------------------------------------------
# Contract / non-fulltime filter
# These substrings (case-insensitive) in title or description mark a job
# as contract/non-fulltime and cause it to be dropped.
# ---------------------------------------------------------------------------
CONTRACT_KEYWORDS: list[str] = [
    "consultant",
    "consulting",
    "contract",
    "contractor",
    "c2c",
    "corp-to-corp",
    "corp to corp",
    "1099",
    "w2 only",
    "temporary",
    " temp ",
    "part-time",
    "part time",
    "freelance",
    "contingent",
    "fixed-term",
]

# ---------------------------------------------------------------------------
# Startup filter
# Substrings in the job description that suggest a startup environment.
# ---------------------------------------------------------------------------
STARTUP_KEYWORDS: list[str] = [
    "series a",
    "series b",
    "seed stage",
    "seed round",
    "early stage",
    "founding team",
    "ground floor",
    "fast-paced startup",
    "our startup",
    "we're a startup",
    "we are a startup",
    "pre-ipo",
]

# Minimum number of employees to be considered non-startup (when data is available).
MIN_COMPANY_SIZE = 500

# Companies to never show in results, regardless of any other logic.
COMPANY_EXCLUDE: list[str] = [
    "microsoft",
    "google",
    "amazon",
    "netflix",
    "gitlab",
    "apple",
    "meta",
    "linkedin",
]

