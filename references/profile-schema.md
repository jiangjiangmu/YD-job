# YD-job 求职者画像契约（Profile Schema）v1

> `config.yaml` 的 `profile:` 段是唯一事实源；`analyzer_engine.py` 读取后转换为运行时键。话术生成器也必须按本契约读取画像。

## 1. config.yaml profile 字段（必填）

| 字段 | 类型 | 说明 |
|---|---|---|
| `skills` | list[str] | 核心技能标签（打分命中与"命中技能/待补技能"依据） |
| `experience_years` | int | 工作年限（经验匹配依据） |
| `expected_salary` | str | 期望薪资，格式 `8K-12K`（运行时拆为 min/max K） |
| `own_degree` | str | 自身学历（须在学历分级表中：博士/硕士/本科/大专/中专/中技/高中/学历不限/初中） |
| `preferred_regions` | list[str] | 偏好区域（区域打分依据；运行时键 `preferred_districts`） |
| `excluded_keywords` | list[str] | 排除词（岗位名命中每项 -20） |
| `exclude_part_time` | bool | true=兼职/实习不参与打分，单独归附表 |
| `notes` | str | 叙事备注（话术生成参考，不参与打分） |

## 2. 运行时映射（analyzer 内部键）

| config 键 | 运行时键 |
|---|---|
| `skills` | `skills` |
| `experience_years` | `years_of_experience` |
| `expected_salary` | `min_salary_k` / `max_salary_k` |
| `own_degree` | `own_degree` |
| `preferred_regions` | `preferred_districts` |
| `excluded_keywords` | `excluded_keywords` |

## 3. search / browser / spider 段（采集配置）

| 段 | 键 | 说明 |
|---|---|---|
| `search` | `keywords` | 多关键词合并采集（兼容旧键 `keyword`） |
| `search` | `city_code` | 目标城市编码（深圳 101280600） |
| `search` | `pages` / `page_size` | 每关键词页数与每页条数 |
| `browser` | `remote_debugging_port` | CDP 调试端口（9222） |
| `spider` | `min_delay_seconds` / `max_delay_seconds` | 请求间隔（勿调小，见 search-policy） |
| `spider` | `navigate_settle_seconds` | 导航稳定等待 |

## 4. 画像变更纪律

- 画像只允许真实信息（来源：简历解析 / 能力清单 / 用户口头确认），禁止编造技能与年限
- 修改 `profile` 后必须重跑 `analyzer_engine.py` 使新画像生效
- 画像变更属于数据变更，**不要求升版本号**（版本号规则见 `version-policy.md`）