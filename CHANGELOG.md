# YD-job Changelog

> 版本规则见 `references/version-policy.md`：仅用户明确指令时修改 `.harness-plugin/plugin.json` 版本号。

## [1.0.0] - 2026-10-22

- 首次开源：契约层 7 份（scoring-rubric / search-policy / delivery-contract / data-contract / profile-schema / communication-templates / version-policy）
- 技能操作手册 3 份：job-search / job-analyze / job-communication
- 生产脚本：BOSS直聘 CDP 采集器（`spider_zhipin.py`）、五维打分 + 26 列 Excel 报表引擎（`analyzer_engine.py`）
- 测试锁 3 套：契约 / 打分 / 交付验证
- 隐私闸门：`.venv/`、`data/`、`config.yaml` 不入库；提供脱敏 `config.example.yaml`

## [1.0.0] 同日补充 - 2026-10-22（版本号不变，遵循 version-policy）

- 新增 `scripts/tracker_sync.py`：投递漏斗 CRM 状态机同步（待沟通 → … → 已入职/已结束），只记录不自动发送
- 新增 `tests/test_tracker.py`：tracker 增删改查与状态机单元测试
- 新增 `requirements.txt` 与本 CHANGELOG；README 补充依赖安装与 CRM 用法