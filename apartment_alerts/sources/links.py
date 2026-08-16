"""
Link handling for the digest app.

By design this app does NOT scrape arbitrary user-provided sites — every site
has a different structure and many block automated requests, so attempting it is
unreliable and a security/maintenance burden. Instead, any link the user adds is
surfaced in the digest's "Check manually" section for a human to open.

Returns (listings, manual_links) to match the orchestrator's interface;
listings is always empty here.
"""


def dispatch(urls: list[str]) -> tuple[list[dict], list[dict]]:
    manual = [{"url": u, "reason": "Included for a manual check — open to view current listings."}
              for u in (urls or []) if isinstance(u, str) and u.strip()]
    return [], manual
