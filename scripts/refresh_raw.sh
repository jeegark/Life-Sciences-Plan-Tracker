#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RAW_DIR="$ROOT_DIR/data/raw"
SOURCE_DIR="$RAW_DIR/sources"
MINISTER_DIR="$RAW_DIR/ministers"

mkdir -p "$RAW_DIR" "$SOURCE_DIR" "$MINISTER_DIR"

curl -L -s "https://www.gov.uk/government/publications/life-sciences-sector-plan/life-sciences-sector-plan" -o "$RAW_DIR/life_sciences_sector_plan.html"

curl -L -s "https://www.gov.uk/government/publications/life-sciences-sector-plan/life-sciences-sector-plan" -o "$SOURCE_DIR/plan_launch.html"
curl -L -s "https://www.gov.uk/government/news/uk-launches-global-talent-drive-to-attract-world-leading-researchers-and-innovators" -o "$SOURCE_DIR/global_talent_taskforce.html"
curl -L -s "https://www.gov.uk/government/publications/post-16-education-and-skills-white-paper/post-16-education-and-skills-white-paper" -o "$SOURCE_DIR/post16_skills_strategy.html"
curl -L -s "https://www.gov.uk/government/publications/replacing-animals-in-science-strategy" -o "$SOURCE_DIR/alternative_methods_strategy.html"
curl -L -s "https://www.gov.uk/government/publications/statement-of-policy-intent-early-access-to-innovative-medical-devices" -o "$SOURCE_DIR/mhra_early_access_policy.html"
curl -L -s "https://www.gov.uk/government/publications/mhra-performance-data" -o "$SOURCE_DIR/mhra_performance_data.html"
curl -L -s "https://www.gov.uk/government/news/mhra-and-nice-invite-early-adopters-to-trial-accelerated-aligned-pathway-six-months-ahead-of-schedule" -o "$SOURCE_DIR/mhra_nice_aligned_pathway_trial.html"
curl -L -s "https://www.gov.uk/guidance/medicines-get-integrated-scientific-advice-from-the-mhra-and-nice" -o "$SOURCE_DIR/integrated_scientific_advice.html"
curl -L -s "https://www.gov.uk/government/publications/transforming-the-uk-clinical-research-system-august-2025-update/transforming-the-uk-clinical-research-system-august-2025-update" -o "$SOURCE_DIR/clinical_trials_system_update.html"
curl -L -s "https://www.gov.uk/government/news/clinical-trials-regulations-signed-into-law" -o "$SOURCE_DIR/clinical_trials_regulations.html"
curl -L -s "https://www.gov.uk/government/news/visionary-leader-appointed-for-health-data-research-service" -o "$SOURCE_DIR/hdrs_chair.html"
curl -L -s "https://www.gov.uk/government/news/healthcare-innovator-appointed-to-health-data-research-service" -o "$SOURCE_DIR/hdrs_ceo.html"
curl -L -s "https://www.gov.uk/government/publications/national-data-library-progress-update-january-2026/national-data-library-progress-update-january-2026" -o "$SOURCE_DIR/national_data_library_progress.html"

curl -L -s "https://www.gov.uk/government/ministers/minister-of-state-minister-for-science-innovation-research-and-nuclear" -o "$MINISTER_DIR/science.html"
curl -L -s "https://www.gov.uk/government/ministers/parliamentary-under-secretary-of-state--286" -o "$MINISTER_DIR/health_innovation.html"
curl -L -s "https://www.gov.uk/government/ministers/minister-of-state-minister-for-investment--2" -o "$MINISTER_DIR/investment.html"
curl -L -s "https://www.gov.uk/government/ministers/minister-of-state--175" -o "$MINISTER_DIR/skills.html"
