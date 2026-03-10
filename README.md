# Life Sciences Sector Plan Tracker

Static microsite MVP for tracking delivery of the UK Life Sciences Sector Plan in a public, evidence-led scorecard format.

## Purpose
- Show where delivery is on track, at risk, delayed, or too vague to track.
- Quantify the estimated cost of delay for patients, the NHS, and investment.
- Give MPs, media, industry, and campaign users quick tools to apply pressure.

## Current Contents
- `MVP_SPEC.md`: product, data, methodology, and implementation spec.
- `index.html`: starter microsite shell wired to sample data.
- `styles.css`: ABPI-adjacent visual system for the MVP.
- `app.js`: simple renderer for the homepage modules.
- `data/tracker.sample.json`: sample content and schema shape for the build.
- `data/evidence_sources.json`: curated official-source manifest for the first evidence refresh.
- `scripts/extract_plan.py`: pulls the official GOV.UK HTML and builds the action register.
- `scripts/fetch_evidence.py`: refreshes official evidence and current minister role holders.
- `scripts/build_tracker.py`: combines the register and evidence cache into `data/tracker.json`.

## Local Preview
Run a local server from this folder so `fetch()` works:

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

## Suggested Next Build Steps
1. Convert the sample data file into the first full action register extracted from the plan.
2. Add build scripts to refresh evidence, minister ownership, and weekly summaries.
3. Split the single-page shell into pillar, action, briefing, and methodology routes.
4. Replace sample counters with computed values from the cost-of-delay model.

## Data Refresh
From this folder:

```bash
zsh scripts/refresh_raw.sh
python3 scripts/extract_plan.py
python3 scripts/fetch_evidence.py
python3 scripts/build_tracker.py --review-date 2026-03-10
```

`refresh_raw.sh` caches the official GOV.UK plan, evidence pages, and minister role pages under `data/raw/`.

The frontend will load `data/tracker.json` when present and fall back to `data/tracker.sample.json` otherwise.
