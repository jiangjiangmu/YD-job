# -*- coding: utf-8 -*-
"""tracker_sync 单元测试：CRM 读写与漏斗状态机（纯标准库，可直接运行）。"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tracker_sync as ts


def run():
    tmp = tempfile.mkdtemp(prefix="ydjob-tracker-")
    p = os.path.join(tmp, "投递追踪.md")

    # 1) add + 默认状态
    ts.add_entry(p, job="IT运维工程师", company="测试科技", salary="9-11K",
                 channel="BOSS直聘", score=70.7, note="开场白已生成")
    rows = ts.load_rows(p)
    assert len(rows) == 1 and rows[0]["当前状态"] == "待沟通"

    # 2) 重复添加必须被拒绝
    try:
        ts.add_entry(p, job="IT运维工程师", company="测试科技", salary="9-11K",
                     channel="BOSS直聘", score=70.7)
        raise AssertionError("重复添加未被拒绝")
    except ValueError:
        pass

    # 3) 非法状态必须被拒绝
    try:
        ts.set_status(p, "测试科技", "随便写的")
        raise AssertionError("非法状态未被拒绝")
    except ValueError:
        pass

    # 4) 推进状态 + 备注追加
    ts.set_status(p, "测试科技", "已打招呼", note="上午发的")
    rows = ts.load_rows(p)
    assert rows[0]["当前状态"] == "已打招呼"
    assert "上午发的" in rows[0]["沟通记录/备注"]
    assert "待沟通 → 已打招呼" in rows[0]["沟通记录/备注"]

    # 5) 过滤与统计
    assert len(ts.list_rows(p, status="已打招呼")) == 1
    assert len(ts.list_rows(p, status="已拿Offer")) == 0
    st = ts.stats(p)
    assert st.get("已打招呼") == 1 and sum(st.values()) == 1

    # 6) 更新不存在的公司必须报错
    try:
        ts.set_status(p, "不存在公司", "面试")
        raise AssertionError("未知公司未被拒绝")
    except ValueError:
        pass

    print("[PASS] tracker tests: add / dedupe / invalid-status / transition / list / stats")


if __name__ == "__main__":
    run()