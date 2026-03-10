#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import pathlib
import re
import subprocess
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
EVIDENCE_SOURCES_PATH = DATA_DIR / "evidence_sources.json"
EVIDENCE_OUTPUT_PATH = DATA_DIR / "evidence.json"


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; LifeSciencesTracker/0.1; +https://www.gov.uk/)",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace")
    except Exception:
        result = subprocess.run(
            ["curl", "-L", "-s", url],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout


def first_match(patterns: list[str], document: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, document, flags=re.I | re.S)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip()
    return None


def normalize_date(value: str) -> str | None:
    value = html.unescape(value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"(\d)(st|nd|rd|th)", r"\1", value, flags=re.I)
    value = re.sub(r"\s+", " ", value).strip(" ,.;:-")

    for pattern in [
        r"\d{4}-\d{2}-\d{2}",
        r"\d{1,2}\s+[A-Za-z]+\s+\d{4}",
        r"[A-Za-z]+\s+\d{1,2},\s+\d{4}",
    ]:
        match = re.search(pattern, value)
        if match:
            candidate = match.group(0)
            for fmt in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%B %d, %Y", "%b %d, %Y"):
                try:
                    return dt.datetime.strptime(candidate, fmt).date().isoformat()
                except ValueError:
                    continue
    return None


def extract_title(document: str) -> str | None:
    return first_match(
        [
            r"<meta property=\"og:title\" content=\"([^\"]+)\"",
            r"<title[^>]*>(.*?)</title>",
            r"<h1[^>]*>(.*?)</h1>",
        ],
        document,
    )


def extract_published_at(document: str) -> str | None:
    value = first_match(
        [
            r"<meta property=\"article:published_time\" content=\"([^\"]+)\"",
            r"<meta name=\"article:published_time\" content=\"([^\"]+)\"",
            r"<meta name=\"govuk:public-updated-at\" content=\"([^\"]+)\"",
            r"\"datePublished\"\s*:\s*\"([^\"]+)\"",
            r"<time[^>]*datetime=\"([^\"]+)\"",
            r"Date published[^<]*</[^>]+>\s*<[^>]+>\s*([^<]+)",
            r"Published[^<]*</[^>]+>\s*<[^>]+>\s*([^<]+)",
            r"News\s*[–-]\s*([^<]+)",
        ],
        document,
    )
    if not value:
        return None
    return normalize_date(value)


def extract_summary(document: str) -> str | None:
    summary = first_match(
        [
            r"<meta property=\"og:description\" content=\"([^\"]*)\"",
            r"<p[^>]*class=\"gem-c-lead-paragraph[^\"]*\">(.*?)</p>",
            r"<p>(.*?)</p>",
        ],
        document,
    )
    if not summary:
        return None
    summary = re.sub(r"<[^>]+>", "", summary)
    summary = re.sub(r"\s+", " ", summary).strip()
    return summary or None


def extract_role_holder(document: str) -> str | None:
    holder = first_match(
        [
            r"Current role holder.*?<h3[^>]*>\s*(.*?)\s*</h3>",
            r"Current role holder:\s*(.*?)\s*</",
        ],
        document,
    )
    if not holder:
        return None
    holder = re.sub(r"<[^>]+>", "", holder)
    holder = re.sub(r"\s+", " ", holder).strip()
    return holder or None


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch official evidence sources for the tracker.")
    parser.add_argument("--manifest", default=str(EVIDENCE_SOURCES_PATH), help="Path to the evidence manifest.")
    args = parser.parse_args()

    manifest = json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8"))
    sources_out = []
    ministers_out = []
    (RAW_DIR / "sources").mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "ministers").mkdir(parents=True, exist_ok=True)

    for source in manifest["sources"]:
        try:
            raw_path = RAW_DIR / "sources" / f"{source['id']}.html"
            if raw_path.exists():
                document = raw_path.read_text(encoding="utf-8")
            else:
                document = fetch(source["url"])
                raw_path.write_text(document, encoding="utf-8")
            sources_out.append(
                {
                    **source,
                    "ok": True,
                    "fetched_at": utc_now_iso(),
                    "title": source.get("title_override") or extract_title(document),
                    "published_at": source.get("published_at_override") or extract_published_at(document),
                    "summary": source.get("summary_override") or extract_summary(document),
                }
            )
        except Exception as exc:  # pragma: no cover - network failures are surfaced in output
            sources_out.append(
                {
                    **source,
                    "ok": False,
                    "error": str(exc),
                    "fetched_at": utc_now_iso(),
                }
            )

    for role in manifest["minister_roles"]:
        try:
            raw_path = RAW_DIR / "ministers" / f"{role['id']}.html"
            if raw_path.exists():
                document = raw_path.read_text(encoding="utf-8")
            else:
                document = fetch(role["url"])
                raw_path.write_text(document, encoding="utf-8")
            ministers_out.append(
                {
                    **role,
                    "ok": True,
                    "fetched_at": utc_now_iso(),
                    "current_holder": extract_role_holder(document),
                    "published_at": extract_published_at(document),
                    "page_title": extract_title(document),
                }
            )
        except Exception as exc:  # pragma: no cover - network failures are surfaced in output
            ministers_out.append(
                {
                    **role,
                    "ok": False,
                    "error": str(exc),
                    "fetched_at": utc_now_iso(),
                }
            )

    EVIDENCE_OUTPUT_PATH.write_text(
        json.dumps(
            {
                "meta": {
                    "fetched_at": utc_now_iso(),
                },
                "sources": sources_out,
                "ministers": ministers_out,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
