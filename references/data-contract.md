# YD-job 数据契约（Data Contract）v1

> 定义 `data/raw_jobs.json` 的 schema 与去重规则。多平台采集器输出必须归一化为本 schema。

## 1. 顶层结构

```json
{
  "meta": {
    "city_code": "101280600",
    "keywords": ["运维", "IT支持"],
    "pages": 2,
    "page_size": 30,
    "dedup_total": 290,
    "collected_at": "2026-10-20T21:30:00+08:00"
  },
  "jobs": [ ... ]
}
```

兼容旧格式：`{ "jobs": [...], "meta": {...} }`；亦允许纯数组（analyzer 自动兼容）。**新采集器必须输出带 meta 的对象结构。**

## 2. 岗位字段（必填 / 可选）

| 字段 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `job_name` | ✅ | str | 职位名称（排除词判定的目标字段） |
| `salary_desc` | ✅ | str | 原始薪资文案（`8K-12K` / `面议`） |
| `skills` | ✅ | list | 岗位技能标签（可为空数组） |
| `job_labels` | 可 | list | 标签（年限/学历等） |
| `experience` | 可 | str | 经验要求（`3-5年` / `经验不限`） |
| `degree` | 可 | str | 学历要求（`大专` / `本科` / `学历不限`） |
| `city` | ✅ | str | 城市 |
| `district` | 可 | str | 行政区（区域打分依据） |
| `business_district` | 可 | str | 商圈 |
| `company` | ✅ | str | 公司名（判重辅助键） |
| `industry` / `company_scale` / `company_stage` | 可 | str | 公司画像 |
| `boss_name` / `boss_title` | 可 | str | 触点信息 |
| `job_url` | ✅ | str | **岗位原始链接**（Excel 第 26 列使用；缺省则该行无链接） |
| `source` | ✅ | str | 平台通道标记（`zhipin` / `v2ex` / …） |
| `encrypt_job_id` | 可 | str | **去重主键**（平台岗位 ID） |
| `security_id` | 可 | str | 平台鉴权字段（排障用，不外发） |
| `job_type` | 可 | int | 0=全职；兼职/实习由调用方按 `exclude_part_time` 过滤 |

## 3. 去重规则

- 主键：`encrypt_job_id`（无则回退 `job_name + company + district` 拼接）
- 跨关键词、跨平台统一去重；`dedup_total` 记录去重后总数
- 同一岗位多次命中只保留 **source 为第一出现通道** 的一条

## 4. 隐私边界

- `security_id`、cookie、token 等鉴权敏感字段**禁止写入外部报告**（仅原始 json 内部保留用于排障）
- `data/岗位分析报告.xlsx` 不得包含任何字段的完整密钥/会话信息

## 5. 数据生命周期

- `data/raw_pages/`：各关键词分页原始返回（排障用，可周期性清理）
- `data/raw/`：预留多平台原始汇入区；**无真实数据时禁止留假数据占位文件**
- `data/reports/`：预留多平台聚合报表区（当前主报告在 `data/` 根）