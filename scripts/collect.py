#!/usr/bin/env python3
"""Reproduce the title tag study dataset.

Fetches each homepage once as a logged-out visitor with a desktop browser user
agent, follows redirects, and records what the server sends in its HTML. No
JavaScript is executed, so anything a page renders client-side is invisible here.

Usage:
    python3 collect.py                 # all hosts -> title-tag-study.csv
    python3 collect.py --limit 5       # first five hosts only
    python3 collect.py --out mine.csv --json mine.json

Standard library only. Python 3.9+.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import html as html_module
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

SITES: dict[str, list[str]] = {
    "News": [
        "bbc.com", "cnn.com", "nytimes.com", "theguardian.com", "reuters.com", "apnews.com",
        "washingtonpost.com", "forbes.com", "techcrunch.com", "theverge.com", "wired.com",
        "arstechnica.com", "engadget.com", "npr.org", "bloomberg.com",
    ],
    "E-commerce": [
        "amazon.com", "ebay.com", "etsy.com", "shopify.com", "walmart.com", "target.com",
        "bestbuy.com", "aliexpress.com", "homedepot.com", "wayfair.com", "ikea.com", "zappos.com",
    ],
    "Software": [
        "microsoft.com", "apple.com", "google.com", "adobe.com", "salesforce.com", "hubspot.com",
        "slack.com", "zoom.us", "notion.so", "atlassian.com", "dropbox.com", "canva.com", "figma.com",
        "stripe.com", "mailchimp.com", "gitlab.com", "github.com", "cloudflare.com", "digitalocean.com",
        "vercel.com", "netlify.com", "wordpress.com", "wix.com", "squarespace.com", "webflow.com",
        "bing.com",
    ],
    "Social and media": [
        "reddit.com", "x.com", "linkedin.com", "instagram.com", "facebook.com", "pinterest.com",
        "youtube.com", "tiktok.com", "medium.com", "quora.com", "twitch.tv", "spotify.com",
        "netflix.com", "soundcloud.com", "vimeo.com", "duckduckgo.com",
    ],
    "Education, government, non-profit": [
        "harvard.edu", "mit.edu", "stanford.edu", "ox.ac.uk", "nasa.gov", "whitehouse.gov", "gov.uk",
        "un.org", "wikipedia.org", "archive.org", "mozilla.org", "w3.org", "eff.org",
        "khanacademy.org", "coursera.org",
    ],
    "Travel, local and services": [
        "airbnb.com", "booking.com", "tripadvisor.com", "expedia.com", "uber.com", "doordash.com",
        "yelp.com", "indeed.com", "glassdoor.com", "zillow.com", "craigslist.org", "weather.com",
        "imdb.com", "espn.com", "nationalgeographic.com",
    ],
}

COLUMNS = [
    "host", "category", "status", "title", "title_len", "description", "description_len",
    "h1_count", "has_canonical", "has_structured_data", "has_og_title", "has_viewport",
]

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
DESC_TAG_RE = re.compile(
    r"""<meta[^>]+name\s*=\s*["']description["'][^>]*>""", re.IGNORECASE
)
CONTENT_RE = re.compile(r"""content\s*=\s*(["'])(.*?)\1""", re.IGNORECASE | re.DOTALL)
H1_RE = re.compile(r"<h1\b", re.IGNORECASE)
CANONICAL_RE = re.compile(r"""<link[^>]+rel\s*=\s*["']?canonical""", re.IGNORECASE)
VIEWPORT_RE = re.compile(r"""<meta[^>]+name\s*=\s*["']?viewport""", re.IGNORECASE)
JSONLD_RE = re.compile(r"""<script[^>]+application/ld\+json""", re.IGNORECASE)
OG_TITLE_RE = re.compile(r"""<meta[^>]+property\s*=\s*["']og:title""", re.IGNORECASE)


def collapse(text: str) -> str:
    """Decode entities, strip tags, and collapse runs of whitespace."""
    return re.sub(r"\s+", " ", html_module.unescape(re.sub(r"<[^>]*>", "", text))).strip()


def measure(page: str) -> dict:
    """Measure the fields this study reports, or None where the page omits them."""
    title = None
    match = TITLE_RE.search(page)
    if match:
        title = collapse(match.group(0)[len("<title"):].split(">", 1)[-1])

    description = None
    tag = DESC_TAG_RE.search(page)
    if tag:
        content = CONTENT_RE.search(tag.group(0))
        if content:
            description = collapse(content.group(2))

    return {
        "title": title,
        "title_len": None if title is None else len(title),
        "description": description,
        "description_len": None if description is None else len(description),
        "h1_count": len(H1_RE.findall(page)),
        "has_canonical": bool(CANONICAL_RE.search(page)),
        "has_structured_data": bool(JSONLD_RE.search(page)),
        "has_og_title": bool(OG_TITLE_RE.search(page)),
        "has_viewport": bool(VIEWPORT_RE.search(page)),
    }


def fetch(host: str, retries: int = 2) -> dict:
    """One GET per host. Redirects are followed by urllib."""
    request = urllib.request.Request(
        f"https://{host}/",
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip",
        },
    )
    status, final_url, body, error, content_type = 0, f"https://{host}/", "", None, ""
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                status = response.status
                final_url = response.geturl()
                content_type = response.headers.get("Content-Type", "")
                raw = response.read()
                if response.headers.get("Content-Encoding") == "gzip" or raw[:2] == b"\x1f\x8b":
                    raw = gzip.decompress(raw)
                body = raw.decode("utf-8", errors="replace")
            error = None
            break
        except urllib.error.HTTPError as exc:
            status = exc.code
            final_url = exc.geturl()
            content_type = exc.headers.get("Content-Type", "") if exc.headers else ""
            try:
                body = exc.read().decode("utf-8", errors="replace")
            except Exception:  # noqa: BLE001 - body is optional here
                body = ""
            error = None
            break
        except Exception as exc:  # noqa: BLE001 - network errors vary by host
            status, body, error = 0, "", f"{type(exc).__name__}: {exc}"
            if attempt < retries:
                time.sleep(2 * (attempt + 1))

    reachable = (
        200 <= status < 400
        and "html" in content_type.lower()
        and body != ""
    )
    return {
        "status": status,
        "final_url": final_url,
        "bytes": len(body.encode("utf-8")),
        "reachable": reachable,
        "error": error,
        "html": body if reachable else "",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=0, help="only the first N hosts")
    parser.add_argument("--out", default="title-tag-study.csv", help="CSV destination")
    parser.add_argument("--json", default="", help="optional raw JSON destination")
    args = parser.parse_args()

    queue = [(category, host) for category, hosts in SITES.items() for host in hosts]
    if args.limit:
        queue = queue[: args.limit]

    rows = []
    for index, (category, host) in enumerate(queue, start=1):
        result = fetch(host)
        row = {
            "host": host,
            "category": category,
            "status": result["status"],
            "reachable": result["reachable"],
            "final_url": result["final_url"],
            "bytes": result["bytes"],
            "error": result["error"],
            "title": None,
            "title_len": None,
            "description": None,
            "description_len": None,
            "h1_count": None,
            "has_canonical": None,
            "has_structured_data": None,
            "has_og_title": None,
            "has_viewport": None,
        }
        if result["reachable"]:
            row.update(measure(result["html"]))
        rows.append(row)
        print(
            f"[{index}/{len(queue)}] {host}: status {result['status']}, "
            f"{'reachable' if result['reachable'] else 'not reachable'}",
            file=sys.stderr,
        )

    reachable = [row for row in rows if row["reachable"]]
    with open(args.out, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(COLUMNS)
        for row in reachable:
            writer.writerow(
                [
                    ("yes" if row[column] else "no") if isinstance(row[column], bool)
                    else ("" if row[column] is None else row[column])
                    for column in COLUMNS
                ]
            )

    if args.json:
        payload = {
            "meta": {
                "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "collected_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "user_agent": USER_AGENT,
                "requested": len(rows),
                "reachable": len(reachable),
                "method": "One HTTPS GET per homepage, redirects followed, HTML only, no JavaScript executed.",
                "script": "collect.py",
            },
            "rows": rows,
        }
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=4, ensure_ascii=False)
            handle.write("\n")

    print(f"Requested {len(rows)} homepages, {len(reachable)} reachable. Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
