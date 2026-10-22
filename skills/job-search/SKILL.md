---
name: job-search
description: Use when the user invokes $yd-job search, needs to collect job postings from BOSS直聘 (CDP 9222), or requests multi-keyword job collection. Requires logged-in debug Chrome.
---

# Job Search（岗位多源采集）

## 前置契约（先读再执行）

- `../../references/search-policy.md`（采集纪律，**必须遵守**：节奏、风控、去重红线）
- `../../references/data-contract.md`（输出 schema）
- `../../config.yaml`（`search` 段：关键词/城市/页数；`browser` 段：调试端口）

## 环境前置（不满足即停）

1. 本地 9222 调试端口 Chrome 已启动：
   `--remote-debugging-port=9222 --user-data-dir="C:\Users\jiang\.dsh\chrome-debug-profile"`
2. 目标平台（BOSS直聘）在调试浏览器中**已登录**且存在至少一个平台标签页
3. 运行 Python：项目 `.venv\Scripts\python.exe`（禁止 DSH runtime python）

## 执行流程

1. 读取 `config.yaml search.keywords`（多关键词）与 `pages`
2. 运行 `../../scripts/spider_zhipin.py`
   - 每个关键词**先真实导航**到搜索页，再发 wapi 请求
   - 请求间隔遵守 `spider.min_delay_seconds`~`max_delay_seconds`
   - `code=37` 类风控 → 重导航 + 重试（≤2 次）→ 仍失败停该关键词并报告
3. 输出：
   - `../../data/raw_jobs.json`（去重后全量，290+ 条量级）
   - `../../data/raw_pages/`（分页原始，排障用）
   - `../../data/probe_joblist.json`（探测样本，可选）

## 输出边界

- 只产出数据文件，**不打分、不出报告、不写投递追踪**
- 不自动投递、不自动发送任何消息（红线）
- 遇到验证码/滑块 → 停止该通道，用户手动完成，**绝不代做验证码**

## 失败处理

- 平台接口改版 → 停止适配器，报告字段差异，不得猜测映射
- 单关键词全失败 → 记录 checkpoint，继续下一关键词，最后汇总失败清单