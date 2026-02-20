"""
Sends push notifications to ntfy.sh.

Each run that finds new jobs fires a single notification containing a
formatted summary (up to 10 jobs).  ntfy.sh has a ~4 KB body limit, so
long descriptions are intentionally excluded.
"""

import requests

from .config import NTFY_URL

_MAX_JOBS_IN_BODY = 10


def _format_job(row) -> str:
    title = str(row.get("title", "N/A"))
    company = str(row.get("company", "N/A"))
    is_remote = row.get("is_remote")
    location = str(row.get("location", ""))
    url = str(row.get("job_url", ""))

    loc_label = "Remote" if is_remote is True else (location or "Unknown location")
    line = f"• {title} @ {company} ({loc_label})"
    if url and url != "nan":
        line += f"\n  {url}"
    return line


def send_notification(df) -> None:
    """Fire a single ntfy notification summarising all new jobs in *df*."""
    if df.empty:
        return

    count = len(df)
    plural = "s" if count != 1 else ""
    title = f"{count} new Python job{plural} found"

    job_lines = [_format_job(row) for _, row in df.iterrows()]
    body = "\n\n".join(job_lines[:_MAX_JOBS_IN_BODY])
    if count > _MAX_JOBS_IN_BODY:
        body += f"\n\n…and {count - _MAX_JOBS_IN_BODY} more"

    try:
        resp = requests.post(
            NTFY_URL,
            data=body.encode("utf-8"),
            headers={
                "Title": title,
                "Priority": "default",
                "Tags": "snake,briefcase",
            },
            timeout=10,
        )
        resp.raise_for_status()
        print(f"[notifier] Sent: {title}")
    except requests.RequestException as exc:
        print(f"[notifier] Failed to send notification: {exc}")
