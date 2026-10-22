# YD-job 工业级求职自动化中台

证据驱动的多源岗位采集 → 五维打分 → 报表交付 → 投递追踪 闭环。架构对齐 YD-bus（契约驱动 + 测试锁定）。

## 目录结构

```
YD-job/
├── .harness-plugin/plugin.json   # DSH 插件元数据（版本号仅用户明示时修改）
├── config.yaml                   # 全局配置：search / browser / spider / profile（唯一事实源）
├── references/                   # 契约层（7 份，行为唯一口径）
│   ├── scoring-rubric.md         # 打分契约：权重/薪资解析/学历分级/档位/降档
│   ├── search-policy.md          # 采集纪律：节奏/风控/去重红线/禁止事项
│   ├── delivery-contract.md      # 交付契约：固定文件名/26列表头/4 Sheet/门禁
│   ├── data-contract.md          # 数据契约：raw_jobs.json schema / 去重 / 隐私边界
│   ├── profile-schema.md         # 画像契约：config profile 字段与运行时映射
│   ├── communication-templates.md# 话术契约：生成规则/禁用表述/证据分级
│   └── version-policy.md         # 版本策略
├── skills/                       # 技能包（每个 SKILL.md = 操作手册）
│   ├── job-search/               # 采集：前置环境/执行流程/输出边界/失败处理
│   ├── job-analyze/              # 打分：唯一口径/门禁/输出边界
│   └── job-communication/        # 话术+CRM：生成规则/红线/追踪状态机
├── scripts/                      # 底层脚本
│   ├── spider_zhipin.py          # BOSS直聘 CDP 采集（生产）
│   ├── analyzer_engine.py        # 五维打分 + 26列 Excel 报表（生产）
│   ├── probe_wapi.py             # 平台接口探测（排障）
│   ├── parse_resume.py           # 简历 docx 解析（画像来源）
│   ├── inspect_cdp.py            # 9222 标签页检查（排障）
│   └── scrape_v2ex_real.py       # V2EX CDP 探测（V2EX 通道未启用）
├── data/
│   ├── raw_jobs.json             # 去重后全量岗位（打分输入）
│   ├── 岗位分析报告.xlsx          # 固定输出（4 Sheet / 26 列）
│   ├── 投递追踪.md               # 求职漏斗 CRM
│   ├── raw_pages/                # 分页原始（排障，可清理）
│   ├── raw/                      # 多平台预留汇入（禁止假数据占位）
│   └── reports/                  # 多平台聚合报表预留
└── tests/                        # 测试锁（venv 直接运行，无需 pytest）
    ├── test_contracts.py         # 配置/数据 schema/契约文件存在性
    ├── test_scoring.py           # 权重/薪资/学历/排除词/档位 单元测试
    └── test_delivery_validation.py # 报表结构/表头/行数/链接/底色 冒烟
```

## 安装依赖

```powershell
pip install -r requirements.txt
```

## 使用流程

```powershell
cd E:\AI\DeepSeek Harness\Vault\desktop\projects\YD-job

# 0. 环境：9222 调试 Chrome + 平台已登录（复用 .venv，禁止 DSH runtime python）
.venv\Scripts\python.exe scripts\inspect_cdp.py   # 确认标签页连通

# 1. 采集（多关键词自动导航 + 防风控）
.venv\Scripts\python.exe scripts\spider_zhipin.py

# 2. 打分 + 生成报告（覆盖 岗位分析报告.xlsx）
.venv\Scripts\python.exe scripts\analyzer_engine.py

# 3. 测试锁（全部通过才算交付）
.venv\Scripts\python.exe tests\test_contracts.py
.venv\Scripts\python.exe tests\test_scoring.py
.venv\Scripts\python.exe tests\test_delivery_validation.py
```

## 投递追踪（CRM）

```powershell
# 新增投递记录（默认状态：待沟通）
.venv\Scripts\python.exe scripts\tracker_sync.py add --job "IT运维工程师" --company "某某科技" --salary "9-11K" --channel "BOSS直聘" --score 70.7
# 推进状态（用户确认后）
.venv\Scripts\python.exe scripts\tracker_sync.py status --company "某某科技" --to "已打招呼"
# 列表 / 统计
.venv\Scripts\python.exe scripts\tracker_sync.py list
.venv\Scripts\python.exe scripts\tracker_sync.py stats
```

## 红线

- 不自动投递/发送任何消息；验证码由用户手动完成
- 不编造画像与数据；假数据禁止落盘 data/raw
- 报告固定覆盖 `岗位分析报告.xlsx`，禁止时间戳堆积
- 版本号只在用户明示时修改（version-policy.md）

## 变更历史

- 2026-10-22：合并 zhipin-helper 与 YD-job-search → YD-job；导入生产脚本与真实数据（290 条）；补充契约层 7 份 + 测试锁 3 套 + 技能操作手册 3 份；V2EX 通道预留未启用。