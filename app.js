const state = {
  data: null,
  filters: {
    search: "",
    pillar: "all",
    status: "all",
  },
  currentPillarId: null,
  currentActionId: null,
  detailTab: "overview",
  selectedAudience: "MP",
  selectedBriefingActionId: "top_delay",
  selectedMpActionId: "top_delay",
  mpLookup: {
    status: "idle",
    message: "",
    member: null,
  },
};

const elements = {
  pageTitle: document.getElementById("pageTitle"),
  homepageMessage: document.getElementById("homepageMessage"),
  launchDate: document.getElementById("launchDate"),
  reviewDate: document.getElementById("reviewDate"),
  overallScore: document.getElementById("overallScore"),
  scoreBreakdown: document.getElementById("scoreBreakdown"),
  evidenceDisclaimer: document.getElementById("evidenceDisclaimer"),
  patientsValue: document.getElementById("patientsValue"),
  patientsDelta: document.getElementById("patientsDelta"),
  nhsValue: document.getElementById("nhsValue"),
  nhsDelta: document.getElementById("nhsDelta"),
  investmentValue: document.getElementById("investmentValue"),
  investmentDelta: document.getElementById("investmentDelta"),
  statusSummary: document.getElementById("statusSummary"),
  evidenceHealth: document.getElementById("evidenceHealth"),
  evidenceHighlights: document.getElementById("evidenceHighlights"),
  weeklySummaryDate: document.getElementById("weeklySummaryDate"),
  weeklySummaryHeadline: document.getElementById("weeklySummaryHeadline"),
  weeklySummaryItems: document.getElementById("weeklySummaryItems"),
  deadlineList: document.getElementById("deadlineList"),
  pillarGrid: document.getElementById("pillarGrid"),
  pillarDetailSection: document.getElementById("pillarDetailSection"),
  closePillarDetail: document.getElementById("closePillarDetail"),
  pillarDetailPills: document.getElementById("pillarDetailPills"),
  pillarDetailTitle: document.getElementById("pillarDetailTitle"),
  pillarDetailSummary: document.getElementById("pillarDetailSummary"),
  pillarDetailStats: document.getElementById("pillarDetailStats"),
  pillarActionGrid: document.getElementById("pillarActionGrid"),
  actionRegisterCount: document.getElementById("actionRegisterCount"),
  actionSearch: document.getElementById("actionSearch"),
  actionPillarFilter: document.getElementById("actionPillarFilter"),
  actionStatusFilter: document.getElementById("actionStatusFilter"),
  actionGrid: document.getElementById("actionGrid"),
  actionDetailSection: document.getElementById("actionDetailSection"),
  closeActionDetail: document.getElementById("closeActionDetail"),
  actionDetailPills: document.getElementById("actionDetailPills"),
  actionDetailTitle: document.getElementById("actionDetailTitle"),
  actionDetailSummary: document.getElementById("actionDetailSummary"),
  actionDetailMeta: document.getElementById("actionDetailMeta"),
  actionImpactGrid: document.getElementById("actionImpactGrid"),
  actionOriginalText: document.getElementById("actionOriginalText"),
  actionMetricsText: document.getElementById("actionMetricsText"),
  actionMilestoneList: document.getElementById("actionMilestoneList"),
  actionEvidenceList: document.getElementById("actionEvidenceList"),
  actionPressureCopy: document.getElementById("actionPressureCopy"),
  actionShareLinks: document.getElementById("actionShareLinks"),
  copyPressureLine: document.getElementById("copyPressureLine"),
  bodyTable: document.getElementById("bodyTable"),
  briefingGrid: document.getElementById("briefingGrid"),
  briefingAudienceSelect: document.getElementById("briefingAudienceSelect"),
  briefingActionSelect: document.getElementById("briefingActionSelect"),
  briefingPreview: document.getElementById("briefingPreview"),
  copyBriefing: document.getElementById("copyBriefing"),
  downloadBriefing: document.getElementById("downloadBriefing"),
  mpLookupForm: document.getElementById("mpLookupForm"),
  mpPostcode: document.getElementById("mpPostcode"),
  manualMpName: document.getElementById("manualMpName"),
  manualConstituency: document.getElementById("manualConstituency"),
  mpActionSelect: document.getElementById("mpActionSelect"),
  mpLookupStatus: document.getElementById("mpLookupStatus"),
  mpResult: document.getElementById("mpResult"),
  mpName: document.getElementById("mpName"),
  mpConstituency: document.getElementById("mpConstituency"),
  mpContactPills: document.getElementById("mpContactPills"),
  mpContact: document.getElementById("mpContact"),
  mpSubject: document.getElementById("mpSubject"),
  mpBody: document.getElementById("mpBody"),
  mpMailtoLink: document.getElementById("mpMailtoLink"),
  copyMpEmail: document.getElementById("copyMpEmail"),
  downloadMpEmail: document.getElementById("downloadMpEmail"),
  detailTabs: Array.from(document.querySelectorAll("[data-detail-tab]")),
  detailPanels: {
    overview: document.getElementById("detailTabOverview"),
    evidence: document.getElementById("detailTabEvidence"),
    pressure: document.getElementById("detailTabPressure"),
  },
};

const formatInteger = new Intl.NumberFormat("en-GB", {
  maximumFractionDigits: 0,
});

const formatCurrency = new Intl.NumberFormat("en-GB", {
  style: "currency",
  currency: "GBP",
  maximumFractionDigits: 0,
});

const formatPercent = new Intl.NumberFormat("en-GB", {
  style: "percent",
  maximumFractionDigits: 0,
});

const formatDate = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "long",
  year: "numeric",
});

const severityRank = {
  Delayed: 0,
  "Late but in progress": 1,
  "At risk": 2,
  "On track": 3,
  Completed: 4,
  "Too vague to track": 5,
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatMetric(counter) {
  if (counter.format === "currency") {
    return formatCurrency.format(counter.central);
  }
  return formatInteger.format(counter.central);
}

function formatDelta(counter) {
  if (counter.format === "currency") {
    return `+${formatCurrency.format(counter.per_day)} per day`;
  }
  return `+${formatInteger.format(counter.per_day)} per day`;
}

function formatImpact(value, format) {
  return format === "currency" ? formatCurrency.format(value) : formatInteger.format(value);
}

function formatCounterRange(counter) {
  const min = counter.format === "currency" ? formatCurrency.format(counter.min) : formatInteger.format(counter.min);
  const max = counter.format === "currency" ? formatCurrency.format(counter.max) : formatInteger.format(counter.max);
  return `${min} to ${max}`;
}

function formatMaybeDate(value) {
  return value ? formatDate.format(new Date(value)) : "Date not extracted";
}

function getStatusClass(status) {
  switch (status) {
    case "Delayed":
      return "pill--delayed";
    case "Late but in progress":
      return "pill--progress";
    case "At risk":
      return "pill--risk";
    default:
      return "pill--progress";
  }
}

function getEffectClass(effect) {
  switch (effect) {
    case "claim":
      return "pill--claim";
    case "complete":
      return "pill--progress";
    case "progress":
      return "pill--risk";
    default:
      return "pill--neutral";
  }
}

function getEffectLabel(effect) {
  switch (effect) {
    case "claim":
      return "Claim";
    case "complete":
      return "Delivered evidence";
    case "progress":
      return "Progress evidence";
    default:
      return "Context";
  }
}

function getActionById(actionId) {
  return state.data.actions.find((action) => action.id === actionId) ?? null;
}

function getPillarById(pillarId) {
  return state.data.pillars.find((pillar) => pillar.id === pillarId) ?? null;
}

function getUniquePillars() {
  const seen = new Map();
  state.data.actions.forEach((action) => {
    if (!seen.has(action.pillar_id)) {
      seen.set(action.pillar_id, action.pillar_title || action.pillar_id);
    }
  });
  return Array.from(seen.entries()).map(([id, title]) => ({ id, title }));
}

function normalizeMilestones(action) {
  const deduped = new Map();
  action.milestones.forEach((milestone) => {
    const key = `${milestone.due_date}:${milestone.title.toLowerCase()}`;
    const existing = deduped.get(key);
    if (!existing || existing.source !== "roadmap" && milestone.source === "roadmap") {
      deduped.set(key, milestone);
    }
  });

  return Array.from(deduped.values()).sort((left, right) => {
    if (left.due_date === right.due_date) {
      return left.title.localeCompare(right.title);
    }
    return left.due_date.localeCompare(right.due_date);
  });
}

function getRepresentativeMilestone(action) {
  const milestones = normalizeMilestones(action);
  const active = milestones.find((milestone) => milestone.status !== "Completed");
  return active ?? milestones[milestones.length - 1] ?? null;
}

function getActionImpactScore(action) {
  const impact = action.impact_profile;
  return impact.patients_per_year + impact.nhs_avoidable_spend_per_year_gbp / 1000000 + impact.investment_per_year_gbp / 1000000;
}

function compareActions(left, right) {
  const leftMilestone = getRepresentativeMilestone(left);
  const rightMilestone = getRepresentativeMilestone(right);
  const leftDelay = leftMilestone?.days_late ?? 0;
  const rightDelay = rightMilestone?.days_late ?? 0;
  const leftSeverity = severityRank[left.status] ?? 99;
  const rightSeverity = severityRank[right.status] ?? 99;

  if (leftSeverity !== rightSeverity) {
    return leftSeverity - rightSeverity;
  }
  if (leftDelay !== rightDelay) {
    return rightDelay - leftDelay;
  }
  return getActionImpactScore(right) - getActionImpactScore(left);
}

function buildEvidenceCoverage(data) {
  const actions = data.actions;
  const linked = actions.filter((action) => (action.evidence || []).length > 0);
  const unlinked = actions.filter((action) => !(action.evidence || []).length);
  const trackableUnlinked = unlinked.filter((action) => action.status !== "Too vague to track");
  const claims = actions.filter((action) => action.claim_without_evidence);
  const topGap = unlinked.slice().sort(compareActions)[0] ?? null;

  return {
    linkedCount: linked.length,
    totalCount: actions.length,
    linkedShare: linked.length / actions.length,
    unlinkedCount: unlinked.length,
    trackableUnlinkedCount: trackableUnlinked.length,
    claimCount: claims.length,
    topGap,
  };
}

function getFilteredActions() {
  return state.data.actions
    .filter((action) => {
      const haystack = [
        action.display_number,
        action.title,
        action.summary,
        action.lead_body,
        action.current_minister,
      ]
        .join(" ")
        .toLowerCase();

      const matchesSearch = haystack.includes(state.filters.search);
      const matchesPillar = state.filters.pillar === "all" || action.pillar_id === state.filters.pillar;
      const matchesStatus = state.filters.status === "all" || action.status === state.filters.status;
      return matchesSearch && matchesPillar && matchesStatus;
    })
    .sort(compareActions);
}

function getTopDelayedAction() {
  const delayed = state.data.actions
    .filter((action) => action.status === "Delayed" || action.status === "Late but in progress")
    .sort(compareActions);
  return delayed[0] ?? state.data.actions.slice().sort(compareActions)[0] ?? null;
}

function getSelectedAction(selectValue) {
  if (selectValue === "top_delay") {
    return getTopDelayedAction();
  }
  return getActionById(selectValue);
}

function actionCardMarkup(action, options = {}) {
  const milestone = getRepresentativeMilestone(action);
  const dueLabel = milestone ? `Due ${formatDate.format(new Date(milestone.due_date))}` : "No dated milestone";
  const deadlineHint = milestone?.days_late ? `${milestone.days_late} days late` : milestone?.status === "At risk" ? "Within 60 days" : "Monitoring";
  const openLabel = options.openLabel ?? "Open action";
  const evidenceCount = action.evidence?.length ?? 0;
  const evidenceLabel = evidenceCount ? `${evidenceCount} official source${evidenceCount === 1 ? "" : "s"}` : "No linked public evidence";

  return `
    <article class="action-card">
      <div class="pill-row">
        <span class="pill ${getStatusClass(action.status)}">${escapeHtml(action.status)}</span>
        <span class="pill pill--risk">Score ${escapeHtml(action.score)}</span>
        <span class="pill pill--progress">Action ${escapeHtml(action.display_number)}</span>
        <span class="pill ${evidenceCount ? "pill--neutral" : "pill--delayed"}">${escapeHtml(evidenceLabel)}</span>
        ${action.claim_without_evidence ? '<span class="pill pill--claim">Claim without deliverable</span>' : ""}
      </div>
      <h3 class="action-card__title">${escapeHtml(action.title)}</h3>
      <p class="action-card__summary">${escapeHtml(action.summary)}</p>
      <div class="action-card__meta">
        <span>${escapeHtml(action.pillar_title)}</span>
        <span>${escapeHtml(action.lead_body)}</span>
        <span>${escapeHtml(action.current_minister)}</span>
      </div>
      <div class="action-card__meta">
        <span>${escapeHtml(dueLabel)}</span>
        <span>${escapeHtml(deadlineHint)}</span>
        <span>${escapeHtml(action.territory || "Territory not specified")}</span>
      </div>
      <div class="action-card__footer">
        <button class="secondary-button" type="button" data-open-action="${escapeHtml(action.id)}">${escapeHtml(openLabel)}</button>
      </div>
    </article>
  `;
}

function renderStatusSummary(statusSummary) {
  elements.statusSummary.innerHTML = Object.entries(statusSummary)
    .map(([label, value]) => {
      return `
        <div class="status-row">
          <span class="status-row__label">${escapeHtml(label)}</span>
          <span class="status-row__value">${formatInteger.format(value)}</span>
        </div>
      `;
    })
    .join("");
}

function renderWeeklySummary(summary) {
  elements.weeklySummaryDate.textContent = `Week ending ${formatDate.format(new Date(summary.review_date))}`;
  elements.weeklySummaryHeadline.textContent = summary.headline;
  elements.weeklySummaryItems.innerHTML = summary.items
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
}

function renderEvidenceCoverage(data) {
  const coverage = buildEvidenceCoverage(data);
  const share = formatPercent.format(coverage.linkedShare);

  elements.evidenceHealth.innerHTML = `
    <div class="evidence-health__main">
      <span class="evidence-health__eyebrow">Official source coverage</span>
      <strong class="evidence-health__value">${escapeHtml(share)}</strong>
      <div class="mini-meter" aria-hidden="true">
        <span style="width: ${Math.round(coverage.linkedShare * 100)}%"></span>
      </div>
    </div>
    <div class="evidence-health__stats">
      <article class="evidence-stat">
        <span class="evidence-stat__label">Actions with evidence</span>
        <strong class="evidence-stat__value">${formatInteger.format(coverage.linkedCount)} / ${formatInteger.format(coverage.totalCount)}</strong>
      </article>
      <article class="evidence-stat">
        <span class="evidence-stat__label">Still unlinked</span>
        <strong class="evidence-stat__value">${formatInteger.format(coverage.unlinkedCount)}</strong>
      </article>
      <article class="evidence-stat">
        <span class="evidence-stat__label">Claim-only items</span>
        <strong class="evidence-stat__value">${formatInteger.format(coverage.claimCount)}</strong>
      </article>
    </div>
  `;

  const highlights = [
    `${formatInteger.format(coverage.trackableUnlinkedCount)} measurable actions still have no linked public source.`,
    coverage.topGap ? `Biggest current gap: ${coverage.topGap.title}.` : "Every action currently has at least one official source attached.",
    coverage.claimCount
      ? `${formatInteger.format(coverage.claimCount)} actions carry a published progress claim but not the promised deliverable.`
      : "No action is currently flagged as claim-only.",
  ];

  elements.evidenceHighlights.innerHTML = highlights.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderDeadlines(deadlines) {
  elements.deadlineList.innerHTML = deadlines
    .map((item) => {
      return `
        <article class="deadline-card">
          <div class="pill-row">
            <span class="pill ${getStatusClass(item.status)}">${escapeHtml(item.status)}</span>
            <span class="pill pill--risk">${formatInteger.format(item.days_late)} days late</span>
          </div>
          <h3 class="deadline-card__title">${escapeHtml(item.title)}</h3>
          <div class="deadline-meta">
            <span>Due ${formatDate.format(new Date(item.due_date))}</span>
            <span>${escapeHtml(item.lead_body)}</span>
            <span>${escapeHtml(item.current_minister)}</span>
          </div>
          <div class="deadline-meta">${escapeHtml(item.note)}</div>
        </article>
      `;
    })
    .join("");
}

function renderPillars(pillars) {
  elements.pillarGrid.innerHTML = pillars
    .map((pillar) => {
      return `
        <article class="pillar-card">
          <div class="pill-row">
            <span class="pill pill--progress">${formatInteger.format(pillar.delayed_actions)} delayed actions</span>
            <span class="pill pill--risk">${formatInteger.format(pillar.tracked_actions)} tracked actions</span>
          </div>
          <h3>${escapeHtml(pillar.title)}</h3>
          <div class="pillar-card__score">${escapeHtml(pillar.score)}</div>
          <p class="pillar-card__summary">${escapeHtml(pillar.summary)}</p>
          <div class="pillar-card__footer">
            <span>${escapeHtml(pillar.estimated_counter_contribution)}</span>
            <span>Hero action: ${escapeHtml(pillar.hero_action_title)}</span>
          </div>
          <div class="action-card__footer">
            <button class="secondary-button" type="button" data-open-pillar="${escapeHtml(pillar.id)}">Open pillar</button>
            <button class="ghost-button" type="button" data-open-action="${escapeHtml(pillar.hero_action_id)}">Open hero action</button>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderBodies(bodies) {
  elements.bodyTable.innerHTML = bodies
    .map((body) => {
      const freshness = body.freshness_days === 999 ? "No linked evidence" : `${formatInteger.format(body.freshness_days)} days`;
      return `
        <tr>
          <td>${escapeHtml(body.name)}</td>
          <td>${formatInteger.format(body.delayed_actions)}</td>
          <td>${formatInteger.format(body.tracked_actions)}</td>
          <td>${escapeHtml(body.current_minister)}</td>
          <td>${escapeHtml(freshness)}</td>
        </tr>
      `;
    })
    .join("");
}

function renderActionFilters() {
  const options = ['<option value="all">All pillars</option>']
    .concat(
      getUniquePillars().map((pillar) => {
        return `<option value="${escapeHtml(pillar.id)}">${escapeHtml(pillar.title)}</option>`;
      }),
    )
    .join("");

  if (!elements.actionPillarFilter.dataset.ready) {
    elements.actionPillarFilter.innerHTML = options;
    elements.actionPillarFilter.dataset.ready = "true";
    elements.actionPillarFilter.value = state.filters.pillar;
  }
}

function renderActionRegister() {
  const actions = getFilteredActions();
  const linked = actions.filter((action) => (action.evidence || []).length > 0).length;
  elements.actionRegisterCount.textContent = `${formatInteger.format(actions.length)} items | ${formatInteger.format(linked)} with evidence`;
  elements.actionGrid.innerHTML = actions.length
    ? actions.map((action) => actionCardMarkup(action)).join("")
    : '<div class="empty-state">No actions match the current filters.</div>';
}

function renderPillarDetail() {
  if (!state.currentPillarId) {
    elements.pillarDetailSection.hidden = true;
    return;
  }

  const pillar = getPillarById(state.currentPillarId);
  const pillarActions = state.data.actions
    .filter((action) => action.pillar_id === state.currentPillarId)
    .sort(compareActions);

  if (!pillar || !pillarActions.length) {
    elements.pillarDetailSection.hidden = true;
    return;
  }

  const totalActionScore = Math.round(pillarActions.reduce((sum, action) => sum + action.score, 0) / pillarActions.length);
  const delayedActions = pillarActions.filter((action) => action.status === "Delayed" || action.status === "Late but in progress");
  const topAction = pillarActions[0];

  elements.pillarDetailSection.hidden = false;
  elements.pillarDetailPills.innerHTML = `
    <span class="pill pill--progress">${escapeHtml(pillar.title)}</span>
    <span class="pill pill--risk">Score ${escapeHtml(totalActionScore)}</span>
    <span class="pill ${getStatusClass(delayedActions.length ? "Delayed" : "On track")}">${formatInteger.format(delayedActions.length)} delayed or late</span>
  `;
  elements.pillarDetailTitle.textContent = pillar.title;
  elements.pillarDetailSummary.textContent = `${pillar.summary} The most exposed item currently is ${topAction.title}.`;
  elements.pillarDetailStats.innerHTML = `
    <article class="stat-card">
      <span class="stat-card__label">Tracked actions</span>
      <strong class="stat-card__value">${formatInteger.format(pillarActions.length)}</strong>
    </article>
    <article class="stat-card">
      <span class="stat-card__label">Delayed or late</span>
      <strong class="stat-card__value">${formatInteger.format(delayedActions.length)}</strong>
    </article>
    <article class="stat-card">
      <span class="stat-card__label">Top exposed action</span>
      <strong class="stat-card__value stat-card__value--small">${escapeHtml(topAction.title)}</strong>
    </article>
  `;
  elements.pillarActionGrid.innerHTML = pillarActions.map((action) => actionCardMarkup(action, { openLabel: "Open action" })).join("");
}

function renderDetailTabs() {
  elements.detailTabs.forEach((button) => {
    const isActive = button.dataset.detailTab === state.detailTab;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-selected", String(isActive));
  });

  Object.entries(elements.detailPanels).forEach(([name, panel]) => {
    panel.hidden = name !== state.detailTab;
  });
}

function buildPressureLine(action) {
  const milestone = getRepresentativeMilestone(action);
  const dueText = milestone ? formatDate.format(new Date(milestone.due_date)) : "the stated timetable";
  const delayText = milestone?.days_late ? `${formatInteger.format(milestone.days_late)} days late` : action.status.toLowerCase();

  return `${action.current_minister} and ${action.lead_body} were supposed to deliver "${action.title}" by ${dueText}. As of ${formatDate.format(new Date(state.data.meta.review_date))}, the action is ${delayText}. The wider plan delay is already being tracked at ${formatMetric(state.data.counters.patients)} people affected, ${formatMetric(state.data.counters.nhs)} in avoidable NHS spend, and ${formatMetric(state.data.counters.investment)} in investment lost or deferred.`;
}

function buildShareLinks(action) {
  const pressureLine = buildPressureLine(action);
  const shareTarget = `${window.location.href.split("#")[0]}#action/${encodeURIComponent(action.id)}`;

  return [
    {
      label: "Share on X",
      href: `https://twitter.com/intent/tweet?text=${encodeURIComponent(`${pressureLine} ${shareTarget}`)}`,
    },
    {
      label: "Share on LinkedIn",
      href: `https://www.linkedin.com/feed/?shareActive=true&text=${encodeURIComponent(`${pressureLine} ${shareTarget}`)}`,
    },
    {
      label: "Email this",
      href: `mailto:?subject=${encodeURIComponent(`Life Sciences Sector Plan delay: ${action.title}`)}&body=${encodeURIComponent(`${pressureLine}\n\n${shareTarget}`)}`,
    },
  ];
}

function renderActionDetail() {
  const action = state.currentActionId ? getActionById(state.currentActionId) : null;
  if (!action) {
    elements.actionDetailSection.hidden = true;
    return;
  }

  const milestones = normalizeMilestones(action);
  const evidence = action.evidence ?? [];
  const pressureLine = buildPressureLine(action);
  const shareLinks = buildShareLinks(action);

  elements.actionDetailSection.hidden = false;
  elements.actionDetailPills.innerHTML = `
    <span class="pill ${getStatusClass(action.status)}">${escapeHtml(action.status)}</span>
    <span class="pill pill--risk">Action ${escapeHtml(action.display_number)}</span>
    <span class="pill pill--progress">${escapeHtml(action.pillar_title)}</span>
  `;
  elements.actionDetailTitle.textContent = action.title;
  elements.actionDetailSummary.textContent = action.summary;
  elements.actionDetailMeta.innerHTML = `
    <article class="detail-meta-card">
      <span class="detail-meta-card__label">Lead body</span>
      <strong>${escapeHtml(action.lead_body)}</strong>
    </article>
    <article class="detail-meta-card">
      <span class="detail-meta-card__label">Current minister</span>
      <strong>${escapeHtml(action.current_minister)}</strong>
    </article>
    <article class="detail-meta-card">
      <span class="detail-meta-card__label">Lead official</span>
      <strong>${escapeHtml(`${action.lead_official_role}, ${action.lead_body}`)}</strong>
    </article>
    <article class="detail-meta-card">
      <span class="detail-meta-card__label">Confidence</span>
      <strong>${formatPercent.format(action.review_confidence)}</strong>
    </article>
    <article class="detail-meta-card">
      <span class="detail-meta-card__label">Public sources</span>
      <strong>${formatInteger.format(evidence.length)}</strong>
      <span class="detail-meta-card__note">${escapeHtml(
        action.claim_without_evidence
          ? "Published progress claim recorded, but the promised deliverable is still missing."
          : evidence.length
            ? "Official sources are linked in the evidence tab."
            : "No linked public evidence is attached yet.",
      )}</span>
    </article>
  `;

  elements.actionImpactGrid.innerHTML = `
    <article class="stat-card">
      <span class="stat-card__label">People affected per year</span>
      <strong class="stat-card__value">${formatInteger.format(action.impact_profile.patients_per_year)}</strong>
    </article>
    <article class="stat-card">
      <span class="stat-card__label">Avoidable NHS spend per year</span>
      <strong class="stat-card__value">${formatCurrency.format(action.impact_profile.nhs_avoidable_spend_per_year_gbp)}</strong>
    </article>
    <article class="stat-card">
      <span class="stat-card__label">Investment at risk per year</span>
      <strong class="stat-card__value">${formatCurrency.format(action.impact_profile.investment_per_year_gbp)}</strong>
    </article>
    <article class="stat-card">
      <span class="stat-card__label">Range factor</span>
      <strong class="stat-card__value stat-card__value--small">${action.impact_profile.range_low}x to ${action.impact_profile.range_high}x</strong>
    </article>
  `;

  elements.actionOriginalText.textContent = action.original_text || action.action_text;
  elements.actionMetricsText.textContent = action.metrics_text || "No public metric extracted.";

  elements.actionMilestoneList.innerHTML = milestones.length
    ? milestones
        .map((milestone) => {
          return `
            <article class="milestone-item">
              <div class="pill-row">
                <span class="pill ${getStatusClass(milestone.status)}">${escapeHtml(milestone.status)}</span>
                <span class="pill pill--risk">${escapeHtml(milestone.deadline_type)}</span>
              </div>
              <h3>${escapeHtml(milestone.title)}</h3>
              <p>${escapeHtml(milestone.text)}</p>
              <div class="deadline-meta">
                <span>Due ${formatDate.format(new Date(milestone.due_date))}</span>
                <span>${escapeHtml(milestone.days_late ? `${milestone.days_late} days late` : milestone.review_note)}</span>
              </div>
            </article>
          `;
        })
        .join("")
    : '<div class="empty-state">No milestone is publicly trackable for this action yet.</div>';

  elements.actionEvidenceList.innerHTML = evidence.length
    ? evidence
        .map((item) => {
          return `
            <article class="evidence-item">
              <div class="evidence-item__meta">
                <div class="pill-row">
                  <span class="pill pill--neutral">${escapeHtml(item.source_org)}</span>
                  <span class="pill ${getEffectClass(item.effect)}">${escapeHtml(getEffectLabel(item.effect))}</span>
                  <span class="pill pill--risk">${escapeHtml(item.evidence_type)}</span>
                </div>
                <span class="evidence-item__date">${escapeHtml(formatMaybeDate(item.published_at))}</span>
              </div>
              <h3>${escapeHtml(item.title)}</h3>
              <p>${escapeHtml(item.summary)}</p>
              <a class="source-link" href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">Open source</a>
            </article>
          `;
        })
        .join("")
    : '<div class="empty-state">No linked public evidence is attached yet for this action.</div>';

  elements.actionPressureCopy.textContent = pressureLine;
  elements.actionShareLinks.innerHTML = shareLinks
    .map((item) => `<a class="secondary-link" href="${escapeHtml(item.href)}" target="_blank" rel="noreferrer">${escapeHtml(item.label)}</a>`)
    .join("");

  renderDetailTabs();
}

function buildBriefingText(audience, action) {
  const topDelays = state.data.latest_missed_deadlines
    .slice(0, 3)
    .map((item) => `- ${item.title} (${item.lead_body}, due ${formatDate.format(new Date(item.due_date))}, ${item.days_late} days late)`)
    .join("\n");

  const focusAction = action
    ? `Focus action: ${action.title}\nLead body: ${action.lead_body}\nCurrent minister: ${action.current_minister}\nStatus: ${action.status}\n`
    : "";

  const audienceLine = {
    MP: "Use this to press ministers on missed commitments and their local consequences.",
    Journalist: "Use this to frame a clear delivery story with dates, bodies, and cost-of-delay numbers.",
    "Member company": "Use this to connect missed commitments to confidence, scale-up conditions, and investment risk.",
    "Patient group": "Use this to connect delivery failure to slower patient access and avoidable NHS pressure.",
  }[audience] || "Use this as a short external briefing.";

  return [
    `Life Sciences Sector Plan Tracker`,
    `Review date: ${formatDate.format(new Date(state.data.meta.review_date))}`,
    "",
    audienceLine,
    "",
    `Overall delivery score: ${state.data.score.overall}`,
    `People affected: ${formatMetric(state.data.counters.patients)} (${formatCounterRange(state.data.counters.patients)} range)`,
    `Avoidable NHS spend: ${formatMetric(state.data.counters.nhs)} (${formatCounterRange(state.data.counters.nhs)} range)`,
    `Investment lost or deferred: ${formatMetric(state.data.counters.investment)} (${formatCounterRange(state.data.counters.investment)} range)`,
    "",
    focusAction,
    `Top missed deadlines:`,
    topDelays,
    "",
    `Public evidence note: ${state.data.meta.evidence_disclaimer}`,
    `Plan source: ${state.data.meta.source_urls[0]}`,
  ]
    .filter(Boolean)
    .join("\n");
}

function renderBriefings(briefings) {
  elements.briefingGrid.innerHTML = briefings
    .map((briefing) => {
      return `
        <article class="briefing-card">
          <p class="briefing-card__audience">${escapeHtml(briefing.audience)}</p>
          <h3>${escapeHtml(briefing.title)}</h3>
          <p>${escapeHtml(briefing.description)}</p>
          <button class="secondary-button" type="button" data-select-audience="${escapeHtml(briefing.audience)}">${escapeHtml(briefing.cta)}</button>
        </article>
      `;
    })
    .join("");
}

function renderBriefingControls() {
  if (!elements.briefingAudienceSelect.dataset.ready) {
    elements.briefingAudienceSelect.innerHTML = state.data.briefings
      .map((briefing) => `<option value="${escapeHtml(briefing.audience)}">${escapeHtml(briefing.audience)}</option>`)
      .join("");
    elements.briefingAudienceSelect.dataset.ready = "true";
  }

  const actionOptions = [
    '<option value="top_delay">Top missed deadlines</option>',
    ...state.data.actions
      .slice()
      .sort(compareActions)
      .map((action) => `<option value="${escapeHtml(action.id)}">Action ${escapeHtml(action.display_number)}: ${escapeHtml(action.title)}</option>`),
  ];

  elements.briefingActionSelect.innerHTML = actionOptions.join("");
  elements.briefingAudienceSelect.value = state.selectedAudience;
  elements.briefingActionSelect.value = state.selectedBriefingActionId;
  const selectedAction = getSelectedAction(state.selectedBriefingActionId);
  elements.briefingPreview.value = buildBriefingText(state.selectedAudience, selectedAction);
}

function buildMpMessage(action, member) {
  const constituency = member?.constituency || elements.manualConstituency.value.trim() || "my constituency";
  const memberName = member?.name || elements.manualMpName.value.trim() || "my MP";
  const emailLabel = member?.email || "";
  const dueMilestone = getRepresentativeMilestone(action);
  const dueLine = dueMilestone ? formatDate.format(new Date(dueMilestone.due_date)) : "the plan timetable";
  const pressureLine = buildPressureLine(action);

  return {
    subject: `Please press ministers on the Life Sciences Sector Plan delay affecting ${constituency}`,
    body: [
      `Dear ${memberName},`,
      "",
      `I am writing as a constituent about the government's failure to deliver parts of the Life Sciences Sector Plan published on 16 July 2025.`,
      "",
      `One action now needing scrutiny is "${action.title}". The plan timetable pointed to ${dueLine}, but the tracker currently records this action as ${action.status.toLowerCase()}.`,
      "",
      pressureLine,
      "",
      `Please ask ministers and ${action.lead_body} to explain the delay, publish the supporting evidence for delivery, and set out when this action will actually be completed.`,
      "",
      `The wider tracker is now estimating ${formatMetric(state.data.counters.patients)} people affected, ${formatMetric(state.data.counters.nhs)} in avoidable NHS spend, and ${formatMetric(state.data.counters.investment)} in investment lost or deferred since launch.`,
      "",
      `Yours sincerely,`,
      `[Your name]`,
      emailLabel ? `[Contact via ${emailLabel}]` : "",
    ]
      .filter(Boolean)
      .join("\n"),
  };
}

function renderMpLookup() {
  const action = getSelectedAction(state.selectedMpActionId);
  const member = state.mpLookup.member;
  const draft = action ? buildMpMessage(action, member) : { subject: "", body: "" };

  elements.mpLookupStatus.textContent = state.mpLookup.message;
  elements.mpSubject.value = draft.subject;
  elements.mpBody.value = draft.body;
  elements.mpMailtoLink.href = draft.subject
    ? `mailto:${member?.email || ""}?subject=${encodeURIComponent(draft.subject)}&body=${encodeURIComponent(draft.body)}`
    : "#";

  if (!member) {
    elements.mpResult.hidden = true;
    return;
  }

  elements.mpResult.hidden = false;
  elements.mpName.textContent = member.name;
  elements.mpConstituency.textContent = `${member.constituency} (${member.party})`;
  elements.mpContactPills.innerHTML = `
    <span class="pill pill--progress">${escapeHtml(member.party)}</span>
    <span class="pill pill--risk">${escapeHtml(member.email ? "Email found" : "No email found")}</span>
  `;
  elements.mpContact.textContent = member.email
    ? `${member.email}${member.phone ? ` | ${member.phone}` : ""}`
    : "No parliamentary email returned by the API.";
}

async function lookupMpByPostcode(postcode) {
  const lookupUrl = `https://members-api.parliament.uk/api/Members/Search?Location=${encodeURIComponent(postcode)}&IsCurrentMember=true&House=1&take=1`;
  const response = await fetch(lookupUrl);
  if (!response.ok) {
    throw new Error("Postcode lookup failed.");
  }

  const data = await response.json();
  const item = data.items?.[0]?.value;
  if (!item) {
    throw new Error("No current MP found for that postcode.");
  }

  const contactResponse = await fetch(`https://members-api.parliament.uk/api/Members/${item.id}/Contact`);
  const contactData = contactResponse.ok ? await contactResponse.json() : { value: [] };
  const parliamentaryOffice = (contactData.value || []).find((entry) => entry.email) || null;

  return {
    id: item.id,
    name: item.nameFullTitle || item.nameDisplayAs,
    constituency: item.latestHouseMembership?.membershipFrom || "Unknown constituency",
    party: item.latestParty?.name || "Unknown party",
    email: parliamentaryOffice?.email || "",
    phone: parliamentaryOffice?.phone || "",
  };
}

async function handleMpLookup(event) {
  event.preventDefault();
  const postcode = elements.mpPostcode.value.trim();
  if (!postcode) {
    state.mpLookup.status = "manual";
    state.mpLookup.message = "Enter a postcode to use the Parliament API, or add MP details manually below.";
    state.mpLookup.member = null;
    renderMpLookup();
    return;
  }

  state.mpLookup.status = "loading";
  state.mpLookup.message = "Looking up the current MP from the official Parliament API...";
  renderMpLookup();

  try {
    state.mpLookup.member = await lookupMpByPostcode(postcode);
    state.mpLookup.status = "success";
    state.mpLookup.message = `Matched ${state.mpLookup.member.name} for ${state.mpLookup.member.constituency}.`;
  } catch (error) {
    state.mpLookup.member = null;
    state.mpLookup.status = "error";
    state.mpLookup.message = `${error.message} You can still add MP details manually.`;
  }

  renderMpLookup();
}

async function copyText(value, message) {
  try {
    await navigator.clipboard.writeText(value);
    return message;
  } catch (error) {
    return "Copy failed in this browser. Select the text manually.";
  }
}

function downloadText(filename, value) {
  const blob = new Blob([value], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function syncToolActionOptions() {
  const options = [
    '<option value="top_delay">Top delay in the tracker</option>',
    ...state.data.actions
      .slice()
      .sort(compareActions)
      .map((action) => `<option value="${escapeHtml(action.id)}">Action ${escapeHtml(action.display_number)}: ${escapeHtml(action.title)}</option>`),
  ];

  elements.mpActionSelect.innerHTML = options.join("");
  elements.briefingActionSelect.innerHTML = options.join("");
  elements.mpActionSelect.value = state.selectedMpActionId;
  elements.briefingActionSelect.value = state.selectedBriefingActionId;
}

function openPillar(pillarId) {
  state.currentPillarId = pillarId;
  renderPillarDetail();
  elements.pillarDetailSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function openAction(actionId) {
  state.currentActionId = actionId;
  state.detailTab = "overview";
  renderActionDetail();
  updateHash(`action/${actionId}`);
  elements.actionDetailSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function updateHash(hash) {
  if (window.location.hash !== `#${hash}`) {
    history.replaceState(null, "", `#${hash}`);
  }
}

function clearHashTo(anchor) {
  history.replaceState(null, "", `#${anchor}`);
}

function renderOverview(data) {
  elements.pageTitle.textContent = data.meta.title;
  elements.homepageMessage.textContent = data.meta.homepage_message;
  elements.launchDate.textContent = `Plan baseline: ${formatDate.format(new Date(data.meta.launch_date))}`;
  elements.reviewDate.textContent = `Review date: ${formatDate.format(new Date(data.meta.review_date))}`;
  elements.overallScore.textContent = data.score.overall;
  elements.scoreBreakdown.textContent = `${data.score.execution} execution score before ${data.score.transparency_penalty}-point transparency penalty`;
  elements.evidenceDisclaimer.textContent = data.meta.evidence_disclaimer;

  elements.patientsValue.textContent = formatMetric(data.counters.patients);
  elements.patientsDelta.textContent = `${formatDelta(data.counters.patients)} | Range ${formatCounterRange(data.counters.patients)}`;
  elements.nhsValue.textContent = formatMetric(data.counters.nhs);
  elements.nhsDelta.textContent = `${formatDelta(data.counters.nhs)} | Range ${formatCounterRange(data.counters.nhs)}`;
  elements.investmentValue.textContent = formatMetric(data.counters.investment);
  elements.investmentDelta.textContent = `${formatDelta(data.counters.investment)} | Range ${formatCounterRange(data.counters.investment)}`;

  renderStatusSummary(data.status_summary);
  renderEvidenceCoverage(data);
  renderWeeklySummary(data.weekly_summary);
  renderDeadlines(data.latest_missed_deadlines);
  renderPillars(data.pillars);
  renderBodies(data.body_rankings);
  renderBriefings(data.briefings);
  renderActionFilters();
  syncToolActionOptions();
  renderActionRegister();
  renderPillarDetail();
  renderActionDetail();
  renderBriefingControls();
  renderMpLookup();
}

function handleHashRoute() {
  const hash = window.location.hash.replace(/^#/, "");
  if (hash.startsWith("action/")) {
    const actionId = decodeURIComponent(hash.slice("action/".length));
    if (getActionById(actionId)) {
      state.currentActionId = actionId;
      renderActionDetail();
    }
  }
  if (hash.startsWith("pillar/")) {
    const pillarId = decodeURIComponent(hash.slice("pillar/".length));
    if (getPillarById(pillarId)) {
      state.currentPillarId = pillarId;
      renderPillarDetail();
    }
  }
}

function bindEvents() {
  elements.actionSearch.addEventListener("input", (event) => {
    state.filters.search = event.target.value.trim().toLowerCase();
    renderActionRegister();
  });

  elements.actionPillarFilter.addEventListener("change", (event) => {
    state.filters.pillar = event.target.value;
    renderActionRegister();
  });

  elements.actionStatusFilter.addEventListener("change", (event) => {
    state.filters.status = event.target.value;
    renderActionRegister();
  });

  elements.pillarGrid.addEventListener("click", (event) => {
    const button = event.target.closest("[data-open-pillar], [data-open-action]");
    if (!button) {
      return;
    }
    if (button.dataset.openPillar) {
      updateHash(`pillar/${button.dataset.openPillar}`);
      openPillar(button.dataset.openPillar);
    }
    if (button.dataset.openAction) {
      openAction(button.dataset.openAction);
    }
  });

  elements.pillarActionGrid.addEventListener("click", (event) => {
    const button = event.target.closest("[data-open-action]");
    if (button) {
      openAction(button.dataset.openAction);
    }
  });

  elements.actionGrid.addEventListener("click", (event) => {
    const button = event.target.closest("[data-open-action]");
    if (button) {
      openAction(button.dataset.openAction);
    }
  });

  elements.closePillarDetail.addEventListener("click", () => {
    state.currentPillarId = null;
    elements.pillarDetailSection.hidden = true;
    clearHashTo("actions");
  });

  elements.closeActionDetail.addEventListener("click", () => {
    state.currentActionId = null;
    elements.actionDetailSection.hidden = true;
    clearHashTo("actions");
  });

  elements.detailTabs.forEach((button) => {
    button.addEventListener("click", () => {
      state.detailTab = button.dataset.detailTab;
      renderDetailTabs();
    });
  });

  elements.copyPressureLine.addEventListener("click", async () => {
    const message = await copyText(elements.actionPressureCopy.textContent, "Pressure line copied.");
    elements.mpLookupStatus.textContent = message;
  });

  elements.briefingGrid.addEventListener("click", (event) => {
    const button = event.target.closest("[data-select-audience]");
    if (!button) {
      return;
    }
    state.selectedAudience = button.dataset.selectAudience;
    renderBriefingControls();
    elements.briefingPreview.scrollIntoView({ behavior: "smooth", block: "center" });
  });

  elements.briefingAudienceSelect.addEventListener("change", (event) => {
    state.selectedAudience = event.target.value;
    renderBriefingControls();
  });

  elements.briefingActionSelect.addEventListener("change", (event) => {
    state.selectedBriefingActionId = event.target.value;
    renderBriefingControls();
  });

  elements.copyBriefing.addEventListener("click", async () => {
    const message = await copyText(elements.briefingPreview.value, "Briefing copied.");
    elements.mpLookupStatus.textContent = message;
  });

  elements.downloadBriefing.addEventListener("click", () => {
    downloadText(`life-sciences-briefing-${state.selectedAudience.toLowerCase().replace(/\s+/g, "-")}.txt`, elements.briefingPreview.value);
  });

  elements.mpLookupForm.addEventListener("submit", handleMpLookup);

  elements.manualMpName.addEventListener("input", renderMpLookup);
  elements.manualConstituency.addEventListener("input", renderMpLookup);

  elements.mpActionSelect.addEventListener("change", (event) => {
    state.selectedMpActionId = event.target.value;
    renderMpLookup();
  });

  elements.copyMpEmail.addEventListener("click", async () => {
    const text = `${elements.mpSubject.value}\n\n${elements.mpBody.value}`;
    const message = await copyText(text, "MP email copied.");
    elements.mpLookupStatus.textContent = message;
  });

  elements.downloadMpEmail.addEventListener("click", () => {
    downloadText("life-sciences-mp-email.txt", `${elements.mpSubject.value}\n\n${elements.mpBody.value}`);
  });

  window.addEventListener("hashchange", handleHashRoute);
}

async function init() {
  let response = await fetch("data/tracker.json");
  if (!response.ok) {
    response = await fetch("data/tracker.sample.json");
  }
  state.data = await response.json();
  bindEvents();
  renderOverview(state.data);
  handleHashRoute();
}

init();
