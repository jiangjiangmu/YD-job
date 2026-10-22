# -*- coding: utf-8 -*-
"""探测 BOSS直聘搜索 wapi 的返回结构（在已登录页面上下文中执行 fetch）"""
import json
import sys
import urllib.request

from websocket import create_connection

BASE_DIR = r"E:\AI\DeepSeek Harness\Vault\desktop\projects\YD-job"
OUT_PATH = BASE_DIR + r"\data\probe_joblist.json"


def main():
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=5).read().decode("utf-8"))
    page = next((t for t in tabs if t.get("type") == "page" and "zhipin.com" in t.get("url", "")), None)
    if not page:
        print("未找到 zhipin.com 页面标签")
        return 1
    print("目标标签:", page.get("title"))
    print("URL:", page.get("url"))
    ws = create_connection(page["webSocketDebuggerUrl"], timeout=40, suppress_origin=True)
    js = (
        "(async () => {"
        "const r = await fetch('/wapi/zpgeek/search/joblist.json?scene=1&query=Python&city=101280600&page=1&pageSize=30',"
        " {credentials: 'include'});"
        "const body = await r.text();"
        "return {status: r.status, body: body};"
        "})()"
    )
    ws.send(json.dumps({
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {"expression": js, "awaitPromise": True, "returnByValue": True},
    }))
    value = None
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") != 1:
            continue
        res = msg.get("result", {})
        if "exceptionDetails" in res:
            print("页面内执行异常:", json.dumps(res["exceptionDetails"], ensure_ascii=False)[:1000])
            ws.close()
            return 1
        value = res.get("result", {}).get("value")
        break
    ws.close()
    if not value:
        print("空返回")
        return 1
    print("HTTP status:", value.get("status"))
    body = value.get("body", "")
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(body)
    print("原始返回已存:", OUT_PATH, "| 长度:", len(body))
    try:
        data = json.loads(body)
    except Exception:
        print("非 JSON 返回，前 500 字符:")
        print(body[:500])
        return 1
    print("code:", data.get("code"), "| message:", data.get("message"))
    zp = data.get("zpData") or {}
    print("zpData keys:", sorted(zp.keys()))
    jobs = zp.get("jobList") or []
    print("jobList 数量:", len(jobs), "| hasMore:", zp.get("hasMore"))
    if jobs:
        all_keys = sorted({k for j in jobs for k in j})
        print("jobList 全字段:", json.dumps(all_keys, ensure_ascii=False))
        print("首条样例:")
        print(json.dumps(jobs[0], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

