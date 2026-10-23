# YD-job Changelog / 变更历史（中英双语 / bilingual）

> 版本规则 / Version policy: see `references/version-policy.md` — bump `.harness-plugin/plugin.json` version only on explicit user instruction / 仅用户明确指令时修改版本号。

## [1.0.0] - 2026-10-22

**中文**
- 首次开源：契约层 7 份（打分 / 采集纪律 / 交付 / 数据 / 画像 / 话术 / 版本策略）
- 技能操作手册 3 份：job-search / job-analyze / job-communication
- 生产脚本：BOSS直聘 CDP 采集器（spider_zhipin.py）、五维打分 + 26 列 Excel 报表引擎（analyzer_engine.py）
- 测试锁 3 套：契约 / 打分 / 交付验证
- 隐私闸门：`.venv/`、`data/`、`config.yaml` 不入库；提供脱敏 `config.example.yaml`

**English**
- Initial open-source release: 7 contracts (scoring rubric / search policy / delivery / data / profile schema / communication templates / version policy)
- 3 skill operating manuals: job-search / job-analyze / job-communication
- Production scripts: BOSS Zhipin CDP collector (`spider_zhipin.py`), five-dimension scoring + 26-column Excel report engine (`analyzer_engine.py`)
- Test locks: contracts / scoring / delivery validation
- Privacy gate: `.venv/`, `data/`, `config.yaml` excluded; sanitized `config.example.yaml` provided

## [1.0.0] 同日补充 / Same-day additions - 2026-10-22（版本号不变 / version unchanged）

**中文**
- 新增 `scripts/tracker_sync.py`：投递漏斗 CRM 状态机（待沟通 → … → 已入职/已结束），只记录，不自动发送
- 新增 `tests/test_tracker.py`：CRM 读写与状态机单元测试
- 新增 `requirements.txt` 与本 CHANGELOG；README 补充依赖安装与 CRM 用法

**English**
- Added `scripts/tracker_sync.py`: application-funnel CRM state machine (pending → … → onboarded/closed); records only, never auto-sends
- Added `tests/test_tracker.py`: CRM read/write + state machine unit tests
- Added `requirements.txt` and this CHANGELOG; README now covers dependency install & CRM usage

## 仓库整理 / Repository cleanup - 2026-10-23（版本号不变 / version unchanged）

**中文**
- 新增 `LICENSE`（MIT）：此前仓库未声明协议，GitHub 显示 All rights reserved，现已明确开源授权
- 移除 5 个早期 V2EX 试验脚本（`probe_wapi.py`、`scrape_v2ex_real.py`、`spider_v2ex.py`、`spider_v2ex_api.py`、`spider_v2ex_cdp.py`）：V2EX 通道未启用，README 与 skills 流程均不依赖
- 同步更新中英双语 README 的 `scripts/` 目录树

**English**
- Added `LICENSE` (MIT): the repository previously declared no license and GitHub showed "All rights reserved"; open-source terms are now explicit
- Removed 5 early V2EX experiment scripts (`probe_wapi.py`, `scrape_v2ex_real.py`, `spider_v2ex.py`, `spider_v2ex_api.py`, `spider_v2ex_cdp.py`): the V2EX channel is not enabled and neither README nor skills depend on them
- Updated the `scripts/` tree in both README files

## Docs / 文档 - 2026-10-22

**中文**
- 中英双语 README（`README.md` 中文 + `README_en.md` 英文，顶部语言导航互链）
- `config.example.yaml` 注释双语化

**English**
- Bilingual README (`README.md` Chinese + `README_en.md` English, cross-linked language navigation at top)
- Bilingual comments in `config.example.yaml`