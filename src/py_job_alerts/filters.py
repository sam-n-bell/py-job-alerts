"""
Filtering pipeline for job postings.

Each predicate operates on a single DataFrame row (pd.Series).
apply_filters() runs all predicates and returns only passing rows.
"""

import pandas as pd

from .config import (
    COMPANY_ALLOWLIST,
    COMPANY_DENYLIST,
    COMPANY_EXCLUDE,
    CONTRACT_KEYWORDS,
    MIN_COMPANY_SIZE,
    SITES_EXCLUDE,
    STARTUP_KEYWORDS,
)


# ---------------------------------------------------------------------------
# Individual predicates  (return True = should be DROPPED)
# ---------------------------------------------------------------------------

def _is_excluded_site(row: pd.Series) -> bool:
    """Drop postings sourced from excluded job boards."""
    site = str(row.get("site", "")).lower()
    return any(s in site for s in SITES_EXCLUDE)


def _is_excluded_company(row: pd.Series) -> bool:
    """Drop postings from companies on the explicit exclude list."""
    company = str(row.get("company", "")).lower()
    return any(excl in company for excl in COMPANY_EXCLUDE)

def _is_contract(row: pd.Series) -> bool:
    """Drop postings that appear to be contract / non-fulltime."""
    haystack = " ".join([
        str(row.get("title", "")),
        str(row.get("description", "")),
        str(row.get("job_type", "")),
    ]).lower()
    return any(kw in haystack for kw in CONTRACT_KEYWORDS)


def _is_startup(row: pd.Series) -> bool:
    """Drop postings from companies that look like startups."""
    company = str(row.get("company", "")).lower()

    # Allowlist bypasses all startup checks.
    if any(allowed in company for allowed in COMPANY_ALLOWLIST):
        return False

    # Explicit denylist.
    if any(denied in company for denied in COMPANY_DENYLIST):
        return True

    # Description signals.
    desc = str(row.get("description", "")).lower()
    if any(kw in desc for kw in STARTUP_KEYWORDS):
        return True

    # Employee count (when jobspy returns it).
    size = row.get("company_num_employees")
    if size is not None:
        try:
            if float(size) < MIN_COMPANY_SIZE:
                return True
        except (ValueError, TypeError):
            pass

    return False


def _is_wrong_location(row: pd.Series) -> bool:
    """Drop postings that are neither remote nor Austin-area."""
    # jobspy sets is_remote=True for fully remote postings.
    if row.get("is_remote") is True:
        return False

    location = str(row.get("location", "")).lower()
    if "austin" in location:
        return False

    # Some postings label hybrid in the description.
    desc = str(row.get("description", "")).lower()
    if "austin" in desc and "hybrid" in desc:
        return False

    return True


def _lacks_python(row: pd.Series) -> bool:
    """Drop postings where 'python' appears in neither title nor description."""
    title = str(row.get("title", "")).lower()
    desc = str(row.get("description", "")).lower()
    return "python" not in title and "python" not in desc


def _is_fullstack_without_backend(row: pd.Series) -> bool:
    """Drop postings with 'full stack' in the title unless 'backend' is also present."""
    title = str(row.get("title", "")).lower()
    return "full stack" in title and "backend" not in title


def _is_java_without_python(row: pd.Series) -> bool:
    """Drop postings where Java appears in the title without Python."""
    title = str(row.get("title", "")).lower()
    return "java" in title and "python" not in title


def _is_not_fulltime(row: pd.Series) -> bool:
    """Drop postings that are explicitly not full-time."""
    job_type = str(row.get("job_type", "")).lower()

    # If the field is populated, trust it.
    if job_type and job_type not in ("nan", "none"):
        return "fulltime" not in job_type and "full_time" not in job_type and "full-time" not in job_type

    # Fall back to description scan when field is absent.
    desc = str(row.get("description", "")).lower()
    part_time_signals = ["part-time", "part time", "parttime", "per diem"]
    return any(sig in desc for sig in part_time_signals)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Return a filtered copy of *df* with unsuitable postings removed."""
    if df.empty:
        return df

    keep = ~(
        df.apply(_is_excluded_site, axis=1)
        | df.apply(_is_excluded_company, axis=1)
        | df.apply(_lacks_python, axis=1)
        | df.apply(_is_fullstack_without_backend, axis=1)
        | df.apply(_is_java_without_python, axis=1)
        | df.apply(_is_contract, axis=1)
        | df.apply(_is_startup, axis=1)
        | df.apply(_is_wrong_location, axis=1)
        | df.apply(_is_not_fulltime, axis=1)
    )

    filtered = df[keep].reset_index(drop=True)
    dropped = len(df) - len(filtered)
    print(f"[filters] Kept {len(filtered)} / {len(df)} postings ({dropped} dropped)")
    return filtered
