#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""投递追踪 CRM 同步脚本（契约见 references/communication-templates.md）。

维护 data/投递追踪.md 的漏斗状态机：
    待沟通 → 已打招呼 → HR回复 → 面试邀约 → 面试 → 待结果 → 已拿Offer → 已入职 / 已结束

纪律（红线）：
- 本脚本只记录状态，绝不自动投递/发送任何消息
- 状态变更以用户确认为准

用法：
    python scripts/tracker_sync.py add --job "IT运维工程师" --company "某某科技" \
        --salary "9-11K" --channel "BOSS直聘" --score 70.7 --note "开场白已生成"
    python scripts/tracker_sync.py status --company "某某科技" --to "已打招呼" --note "上午发的"
    python scripts/tracker_sync.py list [--status 已打招呼]
    python scripts/tracker_sync.py stats
"""
import argparse
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/ -> 项目根
TRACKER_PATH = os.path.join(BASE_DIR, "data", "投递追踪.md")

TITLE = "# 📊 YD-job 求职全生命周期漏斗追踪 (CRM)"
HEADER = "| 岗位名称 | 公司名称 | 薪资 | 渠道 | 匹配得分 | 当前状态 | 沟通记录/备注 |"
SEPARATOR = "|---|---|---|---|---|---|---|"
COLUMNS = ["岗位名称", "公司名称", "薪资", "渠道", "匹配得分", "当前状态", "沟通记录/备注"]
FUNNEL = ["待沟通", "已打招呼", "HR回复", "面试邀约", "面试", "待结果", "已拿Offer", "已入职", "已结束"]


def _ensure_file(path):
    """文件不存在则创建带表头的空 CRM。"""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{TITLE}\n\n{HEADER}\n{SEPARATOR}\n")


def load_rows(path=TRACKER_PATH):
    """读取 markdown 表格，返回行 dict 列表（保持文件顺序）。"""
    _ensure_file(path)
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) != len(COLUMNS):
                continue
            if cells[0] == "岗位名称" or set(cells[0]) <= set("-"):
                continue  # 表头 / 分隔行
            rows.append(dict(zip(COLUMNS, cells)))
    return rows


def save_rows(rows, path=TRACKER_PATH):
    lines = [TITLE, "", HEADER, SEPARATOR]
    for r in rows:
        lines.append("| " + " | ".join(str(r[c]) for c in COLUMNS) + " |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def add_entry(path, job, company, salary, channel, score, note=""):
    """新增一条投递记录（状态默认：待沟通）。同公司同岗位拒绝重复。"""
    rows = load_rows(path)
    for r in rows:
        if r["公司名称"] == company and r["岗位名称"] == job:
            raise ValueError(f"已存在同公司同岗位记录: {company} / {job}")
    rows.append({
        "岗位名称": job, "公司名称": company, "薪资": salary, "渠道": channel,
        "匹配得分": str(score), "当前状态": FUNNEL[0],
        "沟通记录/备注": note or "-",
    })
    save_rows(rows, path)
    return rows


def set_status(path, company, to, note="", job=None):
    """推进状态（合法状态见 FUNNEL）。返回更新的记录数。"""
    if to not in FUNNEL:
        raise ValueError(f"非法状态: {to}（合法: {' / '.join(FUNNEL)}）")
    rows = load_rows(path)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    hit = 0
    for r in rows:
        if r["公司名称"] == company and (job is None or r["岗位名称"] == job):
            old = r["当前状态"]
            tail = f"[{stamp}] {old} → {to}" + (f"；{note}" if note else "")
            prev = r["沟通记录/备注"]
            r["沟通记录/备注"] = tail if prev in ("", "-") else f"{prev}；{tail}"
            r["当前状态"] = to
            hit += 1
    if hit == 0:
        raise ValueError(f"未找到公司为「{company}」的记录")
    save_rows(rows, path)
    return hit


def list_rows(path=TRACKER_PATH, status=None):
    rows = load_rows(path)
    if status:
        rows = [r for r in rows if r["当前状态"] == status]
    return rows


def stats(path=TRACKER_PATH):
    out = {}
    for r in load_rows(path):
        out[r["当前状态"]] = out.get(r["当前状态"], 0) + 1
    return out


def main():
    ap = argparse.ArgumentParser(description="投递追踪 CRM 同步（只记录，不自动发送）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="新增投递记录")
    p_add.add_argument("--job", required=True)
    p_add.add_argument("--company", required=True)
    p_add.add_argument("--salary", default="面议")
    p_add.add_argument("--channel", default="BOSS直聘")
    p_add.add_argument("--score", default="-")
    p_add.add_argument("--note", default="")

    p_st = sub.add_parser("status", help="推进状态")
    p_st.add_argument("--company", required=True)
    p_st.add_argument("--to", required=True, choices=FUNNEL)
    p_st.add_argument("--job", default=None, help="可选，同公司多岗位时指定")
    p_st.add_argument("--note", default="")

    p_ls = sub.add_parser("list", help="列出记录")
    p_ls.add_argument("--status", default=None, choices=FUNNEL)

    sub.add_parser("stats", help="分状态统计")

    args = ap.parse_args()
    if args.cmd == "add":
        add_entry(TRACKER_PATH, args.job, args.company, args.salary, args.channel, args.score, args.note)
        print(f"已添加: {args.company} / {args.job}（待沟通）")
    elif args.cmd == "status":
        n = set_status(TRACKER_PATH, args.company, args.to, args.note, args.job)
        print(f"已更新 {n} 条: {args.company} → {args.to}")
    elif args.cmd == "list":
        rows = list_rows(TRACKER_PATH, args.status)
        if not rows:
            print("（无记录）")
        for r in rows:
            print(f"[{r['当前状态']}] {r['公司名称']} | {r['岗位名称']} | {r['薪资']} | {r['匹配得分']}分 | {r['沟通记录/备注']}")
    elif args.cmd == "stats":
        st = stats(TRACKER_PATH)
        total = sum(st.values())
        print(f"总计 {total} 条：" + " | ".join(f"{k} {v}" for k, v in st.items()))


if __name__ == "__main__":
    main()