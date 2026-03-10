#!/usr/bin/env python3
from __future__ import annotations

import argparse
import calendar
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
PLAN_HTML_PATH = RAW_DIR / "life_sciences_sector_plan.html"
PLAN_REGISTER_PATH = DATA_DIR / "plan_register.json"
PLAN_URL = "https://www.gov.uk/government/publications/life-sciences-sector-plan/life-sciences-sector-plan"

PILLAR_MAP = {
    "pillar-1": {
        "id": "rd",
        "title": "Enabling world class R&D",
    },
    "pillar-2": {
        "id": "invest",
        "title": "Making the UK an outstanding place to start, grow, scale, and invest",
    },
    "pillar-3": {
        "id": "nhs",
        "title": "Driving health innovation and NHS reform",
    },
}

ACTION_TITLE_OVERRIDES = {
    "2a": "Establish pre-clinical translational infrastructure and translational networks",
    "2b": "Publish the alternative methods strategy",
    "9i": "Expand UK Biobank research capability",
    "9ii": "Scale Our Future Health as a clinical trials resource",
    "9iii": "Expand Genomics England's research database",
    "9iv": "Use NHS genomic networks to accelerate adoption of genomic innovation",
    "11": "Create a UK-wide research portfolio database and management tool",
    "11ii": "Create a single searchable database of clinical trial activity",
    "13": "Deploy additional British Business Bank growth capital for life sciences",
    "14": "Publish British Business Bank VC return data",
    "16": "Build a life sciences training and skills system",
    "17": "Deliver sector-specific life sciences skills programmes",
    "18": "Use the Global Talent Taskforce and visa system to attract talent",
    "19": "Deliver the Life Sciences Innovative Manufacturing Fund",
    "21": "Refine implementation of the NHS Net Zero Roadmap",
    "22": "Land at least one major strategic partnership per year",
    "23": "Support 10 to 20 high-potential UK companies to scale and stay in the UK",
    "24": "Strengthen the Health Innovation Network to drive innovation and investment",
    "25": "Reduce barriers to market entry through faster regulation",
    "26": "Ensure NICE processes are timely, agile, and transparent",
    "27": "Enhance MHRA and NICE coordination for faster market entry",
    "28": "Reduce friction so effective medicines reach patients faster",
    "29": "Create low-friction procurement and contracting for MedTech",
    "30": "Place a growth mandate on NHS commercial activity",
    "31": "Update and expand the Innovation Scorecard",
    "32": "Deliver the Healthcare Goals programme",
    "33": "Establish Regional Health Innovation Zones",
}

ROADMAP_MATCHERS = [
    ("medical devices statement of policy intent", "25"),
    ("providing easily accessible scientific advice", "25"),
    ("global talent taskforce", "18"),
    ("turing ai pioneer fellowship", "17"),
    ("10 year uk research workforce strategy", "16"),
    ("nihr’s improving health and economic growth delivery plan", "12"),
    ("alternative methods strategy", "2b"),
    ("value based procurement pilot launch", "29"),
    ("skills-focused industry workshops", "17"),
    ("post-16 education and skills strategy", "16"),
    ("commercial clinical trial approval and set up time", "3"),
    ("improved coordination with nihr activity", "5"),
    ("identified game-changing technologies", "5"),
    ("rbp will be launched", "29"),
    ("begin deploying new industrial strategy capital", "13"),
    ("enhance monitoring and reporting functions", "13"),
    ("single searchable database of clinical trial activity", "11ii"),
    ("centres of excellence in regulatory science and innovation", "17"),
    ("minimum viable product for the hdrs", "7"),
    ("publish a new framework for medical devices", "25"),
    ("pre-market statutory instrument", "25"),
    ("new data assets will be brought into scope for the hdrs", "7"),
    ("ai research screening platform", "6"),
    ("pass regulations reforming the current health service", "8"),
    ("pre-clinical translational hub", "2a"),
    ("wider nhs research data access approvals and governance system", "8"),
    ("nihr innovation catalyst", "6"),
    ("technology appraisals started in 2025/2026", "26"),
    ("innovator passport", "29"),
    ("vc investment return data", "14"),
    ("device access pathway", "27"),
    ("ilap", "27"),
    ("hdrs will begin creating uk-wide service", "7"),
    ("review of priority skills needs", "16"),
    ("translational research networks", "2a"),
    ("2 innovations supported", "6"),
    ("our future health", "9ii"),
    ("uk biobank", "9i"),
    ("genomics england", "9iii"),
    ("healthcare goals", "32"),
    ("sustained increase in r&d funding towards prevention", "10"),
    ("review activity across all skills actions", "16"),
]

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

SEASON_DATES = {
    "spring": (5, 31),
    "summer": (8, 31),
    "autumn": (11, 30),
    "fall": (11, 30),
    "winter": (2, 28),
}


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


def ensure_plan_html(force: bool = False) -> str:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if force and PLAN_HTML_PATH.exists():
        return PLAN_HTML_PATH.read_text(encoding="utf-8")
    if not PLAN_HTML_PATH.exists():
        PLAN_HTML_PATH.write_text(fetch(PLAN_URL), encoding="utf-8")
    return PLAN_HTML_PATH.read_text(encoding="utf-8")


def clean_line(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip(" -")


def html_to_text(fragment: str) -> str:
    fragment = re.sub(r"<\s*br\s*/?\s*>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"</(p|li|ul|ol|h1|h2|h3|h4|h5|h6|td|th|tr)>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"<li[^>]*>", "- ", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    text = html.unescape(fragment)
    lines = [clean_line(line) for line in text.splitlines()]
    return "\n".join([line for line in lines if line])


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def dedupe_strings(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        key = clean_line(value).lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(clean_line(value))
    return result


def infer_pillar(pillar_html_id: str) -> dict[str, str]:
    for prefix, pillar in PILLAR_MAP.items():
        if pillar_html_id.startswith(prefix):
            return pillar
    raise ValueError(f"Unmapped pillar id: {pillar_html_id}")


def extract_territory_and_text(title_text: str) -> tuple[str | None, str]:
    lines = [line for line in title_text.splitlines() if line]
    territory_lines = []
    content_lines = []
    for line in lines:
        if re.fullmatch(r"(UK|England|UK-wide collaboration|UK/England|England and > UK-wide collaboration)", line, flags=re.I):
            territory_lines.append(line)
        else:
            content_lines.append(line)
    territory = ", ".join(dedupe_strings(territory_lines)) if territory_lines else None
    return territory, " ".join(content_lines)


def split_sro_text(value: str) -> tuple[str, str]:
    first_line = value.splitlines()[0]
    if "," in first_line:
        role, body = first_line.rsplit(",", 1)
        return clean_line(role), clean_line(body)
    return clean_line(first_line), clean_line(first_line)


def parse_due_phrase(text: str) -> dict[str, str] | None:
    text = clean_line(re.sub(r"^\([^)]*\)\s*", "", text))
    patterns = [
        re.compile(r"^(?P<prefix>By|From)\s+(?P<month>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<year>\d{4})[:,]?\s*(?P<rest>.*)$", re.I),
        re.compile(r"^(?P<prefix>By|From)\s+(?P<season>Spring|Summer|Autumn|Fall|Winter)\s+(?P<year>\d{4})[:,]?\s*(?P<rest>.*)$", re.I),
        re.compile(r"^(?P<season>Spring|Summer|Autumn|Fall|Winter)\s+(?P<year>\d{4})[:,]?\s*(?P<rest>.*)$", re.I),
        re.compile(r"^(?P<prefix>By)\s+(?:the\s+)?end\s+Q(?P<quarter>[1-4])\s+(?P<fy_start>\d{4})/(?P<fy_end>\d{4})[:,]?\s*(?P<rest>.*)$", re.I),
        re.compile(r"^(?P<prefix>By)\s+(?:the\s+)?end\s+of\s+(?P<year>\d{4})[:,]?\s*(?P<rest>.*)$", re.I),
        re.compile(r"^(?P<prefix>By)\s+end\s+(?P<year>\d{4})[:,]?\s*(?P<rest>.*)$", re.I),
        re.compile(r"^(?P<prefix>By)\s+(?P<year>\d{4})[:,]?\s*(?P<rest>.*)$", re.I),
    ]
    for pattern in patterns:
        match = pattern.match(text)
        if not match:
            continue
        groups = match.groupdict()
        prefix = (groups.get("prefix") or "By").lower()
        if groups.get("month"):
            month = MONTHS[groups["month"].lower()]
            year = int(groups["year"])
            day = 1 if prefix == "from" else calendar.monthrange(year, month)[1]
            due_date = dt.date(year, month, day)
        elif groups.get("season"):
            year = int(groups["year"])
            month, day = SEASON_DATES[groups["season"].lower()]
            due_date = dt.date(year, month, day)
        elif groups.get("quarter"):
            quarter = int(groups["quarter"])
            fy_start = int(groups["fy_start"])
            month = quarter * 3
            year = fy_start if quarter < 4 else int(groups["fy_end"])
            day = calendar.monthrange(year, month)[1]
            due_date = dt.date(year, month, day)
        else:
            year = int(groups["year"])
            due_date = dt.date(year, 12, 31)
        rest = clean_line(groups.get("rest") or text)
        return {
            "due_label": clean_line(match.group(0).replace(rest, "").strip(" :")),
            "due_date": due_date.isoformat(),
            "title": clean_line(rest) or text,
        }
    return None


def build_milestones(lines: list[str], source: str) -> tuple[list[dict[str, object]], list[str]]:
    milestones = []
    undated_metrics = []
    for line in dedupe_strings(lines):
        due = parse_due_phrase(line)
        if not due:
            undated_metrics.append(line)
            continue
        milestones.append(
            {
                "id": slugify(f"{source}-{due['title']}-{due['due_date']}"),
                "title": due["title"],
                "text": line,
                "due_label": due["due_label"],
                "due_date": due["due_date"],
                "deadline_type": "explicit",
                "source": source,
            }
        )
    return milestones, undated_metrics


def normalize_action_id(raw_number: str) -> str:
    value = raw_number.lower().replace(" ", "")
    value = value.replace(".", "")
    return value


def build_action_record(
    action_id: str,
    display_number: str,
    pillar: dict[str, str],
    title_text: str,
    metrics_text: str,
    sro_text: str,
) -> dict[str, object]:
    territory, action_text = extract_territory_and_text(title_text)
    lead_role, lead_body = split_sro_text(sro_text)
    metric_lines = [line for line in metrics_text.splitlines() if line]
    milestones, undated_metrics = build_milestones(metric_lines, "annex_metric")
    return {
        "id": action_id,
        "display_number": display_number,
        "pillar_id": pillar["id"],
        "pillar_title": pillar["title"],
        "title": ACTION_TITLE_OVERRIDES.get(action_id, clean_line(action_text.rstrip("."))),
        "action_text": clean_line(action_text),
        "territory": territory,
        "lead_official_role": lead_role,
        "lead_body": lead_body,
        "metrics_text": metrics_text,
        "milestones": milestones,
        "undated_metrics": undated_metrics,
    }


def parse_annex_tables(document: str) -> list[dict[str, object]]:
    start = document.index('<h4 id="pillar-1')
    end = document.index('<h3 id="footnotes">')
    segment = document[start:end]
    table_pattern = re.compile(
        r'<h4 id="(?P<html_id>pillar-[^"]+)">(?P<title>.*?)</h4>\s*<table>(?P<table>.*?)</table>',
        re.S,
    )
    rows: list[dict[str, object]] = []
    for match in table_pattern.finditer(segment):
        pillar = infer_pillar(match.group("html_id"))
        table_html = match.group("table")
        row_pattern = re.compile(r"<tr>(?P<row>.*?)</tr>", re.S)
        cell_pattern = re.compile(r"<t[dh][^>]*>(?P<cell>.*?)</t[dh]>", re.S)
        for row_match in row_pattern.finditer(table_html):
            cells = [html_to_text(cell) for cell in cell_pattern.findall(row_match.group("row"))]
            if len(cells) != 4 or cells[0].lower().startswith("action"):
                continue
            raw_number, title_text, metrics_text, sro_text = cells
            raw_number = clean_line(raw_number)
            if raw_number == "2":
                all_metrics = [line for line in metrics_text.splitlines() if line]
                split_records = [
                    (
                        "2a",
                        "2a",
                        "Establish pre-clinical translational infrastructure and translational networks.",
                        "\n".join(
                            line
                            for line in all_metrics
                            if "alternative methods strategy" not in line.lower()
                        ),
                        "Executive Chair, Medical Research Council",
                    ),
                    (
                        "2b",
                        "2b",
                        "Publish a strategy to support the development, validation, and uptake of alternative methods.",
                        "\n".join(
                            line
                            for line in all_metrics
                            if "alternative methods strategy" in line.lower()
                        ),
                        "Director, Office for Life Sciences",
                    ),
                ]
                for action_id, display_number, split_title, split_metrics, split_sro in split_records:
                    rows.append(
                        build_action_record(
                            action_id=action_id,
                            display_number=display_number,
                            pillar=pillar,
                            title_text=split_title,
                            metrics_text=split_metrics,
                            sro_text=split_sro,
                        )
                    )
                continue
            action_id = normalize_action_id(raw_number)
            rows.append(
                build_action_record(
                    action_id=action_id,
                    display_number=raw_number,
                    pillar=pillar,
                    title_text=title_text,
                    metrics_text=metrics_text,
                    sro_text=sro_text,
                )
            )
    return rows


def extract_roadmap_items(document: str) -> list[dict[str, object]]:
    start = document.index('<h3 id="plan-through-to-2035">')
    end = document.index('{;#annex-a}', start)
    segment = document[start:end]
    chunks = segment.split("<h4")
    items: list[dict[str, object]] = []
    for chunk in chunks[1:]:
        block = "<h4" + chunk
        if "</h4>" not in block:
            continue
        heading_html, body = block.split("</h4>", 1)
        year_label = html_to_text(heading_html + "</h4>")
        for part in re.findall(r"<li>(.*?)</li>|<p>(.*?)</p>", body, flags=re.S):
            fragment = next((entry for entry in part if entry), "")
            if not fragment:
                continue
            text = html_to_text(fragment)
            if not text or text.startswith("Plan through") or text.startswith("The BBB will begin publishing"):
                continue
            if text == "The BBB will begin publishing VC investment return data.":
                text = "By end Q4 2026/2027: The BBB will begin publishing VC investment return data."
            due = parse_due_phrase(text)
            if not due:
                continue
            lowered = clean_line(text).lower()
            action_id = next((candidate for needle, candidate in ROADMAP_MATCHERS if needle in lowered), None)
            if not action_id:
                continue
            items.append(
                {
                    "id": slugify(f"roadmap-{due['title']}-{due['due_date']}"),
                    "action_id": action_id,
                    "year_label": year_label,
                    "title": due["title"],
                    "text": text,
                    "due_label": due["due_label"],
                    "due_date": due["due_date"],
                    "deadline_type": "explicit",
                    "source": "roadmap",
                }
            )
    return items


def dedupe_milestones(milestones: list[dict[str, object]]) -> list[dict[str, object]]:
    seen = set()
    result = []
    for milestone in milestones:
        key = (
            milestone["due_date"],
            slugify(str(milestone["title"])),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(milestone)
    return sorted(result, key=lambda item: (item["due_date"], item["title"]))


def merge_roadmap(actions: list[dict[str, object]], roadmap_items: list[dict[str, object]]) -> None:
    by_id = {action["id"]: action for action in actions}
    for item in roadmap_items:
        action = by_id.get(item["action_id"])
        if not action:
            continue
        action["milestones"].append(
            {
                "id": item["id"],
                "title": item["title"],
                "text": item["text"],
                "due_label": item["due_label"],
                "due_date": item["due_date"],
                "deadline_type": item["deadline_type"],
                "source": item["source"],
            }
        )
    for action in actions:
        action["milestones"] = dedupe_milestones(action["milestones"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract the Life Sciences Sector Plan action register.")
    parser.add_argument("--force-fetch", action="store_true", help="Refresh the cached plan HTML before parsing.")
    args = parser.parse_args()

    document = ensure_plan_html(force=args.force_fetch)
    actions = parse_annex_tables(document)
    roadmap_items = extract_roadmap_items(document)
    merge_roadmap(actions, roadmap_items)

    PLAN_REGISTER_PATH.write_text(
        json.dumps(
            {
                "meta": {
                    "generated_at": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
                    "source_url": PLAN_URL,
                    "plan_launch_date": "2025-07-16",
                    "roadmap_items": len(roadmap_items),
                    "action_count": len(actions),
                },
                "actions": actions,
                "roadmap": roadmap_items,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
