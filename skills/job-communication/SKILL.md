---
name: job-communication
description: Use when the user invokes $yd-job communicate, needs outreach messages for target jobs, or wants the 投递追踪.md CRM updated.
---

# Job Communication（话术生成与投递追踪）

## 前置契约（先读再执行）

- `../../references/communication-templates.md`（生成规则 + 禁用表述红线 + 证据分级）
- `../../references/scoring-rubric.md`（档位决定话术优先级：⭐必投 → 去 → 可去 → 缓 → 不去）
- `../../data/投递追踪.md`（CRM 状态文件）

## 输入

- `../../data/岗位分析报告.xlsx` 的「岗位总表」（匹配分析/命中技能/公司/HR头衔/备注）
- `../../config.yaml profile.notes`（个人叙事，仅语气参考）

## 执行流程

1. 选定目标岗位（默认从 ⭐必投 / 去 档位开始）
2. 按 communication-templates §2 生成三段式话术（点名岗位+公司、真实技能、≤120 字）
3. 证据分级检查：话术中每项主张必须是 `U`（用户确认）或 `R`（简历来源）；`N` 级禁止出现
4. 检查无【】占位符残留后交付用户手动复制
5. 用户发送后，经用户确认更新 `投递追踪.md`（可直接用 `scripts/tracker_sync.py`）：岗位/公司/薪资/渠道/匹配得分/状态/沟通记录

## 输出边界

- **永不自动发送**消息、永不自动投递
- 不编造项目/数字/到岗承诺（如"次日到岗"禁用）
- 不生成"给个机会"式甩卖话术，不评价前东家
- 一条岗位一条话术，禁止群发模板腔

## 追踪状态机（投递追踪.md）

`待沟通 → 已打招呼 → HR回复 → 面试邀约 → 面试 → 待结果 → 已拿Offer → 已入职 / 已结束`

- 状态变更以用户确认为准；每轮结束给出下一步建议（按档位优先）