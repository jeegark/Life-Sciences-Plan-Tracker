#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import pathlib
import re
from collections import Counter, defaultdict
from urllib.parse import urlparse


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PLAN_REGISTER_PATH = DATA_DIR / "plan_register.json"
EVIDENCE_PATH = DATA_DIR / "evidence.json"
TRACKER_PATH = DATA_DIR / "tracker.json"

PLAN_URL = "https://www.gov.uk/government/publications/life-sciences-sector-plan/life-sciences-sector-plan"
ABPI_URL = "https://www.abpi.org.uk/"

STATUS_WEIGHTS = {
    "Completed": 1.0,
    "On track": 0.75,
    "At risk": 0.4,
    "Late but in progress": 0.2,
    "Delayed": 0.0,
}

MINISTER_ROLE_LABELS = {
    "science": "Minister of State (Minister for Science, Innovation, Research and Nuclear)",
    "health_innovation": "Parliamentary Under-Secretary of State for Health Innovation and Safety",
    "investment": "Minister of State (Minister for Investment)",
    "skills": "Minister of State (Minister for Skills)",
}

BRIEFINGS = [
    {
        "audience": "MP",
        "title": "Constituency pressure briefing",
        "description": "Draft pack for postcode-matched MP outreach, with local framing and the latest missed deadlines.",
        "href": "#",
        "cta": "Open MP pack",
    },
    {
        "audience": "Journalist",
        "title": "Media stats sheet",
        "description": "Fast summary of missed deadlines, accountability gaps, and current cost-of-delay counters.",
        "href": "#",
        "cta": "Open media view",
    },
    {
        "audience": "Member company",
        "title": "Sector impact note",
        "description": "Shorter sector-facing note for meetings, submissions, and coalition work.",
        "href": "#",
        "cta": "Open company note",
    },
    {
        "audience": "Patient group",
        "title": "Patient access note",
        "description": "Plain-language note on what delivery delays mean for patients and the NHS.",
        "href": "#",
        "cta": "Open patient note",
    },
]

SOURCE_ORGS_BY_HOST = {
    "www.gov.uk": "GOV.UK",
    "www.england.nhs.uk": "NHS England",
    "www.nice.org.uk": "NICE",
    "www.ukri.org": "UKRI",
    "www.british-business-bank.co.uk": "British Business Bank",
    "www.ukbiobank.ac.uk": "UK Biobank",
    "ourfuturehealth.org.uk": "Our Future Health",
    "www.genomicsengland.co.uk": "Genomics England",
    "www.nihr.ac.uk": "NIHR",
    "www.spcr.nihr.ac.uk": "NIHR",
    "bioresource.nihr.ac.uk": "NIHR",
    "io.nihr.ac.uk": "NIHR",
}


def parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value[:10])


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def clean_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def source_org(source: dict[str, object]) -> str:
    explicit = source.get("source_org")
    if explicit:
        return str(explicit)
    host = urlparse(str(source["url"])).netloc
    return SOURCE_ORGS_BY_HOST.get(host, host or "Official source")


def source_title(source: dict[str, object]) -> str:
    title = str(source.get("title") or "").strip()
    lowered = title.lower()
    if not title or "page not found" in lowered or "just a moment" in lowered:
        return str(source["label"])
    return title


def source_summary(source: dict[str, object]) -> str:
    summary = str(source.get("summary") or "").strip()
    lowered = summary.lower()
    if not summary or lowered.startswith("change my preferences") or lowered.startswith("if you typed the web address"):
        return str(source["label"])
    return summary


def build_accountability_actions(review_date: dt.date) -> list[dict[str, object]]:
    launch = dt.date(2025, 7, 16)
    return [
        {
            "id": "accountability-annual-update",
            "display_number": "A1",
            "pillar_id": "accountability",
            "pillar_title": "Accountability",
            "title": "Publish the annual Sector Plan implementation update",
            "action_text": "Government committed to publish an annual implementation update covering the whole plan.",
            "territory": "UK",
            "lead_official_role": "Director",
            "lead_body": "Office for Life Sciences",
            "metrics_text": "By 2026, publish the annual Sector Plan implementation update.",
            "undated_metrics": [],
            "milestones": [
                {
                    "id": "accountability-annual-update-2026",
                    "title": "Publish the annual implementation update",
                    "text": "By 2026, publish the annual Sector Plan implementation update.",
                    "due_label": "By 2026",
                    "due_date": dt.date(2026, 7, 16).isoformat(),
                    "deadline_type": "explicit",
                    "source": "plan_text",
                }
            ],
        },
        {
            "id": "accountability-council-review",
            "display_number": "A2",
            "pillar_id": "accountability",
            "pillar_title": "Accountability",
            "title": "Report progress to the Life Sciences Council every 6 months",
            "action_text": "The ministerially chaired Life Sciences Delivery Board committed to report on a 6-monthly basis to the Life Sciences Council.",
            "territory": "UK",
            "lead_official_role": "Director",
            "lead_body": "Office for Life Sciences",
            "metrics_text": "By January 2026, report progress to the Life Sciences Council and continue 6-monthly thereafter.",
            "undated_metrics": [],
            "milestones": [
                {
                    "id": "accountability-council-review-2026-01",
                    "title": "First 6-monthly Life Sciences Council delivery report",
                    "text": "By January 2026, report progress to the Life Sciences Council.",
                    "due_label": "By January 2026",
                    "due_date": dt.date(2026, 1, 16).isoformat(),
                    "deadline_type": "explicit",
                    "source": "plan_text",
                }
            ],
        },
    ]


def assign_minister_role(action_id: str, pillar_id: str, lead_body: str) -> str:
    if action_id in {"3", "4", "6", "7", "8", "9iv", "11ii", "12", "21", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "accountability-annual-update", "accountability-council-review"}:
        return "health_innovation"
    if action_id in {"16", "17"}:
        return "skills"
    if pillar_id == "invest":
        return "investment"
    if lead_body in {"Department of Health and Social Care", "NHS England"}:
        return "health_innovation"
    return "science"


def impact_profile_for_action(action: dict[str, object]) -> dict[str, object]:
    text = f"{action['title']} {action['action_text']}".lower()
    if "trial" in text:
        patients, nhs, investment, confidence = 32000, 18000000, 175000000, 0.8
    elif "data" in text or "genom" in text:
        patients, nhs, investment, confidence = 18000, 11000000, 130000000, 0.7
    elif "manufacturing" in text:
        patients, nhs, investment, confidence = 7000, 4500000, 240000000, 0.65
    elif "regulator" in text or "mhra" in text or "nice" in text or "market entry" in text:
        patients, nhs, investment, confidence = 26000, 23000000, 125000000, 0.72
    elif "talent" in text or "skill" in text:
        patients, nhs, investment, confidence = 3500, 1500000, 45000000, 0.45
    elif "capital" in text or "investment" in text or "partnership" in text or "scale" in text or "export" in text:
        patients, nhs, investment, confidence = 4500, 2000000, 210000000, 0.55
    elif "uptake" in text or "procurement" in text or "innovation scorecard" in text or "passport" in text:
        patients, nhs, investment, confidence = 42000, 52000000, 70000000, 0.7
    else:
        patients, nhs, investment, confidence = 6000, 4000000, 60000000, 0.4

    if action["id"] in {"3", "7", "19", "25", "27", "29"}:
        patients = int(patients * 1.35)
        nhs = int(nhs * 1.35)
        investment = int(investment * 1.35)
    return {
        "patients_per_year": patients,
        "nhs_avoidable_spend_per_year_gbp": nhs,
        "investment_per_year_gbp": investment,
        "range_low": 0.65,
        "range_high": 1.35,
        "confidence_weight": confidence,
        "proxy_used": False,
        "notes": "Heuristic alpha profile based on action type pending a calibrated economic model.",
    }


def fallback_proxy_due_date(action: dict[str, object]) -> str:
    text = f"{action['title']} {action['metrics_text']}".lower()
    if "2030" in text:
        return "2030-12-31"
    if action["pillar_id"] == "invest":
        return "2027-03-31"
    return "2026-12-31"


def load_inputs() -> tuple[list[dict[str, object]], dict[str, object]]:
    plan_register = json.loads(PLAN_REGISTER_PATH.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    actions = plan_register["actions"]
    return actions, evidence


def evidence_index(evidence: dict[str, object], review_date: dt.date) -> tuple[dict[str, list[dict[str, object]]], dict[str, dict[str, object]]]:
    by_action: dict[str, list[dict[str, object]]] = defaultdict(list)
    for source in evidence["sources"]:
        if not source.get("ok"):
            continue
        published_at = source.get("published_at")
        if published_at and parse_date(published_at) > review_date:
            continue
        for action_id in source["action_ids"]:
            if action_id == "all":
                continue
            by_action[action_id].append(source)
    ministers = {
        item["id"]: item
        for item in evidence["ministers"]
        if item.get("ok") and item.get("current_holder")
    }
    return by_action, ministers


def apply_evidence(action: dict[str, object], action_evidence: list[dict[str, object]], review_date: dt.date) -> list[dict[str, object]]:
    processed = []
    for raw in action["milestones"]:
        milestone = dict(raw)
        milestone.setdefault("completed_date", None)
        milestone.setdefault("progress_date", None)
        for evidence_item in action_evidence:
            keywords = [keyword.lower() for keyword in evidence_item.get("milestone_keywords", [])]
            milestone_text = f"{milestone['title']} {milestone['text']}".lower()
            if keywords and not any(keyword in milestone_text for keyword in keywords):
                continue
            published_at = evidence_item.get("published_at")
            if not published_at:
                continue
            published_date = parse_date(published_at)
            if evidence_item.get("effect") == "complete":
                existing = milestone.get("completed_date")
                if existing is None or published_date < parse_date(existing):
                    milestone["completed_date"] = published_date.isoformat()
            if evidence_item.get("effect") == "progress":
                existing = milestone.get("progress_date")
                if existing is None or published_date < parse_date(existing):
                    milestone["progress_date"] = published_date.isoformat()
        processed.append(milestone)
    if not processed:
        proxy_due = fallback_proxy_due_date(action)
        processed.append(
            {
                "id": slugify(f"{action['id']}-proxy"),
                "title": action["title"],
                "text": action["title"],
                "due_label": "Proxy milestone",
                "due_date": proxy_due,
                "deadline_type": "proxy",
                "source": "build_proxy",
                "completed_date": None,
                "progress_date": None,
            }
        )
        action["impact_profile"]["proxy_used"] = True
        action["impact_profile"]["confidence_weight"] = min(action["impact_profile"]["confidence_weight"], 0.35)
    return processed


def milestone_status(milestone: dict[str, object], review_date: dt.date) -> tuple[str, int]:
    due_date = parse_date(milestone["due_date"])
    completed_date = parse_date(milestone["completed_date"]) if milestone.get("completed_date") else None
    progress_date = parse_date(milestone["progress_date"]) if milestone.get("progress_date") else None
    if completed_date and completed_date <= review_date:
        delay = max((completed_date - due_date).days, 0)
        return "Completed", delay
    if due_date < review_date:
        delay = (review_date - due_date).days
        if progress_date:
            return "Late but in progress", delay
        return "Delayed", delay
    if due_date <= review_date + dt.timedelta(days=60):
        return "At risk", 0
    return "On track", 0


def action_status(milestones: list[dict[str, object]]) -> str:
    statuses = [milestone["status"] for milestone in milestones]
    if all(status == "Completed" for status in statuses):
        return "Completed"
    if any(status == "Delayed" for status in statuses):
        if any(status in {"Late but in progress", "Completed"} for status in statuses):
            return "Late but in progress"
        return "Delayed"
    if any(status == "Late but in progress" for status in statuses):
        return "Late but in progress"
    if any(status == "At risk" for status in statuses):
        return "At risk"
    return "On track"


def score_action(milestones: list[dict[str, object]]) -> int:
    total = sum(STATUS_WEIGHTS.get(milestone["status"], 0) for milestone in milestones)
    if not milestones:
        return 0
    return int(round(100 * total / len(milestones)))


def status_history_entry(status: str, reason: str, evidence_items: list[dict[str, object]], review_date: dt.date) -> dict[str, object]:
    return {
        "date": review_date.isoformat(),
        "status": status,
        "reason": reason,
        "evidence_ids": [item["id"] for item in evidence_items if item.get("ok")],
    }


def compute_counter(actions: list[dict[str, object]], review_date: dt.date, metric_key: str) -> tuple[int, int]:
    launch_date = dt.date(2025, 7, 16)
    total = 0.0
    daily = 0.0
    for action in actions:
        annual_benefit = action["impact_profile"][metric_key]
        confidence = action["impact_profile"]["confidence_weight"]
        for milestone in action["milestones"]:
            due_date = parse_date(milestone["due_date"])
            if due_date <= launch_date:
                continue
            benefit_share = milestone["benefit_share"]
            span = max((due_date - launch_date).days, 1)
            elapsed = max(min((review_date - launch_date).days, span), 0)
            planned_share = benefit_share * (elapsed / span)
            actual_share = 0.0
            if milestone.get("completed_date"):
                completed_date = parse_date(milestone["completed_date"])
                if completed_date <= review_date:
                    actual_share = benefit_share
            elif milestone.get("progress_date") and parse_date(milestone["progress_date"]) <= review_date:
                actual_share = benefit_share * 0.35
            gap = max(planned_share - actual_share, 0.0)
            total += annual_benefit * gap * confidence * ((review_date - launch_date).days / 365)
            daily += (annual_benefit / 365) * gap * confidence
    return int(round(total)), int(round(daily))


def build_weekly_summary(actions: list[dict[str, object]], latest_missed: list[dict[str, object]], review_date: dt.date) -> dict[str, object]:
    delayed = sum(1 for action in actions if action["status"] == "Delayed")
    at_risk = sum(1 for action in actions if action["status"] == "At risk")
    items = []
    if latest_missed:
        items.append(f"Most overdue item: {latest_missed[0]['title']} ({latest_missed[0]['days_late']} days late).")
    items.append(f"{delayed} actions are currently delayed.")
    items.append(f"{at_risk} actions are at risk in the next 60 days.")
    return {
        "review_date": review_date.isoformat(),
        "headline": "Government delivery remains off pace across the plan, with accountability, regulation, and NHS adoption still the main pressure points.",
        "items": items,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build tracker.json from the plan register and evidence cache.")
    parser.add_argument("--review-date", default="2026-03-10", help="Review date in ISO format.")
    args = parser.parse_args()

    review_date = parse_date(args.review_date)
    actions, evidence = load_inputs()
    actions.extend(build_accountability_actions(review_date))
    evidence_by_action, ministers = evidence_index(evidence, review_date)

    processed_actions = []
    for raw_action in actions:
        action = dict(raw_action)
        action["impact_profile"] = impact_profile_for_action(action)
        action["summary"] = action["action_text"]
        action["original_text"] = action["action_text"]
        role_id = assign_minister_role(action["id"], action["pillar_id"], action["lead_body"])
        minister = ministers.get(role_id, {})
        action["minister_role_id"] = role_id
        action["current_minister_role"] = MINISTER_ROLE_LABELS[role_id]
        action["current_minister"] = minister.get("current_holder", "Unknown")
        action["lead_body_id"] = slugify(str(action["lead_body"]))
        action["support_body_ids"] = []
        action_evidence = evidence_by_action.get(action["id"], [])
        action_evidence.sort(key=lambda item: item.get("published_at") or "", reverse=True)
        action["claim_without_evidence"] = any(item.get("effect") == "claim" for item in action_evidence)
        action["review_confidence"] = action["impact_profile"]["confidence_weight"]
        action["evidence"] = [
            {
                "id": item["id"],
                "title": source_title(item),
                "source_org": source_org(item),
                "published_at": item.get("published_at"),
                "url": item["url"],
                "evidence_type": item["evidence_type"],
                "effect": item.get("effect", "context"),
                "summary": source_summary(item),
            }
            for item in action_evidence
        ]

        milestones = apply_evidence(action, action_evidence, review_date)
        for milestone in milestones:
            milestone["benefit_share"] = round(1 / len(milestones), 4)
            status, days_late = milestone_status(milestone, review_date)
            milestone["status"] = status
            milestone["days_late"] = days_late
            milestone["weight"] = 1
            milestone["review_note"] = "Generated from the official plan, roadmap, and current public evidence cache."
        if raw_action["id"] not in {"accountability-annual-update", "accountability-council-review"} and not raw_action["milestones"] and raw_action["undated_metrics"]:
            action["status"] = "Too vague to track"
            action["score"] = 0
        else:
            action["status"] = action_status(milestones)
            action["score"] = score_action(milestones)
        if action["status"] == "Too vague to track":
            action["impact_profile"]["proxy_used"] = True
        action["milestones"] = milestones
        action["status_history"] = [
            status_history_entry(
                status=action["status"],
                reason=(
                    "Built from current due dates, official evidence linked in the tracker cache, "
                    "and published progress claims where the promised deliverable is still absent."
                    if action["claim_without_evidence"]
                    else "Built from current due dates and official evidence linked in the tracker cache."
                ),
                evidence_items=action_evidence,
                review_date=review_date,
            )
        ]
        processed_actions.append(action)

    status_counts = Counter(action["status"] for action in processed_actions)
    measurable_actions = [action for action in processed_actions if action["status"] != "Too vague to track"]
    execution_score = 0
    if measurable_actions:
        execution_score = int(round(sum(action["score"] for action in measurable_actions) / len(measurable_actions)))
    transparency_penalty = min(15, status_counts["Too vague to track"] + 2 * sum(1 for action in processed_actions if action["claim_without_evidence"]))
    overall_score = max(0, execution_score - transparency_penalty)

    latest_missed_by_key: dict[tuple[str, str], dict[str, object]] = {}
    for action in processed_actions:
        for milestone in action["milestones"]:
            if milestone["status"] not in {"Delayed", "Late but in progress"}:
                continue
            key = (action["id"], milestone["due_date"])
            candidate = {
                "title": milestone["title"],
                "due_date": milestone["due_date"],
                "status": milestone["status"],
                "lead_body": action["lead_body"],
                "current_minister": action["current_minister"],
                "days_late": milestone["days_late"],
                "note": action["title"],
                "source": milestone["source"],
            }
            existing = latest_missed_by_key.get(key)
            if not existing:
                latest_missed_by_key[key] = candidate
                continue
            if candidate["source"] == "roadmap" and existing["source"] != "roadmap":
                latest_missed_by_key[key] = candidate
                continue
            if len(str(candidate["title"])) < len(str(existing["title"])):
                latest_missed_by_key[key] = candidate
    latest_missed_deadlines = list(latest_missed_by_key.values())
    for item in latest_missed_deadlines:
        item.pop("source", None)
    latest_missed_deadlines.sort(key=lambda item: (-item["days_late"], item["due_date"]))
    latest_missed_deadlines = latest_missed_deadlines[:8]

    body_buckets: dict[str, list[dict[str, object]]] = defaultdict(list)
    for action in processed_actions:
        body_buckets[action["lead_body"]].append(action)
    body_rankings = []
    for body, items in body_buckets.items():
        delayed_actions = sum(1 for item in items if item["status"] in {"Delayed", "Late but in progress"})
        body_rankings.append(
            {
                "body_id": slugify(body),
                "name": body,
                "type": "delivery body",
                "delayed_actions": delayed_actions,
                "tracked_actions": len(items),
                "current_minister": items[0]["current_minister"],
                "freshness_days": min(
                    (
                        (review_date - parse_date(evidence_item["published_at"])).days
                        for item in items
                        for evidence_item in item["evidence"]
                        if evidence_item.get("published_at")
                    ),
                    default=999,
                ),
            }
        )
    body_rankings.sort(key=lambda item: (-item["delayed_actions"], item["name"]))

    pillar_lookup = {
        "rd": "Enabling world-class research and development",
        "invest": "Making the UK an outstanding place to start, scale, and invest",
        "nhs": "Driving health innovation and NHS reform",
    }
    pillars = []
    for pillar_id, pillar_title in pillar_lookup.items():
        pillar_actions = [action for action in processed_actions if action["pillar_id"] == pillar_id]
        if not pillar_actions:
            continue
        delayed = [action for action in pillar_actions if action["status"] in {"Delayed", "Late but in progress"}]
        hero_action = max(
            pillar_actions,
            key=lambda action: action["impact_profile"]["patients_per_year"]
            + action["impact_profile"]["nhs_avoidable_spend_per_year_gbp"] / 1000000
            + action["impact_profile"]["investment_per_year_gbp"] / 1000000,
        )
        pillar_score = int(round(sum(action["score"] for action in pillar_actions) / len(pillar_actions)))
        pillars.append(
            {
                "id": pillar_id,
                "title": pillar_title,
                "summary": clean_text(
                    f"{len(delayed)} actions are currently delayed or running late in this pillar."
                ),
                "score": pillar_score,
                "tracked_actions": len(pillar_actions),
                "delayed_actions": len(delayed),
                "estimated_counter_contribution": "Major source of current delay impact",
                "hero_action_id": hero_action["id"],
                "hero_action_title": hero_action["title"],
            }
        )

    patients_total, patients_daily = compute_counter(processed_actions, review_date, "patients_per_year")
    nhs_total, nhs_daily = compute_counter(processed_actions, review_date, "nhs_avoidable_spend_per_year_gbp")
    investment_total, investment_daily = compute_counter(processed_actions, review_date, "investment_per_year_gbp")

    tracker = {
        "meta": {
            "title": "Life Sciences Sector Plan Tracker",
            "launch_date": "2025-07-16",
            "review_date": review_date.isoformat(),
            "last_updated": review_date.isoformat(),
            "source_urls": [
                PLAN_URL,
                ABPI_URL,
            ],
            "homepage_message": "Government delay is harming patients, costing the NHS, and putting investment at risk.",
            "evidence_disclaimer": "Status judgments are based on publicly available evidence as of the review date.",
            "methodology_version": "0.2-alpha",
        },
        "score": {
            "overall": overall_score,
            "execution": execution_score,
            "transparency_penalty": transparency_penalty,
        },
        "counters": {
            "patients": {
                "format": "integer",
                "central": patients_total,
                "min": math.floor(patients_total * 0.65),
                "max": math.ceil(patients_total * 1.35),
                "per_day": patients_daily,
            },
            "nhs": {
                "format": "currency",
                "central": nhs_total,
                "min": math.floor(nhs_total * 0.65),
                "max": math.ceil(nhs_total * 1.35),
                "per_day": nhs_daily,
            },
            "investment": {
                "format": "currency",
                "central": investment_total,
                "min": math.floor(investment_total * 0.65),
                "max": math.ceil(investment_total * 1.35),
                "per_day": investment_daily,
            },
        },
        "status_summary": {
            "Completed": status_counts["Completed"],
            "On track": status_counts["On track"],
            "At risk": status_counts["At risk"],
            "Delayed": status_counts["Delayed"],
            "Late but in progress": status_counts["Late but in progress"],
            "Too vague to track": status_counts["Too vague to track"],
        },
        "pillars": pillars,
        "actions": processed_actions,
        "latest_missed_deadlines": latest_missed_deadlines,
        "body_rankings": body_rankings[:10],
        "weekly_summary": build_weekly_summary(processed_actions, latest_missed_deadlines, review_date),
        "briefings": BRIEFINGS,
    }

    TRACKER_PATH.write_text(json.dumps(tracker, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
