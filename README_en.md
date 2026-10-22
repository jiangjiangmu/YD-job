# YD-job — Industrial-Grade Job-Search Automation Hub

[简体中文](README.md) | [English](README_en.md)

An evidence-driven, closed-loop pipeline for job hunting: **multi-source job collection → five-dimension scoring → report delivery → application tracking**. Architecture follows the YD-bus paradigm: *contract-driven + test-locked*.

> 📝 Note: `references/` (7 contracts) and `skills/` (3 operating manuals) are currently written in Chinese — see the summaries below. Config template and changelog are bilingual.

## Repository Layout

```text
YD-job/
├── .harness-plugin/plugin.json   # DSH plugin metadata (version bumped only on explicit user instruction)
├── config.yaml                   # Global config (source of truth; NOT committed — see config.example.yaml)
├── config.example.yaml           # Sanitized config template (bilingual comments)
├── requirements.txt              # Python dependencies
├── CHANGELOG.md                  # Changelog (bilingual)
├── references/                   # Contract layer (7 files — the single source of behavioral truth)
├── skills/                       # Skill packs (each SKILL.md = an operating manual)
├── scripts/                      # Executable scripts
│   ├── spider_zhipin.py          # BOSS Zhipin collector via Chrome DevTools Protocol (production)
│   ├── analyzer_engine.py        # Five-dimension scoring + 26-column Excel report engine (production)
│   ├── tracker_sync.py           # Application-funnel CRM state machine
│   ├── probe_wapi.py             # Platform API probe (troubleshooting)
│   ├── parse_resume.py           # Resume .docx parser (profile source)
│   ├── inspect_cdp.py            # Port-9222 tab inspector (troubleshooting)
│   └── scrape_v2ex_real.py       # V2EX CDP probe (V2EX channel reserved, not enabled)
├── data/                         # Runtime data (NOT committed: platform auth fields + personal data)
└── tests/                        # Test locks (run directly with venv python, no pytest needed)
    ├── test_contracts.py         # Config / data schema / contract file existence
    ├── test_scoring.py           # Weights / salary parsing / degree levels / exclusions / verdict bands
    ├── test_delivery_validation.py # Report structure / header / rows / links / band colors smoke test
    └── test_tracker.py           # CRM read/write + funnel state machine
```

## Install

```powershell
pip install -r requirements.txt
```

## Workflow

```powershell
cd <your YD-job directory>

# 0. Environment: debug Chrome on port 9222 + platform logged in
.venv\Scripts\python.exe scripts\inspect_cdp.py   # verify tab connectivity

# 1. Collect (multi-keyword auto-navigation + anti-risk-control pacing)
.venv\Scripts\python.exe scripts\spider_zhipin.py

# 2. Score + generate report (overwrites 岗位分析报告.xlsx)
.venv\Scripts\python.exe scripts\analyzer_engine.py

# 3. Test locks (all must pass before delivery)
.venv\Scripts\python.exe tests\test_contracts.py
.venv\Scripts\python.exe tests\test_scoring.py
.venv\Scripts\python.exe tests\test_delivery_validation.py
.venv\Scripts\python.exe tests\test_tracker.py
```

## How Scoring Works

Total 100 points: **skills 40 + salary 25 + experience 15 + degree 10 + district 10**; each excluded keyword hit in the job title costs **−20**. Verdict bands: **≥70 ⭐must-apply / ≥65 go / ≥58 possible / ≥48 hold / <48 skip**, with a one-band downgrade when a hard degree gate blocks the match. Every row of the report carries its verdict, a one-line "why", and the five sub-scores.

## Application Tracking (CRM)

`scripts/tracker_sync.py` maintains `data/投递追踪.md` as a funnel state machine:

`待沟通 (pending) → 已打招呼 (contacted) → HR回复 (HR replied) → 面试邀约 (invited) → 面试 (interviewed) → 待结果 (awaiting) → 已拿Offer (offer) → 已入职 (onboarded) / 已结束 (closed)`

```powershell
python scripts/tracker_sync.py add --job "IT Ops Engineer" --company "ACME" --salary "9-11K" --channel "BOSS Zhipin" --score 70.7
python scripts/tracker_sync.py status --company "ACME" --to "已打招呼"
python scripts/tracker_sync.py list
python scripts/tracker_sync.py stats
```

Duplicate company+job entries are rejected; invalid funnel states are rejected; every transition is timestamped into the notes column.

## Contracts (references/ — written in Chinese)

| File | Purpose (summary) |
|---|---|
| `scoring-rubric.md` | Scoring contract: weights, salary parsing rules, degree levels, verdict bands, downgrade rule |
| `search-policy.md` | Collection discipline: 10–18s request pacing, navigation reset, code=37 retry, 100-candidate cap per keyword, never solves CAPTCHAs, never rotates proxies |
| `delivery-contract.md` | Delivery contract: fixed report filename, frozen 26-column header order, 4 sheets, verdict colors, pre-delivery gates |
| `data-contract.md` | Data contract: `raw_jobs.json` schema, dedup key (`encrypt_job_id`), privacy boundary (auth fields never leave the machine) |
| `profile-schema.md` | Profile schema: `config.yaml` profile fields ↔ analyzer runtime keys |
| `communication-templates.md` | Outreach rules: generation format, banned phrases, evidence grading (U=user-confirmed / R=resume-sourced / N=unproven, forbidden) |
| `version-policy.md` | Versioning: change version numbers only on explicit user instruction |

## Skills (skills/ — written in Chinese)

| Skill | Role |
|---|---|
| `job-search` | Collection operating manual: prerequisites, execution flow, output boundaries, failure handling |
| `job-analyze` | Scoring & report manual: single scoring source of truth, delivery gates |
| `job-communication` | Outreach message rules + CRM funnel sync (never auto-sends) |

## Hard Rules

- Never auto-apply or auto-send anything; CAPTCHAs are completed by the user manually
- Never fabricate profiles or data; no fake/placeholder data in `data/raw`
- The report always overwrites the fixed `岗位分析报告.xlsx` — no timestamped copies
- Version numbers change only on explicit user instruction (`version-policy.md`)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) (bilingual).