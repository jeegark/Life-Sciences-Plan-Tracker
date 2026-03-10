# Life Sciences Sector Plan Tracker MVP Spec

## Product Frame
This MVP is a public microsite designed to monitor delivery of the UK Life Sciences Sector Plan and strengthen external advocacy. It should feel institutionally credible, visually adjacent to ABPI, and clearly grounded in public evidence rather than campaign rhetoric alone.

The tracker should:
- Cover the full plan and all actions.
- Organize content around the plan's three strategic pillars.
- Show named lead bodies, supporting bodies, and the current responsible minister.
- Track explicit milestones, inferred milestones, and actions too vague to track.
- Publish three live cost-of-delay counters from 16 July 2025 onward.
- Provide pressure tools for MPs, media, and sector audiences.

The tracker should not:
- Depend on private member-company data for core scoring.
- Require user sign-in.
- Collect personal data beyond an optional postcode lookup for MP matching.

## Source Anchors
- Plan basis: [Life Sciences Sector Plan](https://www.gov.uk/government/publications/life-sciences-sector-plan/life-sciences-sector-plan)
- Brand reference: [ABPI](https://www.abpi.org.uk/)

The plan structure this MVP should reflect:
- Three strategic pillars.
- Four headline targets.
- Six headline actions.
- Annual implementation update promise.
- Six-monthly Life Sciences Council review promise.

## MVP Outcome
The homepage should make one argument fast:

> Government delay is harming patients, costing the NHS, and putting investment at risk.

The user should be able to answer, within two minutes:
- Is the government delivering this plan?
- Which bodies are falling behind?
- What is the estimated cost of delay so far?
- What can I send to my MP or use in media now?

## Information Architecture
### 1. Homepage
Primary modules:
- Hero with single message and review date.
- Overall delivery score.
- Three live counters:
  - People affected
  - Avoidable NHS spend
  - Investment lost or deferred
- Status summary across all actions and milestones.
- Latest missed deadlines.
- Worst-performing delivery bodies.
- Pillar scorecards.
- Latest weekly summary.
- Briefing download hub.
- Methodology and disclaimer preview.

### 2. Pillar Pages
One page for each pillar:
- Enabling world-class research and development
- Making the UK an outstanding place to start, scale, and invest
- Driving health innovation and NHS reform

Each pillar page should show:
- Pillar summary and score
- Action list
- Delayed and at-risk actions first
- Counter contribution estimate
- Evidence highlights

### 3. Action Detail Pages
Each action page should include:
- Original plan text
- Action summary
- Lead body
- Supporting bodies
- Current minister
- Milestone list with due dates and statuses
- Evidence tab
- Claim made, evidence not published label where needed
- Consequence of delay
- Share tools
- MP briefing download

### 4. Methodology Page
Should explain:
- Scoring rules
- Status rules
- Cost-of-delay formulas
- Range assumptions
- Proxy treatment for vague commitments
- Evidence and review rules

### 5. Weekly Summary Archive
Each weekly note should include:
- What changed this week
- New evidence published
- Deadlines missed
- Bodies added to watchlist

### 6. Briefings Hub
Tailored downloads for:
- MPs
- Journalists
- Member companies
- Patient groups

## Homepage Modules in the MVP
### Hero
- Neutral title such as `Life Sciences Sector Plan Tracker`
- Publication baseline: 16 July 2025
- Last evidence review date
- Plain-language disclaimer that judgments rely on public evidence

### Counters
Display three separate cards, each with:
- Central estimate to date
- Daily increase
- Range available in methodology

### Latest Missed Deadlines
Table or stacked cards:
- Milestone
- Due date
- Lead body
- Current minister
- Current status
- Days late

### Worst-Performing Bodies
Rank by number of delayed actions. For each body show:
- Delayed actions count
- Total tracked actions
- Current minister
- Evidence freshness

### Pillar Scorecards
Per pillar:
- Delivery score
- Delayed actions count
- Top blocked action
- Estimated counter contribution

## Data Model
The MVP should build a single generated JSON payload for the frontend. The pipeline can store richer source files internally, but the browser should receive one normalized bundle.

### Root Shape
```json
{
  "meta": {},
  "score": {},
  "counters": {},
  "status_summary": {},
  "pillars": [],
  "actions": [],
  "latest_missed_deadlines": [],
  "body_rankings": [],
  "weekly_summary": {},
  "briefings": []
}
```

### `meta`
Required fields:
- `title`
- `launch_date`
- `last_updated`
- `review_date`
- `source_urls[]`
- `homepage_message`
- `evidence_disclaimer`
- `methodology_version`

### `pillars[]`
Required fields:
- `id`
- `title`
- `summary`
- `score`
- `tracked_actions`
- `delayed_actions`
- `estimated_counter_contribution`
- `hero_action_id`

### `actions[]`
Required fields:
- `id`
- `pillar_id`
- `title`
- `summary`
- `original_text`
- `status`
- `lead_body_id`
- `support_body_ids[]`
- `current_minister`
- `score`
- `deadline_type`
- `review_confidence`
- `claim_without_evidence`
- `impact_profile`
- `milestones[]`
- `evidence[]`
- `status_history[]`

### `impact_profile`
Required fields:
- `patients_per_year`
- `nhs_avoidable_spend_per_year_gbp`
- `investment_per_year_gbp`
- `range_low`
- `range_high`
- `confidence_weight`
- `proxy_used`
- `notes`

### `milestones[]`
Required fields:
- `id`
- `title`
- `due_date`
- `status`
- `deadline_type`
- `weight`
- `benefit_share`
- `completed_date`
- `days_late`
- `review_note`

`deadline_type` values:
- `explicit`
- `inferred`
- `proxy`

### `evidence[]`
Required fields:
- `id`
- `title`
- `source_org`
- `published_at`
- `url`
- `evidence_type`
- `summary`

`evidence_type` values:
- `official_update`
- `minister_statement`
- `consultation`
- `guidance`
- `implementation_update`
- `select_committee`
- `arms_length_body_update`
- `parliamentary_answer`

### `status_history[]`
Required fields:
- `date`
- `status`
- `reason`
- `evidence_ids[]`

### `body_rankings[]`
Required fields:
- `body_id`
- `name`
- `type`
- `delayed_actions`
- `tracked_actions`
- `current_minister`
- `freshness_days`

## Status Rules
Use a public-facing status model with explicit criteria.

### `Completed`
Use when:
- Public evidence confirms the milestone or action has been delivered.

### `On track`
Use when all are true:
- The due date has not passed.
- Available evidence shows progress consistent with the planned path.
- No material blocker is visible from public evidence.

### `At risk`
Use when any are true:
- The due date is within 60 days and required outputs are not yet visible.
- Dependencies are unresolved.
- Delivery claims exist but evidence remains thin.

### `Delayed`
Use when:
- The due date has passed and there is no public evidence of delivery.

### `Late but in progress`
Use when:
- The due date has passed.
- Public evidence shows restart, partial implementation, or active remediation.
- The milestone is still not complete.

### `Too vague to track`
Use when:
- The plan text does not provide a measurable output, usable date, or accountable delivery point even after best-efforts normalization.

### `Claim made, evidence not published`
This is a transparency flag, not a standalone delivery status. Apply it when:
- A minister or body claims progress.
- No public document, dataset, or implementation notice verifies that claim.

## Scoring Model
The public score should be simple enough to defend in media.

### Milestone weights
- `Completed`: 1.00
- `On track`: 0.75
- `At risk`: 0.40
- `Late but in progress`: 0.20
- `Delayed`: 0.00
- `Too vague to track`: excluded from the measurable denominator

### Transparency penalty
Subtract from the overall score:
- `2` points for each action flagged `claim made, evidence not published`
- `1` point for each action marked `too vague to track`
- Cap total penalty at `15`

### Score formula
```text
Execution score = 100 * weighted measurable milestone points / weighted measurable milestone total
Overall score = max(0, Execution score - transparency penalty)
```

Use the same formula at:
- Whole-plan level
- Pillar level
- Delivery-body level

## Cost-of-Delay Methodology
The ticker should be a model of unrealized public and economic benefit caused by slower-than-promised delivery from the plan launch date.

### Core principle
The counters measure the gap between:
- the benefit that should have been progressively unlocked if the plan began delivering from launch on its own timetable
- and the benefit actually evidenced as unlocked in public

This avoids waiting until a deadline is formally missed before any cost appears.

### Required impact estimate per action
For each action, estimate:
- Annual people affected if delivered
- Annual avoidable NHS spend if delivered
- Annual investment gained if delivered
- Low and high variants
- Confidence weight

### Planned progress curve
For each milestone:
```text
planned_share(t) = milestone benefit share * min(max((t - launch_date) / (due_date - launch_date), 0), 1)
```

This means benefit is expected to ramp in from launch toward the milestone date, not appear instantaneously on the deadline.

### Actual progress curve
For MVP purposes:
- `Completed`: 100% of the milestone share unlocks from the confirmed completion date.
- `Late but in progress`: 35% of the share unlocks once public evidence shows partial delivery.
- `On track` and `At risk`: 0% unlock until a concrete public output exists.
- `Delayed`: 0%
- `Too vague to track`: use proxy logic below.

This is conservative because it requires tangible evidence before value is treated as realized.

### Daily loss formula
For each metric `m` on day `t`:
```text
daily_loss_m(t) = sum over milestones(
  annual_benefit_m / 365
  * max(planned_share(t) - actual_share(t), 0)
  * confidence_weight
)
```

### Counter total
```text
counter_m(today) = sum of daily_loss_m from 16 July 2025 through review date
```

### Proxy handling for vague commitments
For actions marked `Too vague to track`:
- Assign a proxy due date based on adjacent explicit commitments in the same pillar.
- Assign impact values using the lower quartile of comparable actions in that pillar.
- Set `proxy_used = true`.
- Apply a lower `confidence_weight`, default `0.35`.

These items should contribute to the counters but remain visibly labeled as proxies.

### Range presentation
Frontend:
- Show central estimate only in the live ticker.

Methodology page:
- Show low, central, and high estimates.
- Explain assumptions and confidence weights.

## Evidence and Review Rules
- Public sources only for scoring and counters.
- Review cadence: weekly.
- Every status change requires:
  - a review date
  - a reason
  - at least one evidence link or a note that evidence is absent
- If official sources conflict, the more conservative interpretation should be used until clarified.

## Weekly Summary Rules
Each weekly summary should include:
- Total score movement since previous week
- Newly missed deadlines
- New claims without evidence
- Bodies entering or leaving the top delay table
- Counter movement over the week

## Briefing Rules
Each generated briefing should include:
- Audience type
- Review date
- Top three delayed items
- Latest counter snapshot
- Source note
- Tailored framing

Audience framing:
- `MP`: constituency and accountability angle
- `Journalist`: headline stats and missed deadlines
- `Member company`: sector and investment implications
- `Patient group`: access and health impact angle

## Technical Architecture
Use a static frontend plus generated JSON. This matches the existing repo structure and keeps hosting simple.

### Frontend
- Plain `HTML`, `CSS`, and `JavaScript`
- One generated payload for homepage modules
- Additional per-action JSON files in phase two

### Build pipeline
Suggested scripts:
- `scripts/extract_plan.py`: parse and normalize plan actions and milestones
- `scripts/fetch_evidence.py`: collect public updates, statements, and implementation notes
- `scripts/fetch_ministers.py`: refresh current minister ownership
- `scripts/build_tracker.py`: compute statuses, scores, counters, and frontend JSON
- `scripts/build_briefings.py`: generate per-audience downloads

### Generated outputs
- `data/tracker.json`
- `data/actions/<action-id>.json`
- `data/briefings/<audience>.json`
- `data/weekly/<yyyy-mm-dd>.json`

## Starter File Structure
```text
life-sciences-tracker/
  README.md
  MVP_SPEC.md
  index.html
  styles.css
  app.js
  data/
    tracker.sample.json
```

## MVP Build Sequence
1. Extract the full action register from the plan into normalized JSON.
2. Confirm every explicit date and assign inferred or proxy dates where needed.
3. Create the first evidence pass from GOV.UK, arm's-length bodies, NHS, and Parliament sources.
4. Score all milestones and bodies.
5. Implement the live counters from the action impact profiles.
6. Add MP postcode lookup and tailored briefing downloads.

## Open Issues for Build Phase
- Final host and deployment path
- Public source coverage limits for minister and body refreshes
- Choice of postcode-to-MP resolver
- Exact wording for public disclaimer and legal review
