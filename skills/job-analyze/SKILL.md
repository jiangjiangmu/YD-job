---
name: job-analyze
description: Use when the user invokes $yd-job analyze, needs scoring of collected jobs, wants the 岗位分析报告.xlsx regenerated, or asks which jobs to apply to.
---

# Job Analyze（多维打分与报表生成）

## 前置契约（先读再执行）

- `../../references/scoring-rubric.md`（**打分唯一口径**：权重/薪资解析/学历分级/档位阈值/降档规则）
- `../../references/delivery-contract.md`（输出结构：26 列固定表头、4 个 Sheet、固定文件名、无时间戳堆积）
- `../../references/data-contract.md`（输入 schema）
- `../../references/profile-schema.md`（画像字段与运行时映射）
- `../../config.yaml`（`profile` 段）

## 输入

- `../../data/raw_jobs.json`（job-search 产出或已有数据）
- 若文件不存在 → 提示先跑 `job-search`，**不得用假数据演示**

## 执行流程

1. 校验 `config.yaml profile` 完整性（skills/experience_years/expected_salary/own_degree/preferred_regions/excluded_keywords）
2. 运行 `../../scripts/analyzer_engine.py`
   - 按 scoring-rubric 五维加权打分；排除词每项 -20
   - 兼职/实习（exclude_part_time）单独归附表
   - 学历硬门槛触发降档
3. 输出（覆盖更新）：
   - `../../data/岗位分析报告.xlsx`：分析结论 / 岗位总表（26 列）/ 兼职实习 / 统计与配置

## 输出边界

- 每一行岗位必须带：综合得分、要不要去（档位+底色）、匹配分析（为什么）、五维分项
- 不改动 `raw_jobs.json` 原始数据
- 不生成话术、不写投递追踪（那是 job-communication 的职责）

## 完成确认

- 控制台输出 `岗位总表 N 条 | 兼职实习 M 条`，与 data-contract 一致
- 交付前门禁见 delivery-contract §6，任一失败 → 阻断交付并报告