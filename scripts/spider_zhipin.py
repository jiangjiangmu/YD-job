# -*- coding: utf-8 -*-
"""YD-job 岗位采集脚本

复用本地已登录 BOSS直聘 的 Chrome（CDP 调试端口 9222），
在页面上下文中调用搜索 wapi，采集指定关键词/城市的岗位列表，
输出结构化数据到 data/raw_jobs.json（原始分页数据另存 data/raw_pages/）。

用法：
    .venv\\Scripts\\python.exe spider.py
"""
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime

import yaml
from websocket import create_connection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/ -> project root
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_PAGES_DIR = os.path.join(DATA_DIR, "raw_pages")
OUTPUT_PATH = os.path.join(DATA_DIR, "raw_jobs.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_zhipin_tab(port):
    """通过 CDP HTTP 接口找到 BOSS直聘 标签页"""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5) as r:
            tabs = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"[错误] 无法连接 Chrome 调试端口 {port}: {e}")
        print('       请先用调试参数启动 Chrome 并打开 BOSS直聘（已登录状态）：')
        print('       chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\Users\\jiang\\.dsh\\chrome-debug-profile"')
        return None
    for t in tabs:
        if t.get("type") == "page" and "zhipin.com" in (t.get("url") or ""):
            return t
    print("[错误] 调试 Chrome 中没有 zhipin.com 页面，请先打开 BOSS直聘 并确认已登录")
    return None


def build_fetch_js(keyword, city_code, page, page_size):
    params = {"scene": 1, "query": keyword, "city": city_code, "page": page, "pageSize": page_size}
    qs = "&".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in params.items())
    return (
        "(async () => {"
        f"const r = await fetch('/wapi/zpgeek/search/joblist.json?{qs}', {{credentials: 'include'}});"
        "const body = await r.text();"
        "return {status: r.status, body: body};"
        "})()"
    )


def cdp_eval(ws, js):
    """在页面上下文执行 JS（等待 Promise），返回序列化结果"""
    ws.send(json.dumps({
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {"expression": js, "awaitPromise": True, "returnByValue": True},
    }))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") != 1:
            continue
        res = msg.get("result", {})
        if "exceptionDetails" in res:
            detail = json.dumps(res.get("exceptionDetails", {}).get("exception", {}), ensure_ascii=False)
            raise RuntimeError(f"页面内执行异常: {detail[:300]}")
        return res.get("result", {}).get("value")


def navigate_and_wait(ws, url, settle_seconds=6.0):
    """让标签页导航到指定 URL 并等待页面稳定（用于正常化会话/重置风控状态）"""
    ws.send(json.dumps({"id": 1, "method": "Page.navigate", "params": {"url": url}}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == 1:
            break
    time.sleep(settle_seconds)


def normalize(job, keyword, city_code, page, fetched_at):
    """把 wapi 原始字段映射为扁平结构"""
    security_id = job.get("securityId", "")
    lid = job.get("lid", "")
    detail_url = f"https://www.zhipin.com/job_detail/{job.get('encryptJobId', '')}.html"
    if lid or security_id:
        detail_url += "?" + "&".join(filter(None, [f"lid={lid}" if lid else "", f"securityId={security_id}" if security_id else ""]))
    return {
        "job_name": job.get("jobName", ""),
        "salary_desc": job.get("salaryDesc", ""),
        "skills": job.get("skills") or [],
        "job_labels": job.get("jobLabels") or [],
        "experience": job.get("jobExperience", ""),
        "degree": job.get("jobDegree", ""),
        "city": job.get("cityName", ""),
        "district": job.get("areaDistrict", ""),
        "business_district": job.get("businessDistrict", ""),
        "company": job.get("brandName", ""),
        "industry": job.get("brandIndustry", ""),
        "company_scale": job.get("brandScaleName", ""),
        "company_stage": job.get("brandStageName", ""),
        "boss_name": job.get("bossName", ""),
        "boss_title": job.get("bossTitle", ""),
        "job_type": job.get("jobType"),
        "encrypt_job_id": job.get("encryptJobId", ""),
        "security_id": security_id,
        "lid": lid,
        "job_url": detail_url,
        "keyword": keyword,
        "city_code": str(city_code),
        "page": page,
        "fetched_at": fetched_at,
    }


def main():
    cfg = load_config()
    search = cfg.get("search") or {}
    port = int((cfg.get("browser") or {}).get("remote_debugging_port", 9222))
    spider_cfg = cfg.get("spider") or {}
    keywords = [str(k).strip() for k in (search.get("keywords") or [search.get("keyword") or "Python"]) if str(k).strip()]
    city_code = str(search.get("city_code", "101280600"))
    pages = int(search.get("pages", 1))
    page_size = int(search.get("page_size", 30))
    min_delay = float(spider_cfg.get("min_delay_seconds", 2.5))
    max_delay = float(spider_cfg.get("max_delay_seconds", 4.5))
    settle = float(spider_cfg.get("navigate_settle_seconds", 6))

    print("=== Zhipin Helper Spider ===")
    print(f"关键词: {'、'.join(keywords)} | 城市编码: {city_code} | 每词 {pages} 页 (每页 {page_size} 条)")

    tab = get_zhipin_tab(port)
    if not tab:
        return 1
    print(f"目标标签: {tab.get('title')}")
    print(f"页面 URL: {tab.get('url')}")

    os.makedirs(RAW_PAGES_DIR, exist_ok=True)
    ws = create_connection(tab["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
    fetched_at = datetime.now().isoformat(timespec="seconds")
    jobs = []
    def safe_name(s):
        return re.sub(r'[\\/:*?"<>|]', "_", s)

    kw_counts = {}
    try:
        for kw in keywords:
            print(f"\n>>> 关键词「{kw}」")
            kw_counts[kw] = 0
            search_url = f"https://www.zhipin.com/web/geek/jobs?query={urllib.parse.quote(kw)}&city={city_code}"
            print(f"  导航搜索页并等待 {settle:.0f}s ...")
            navigate_and_wait(ws, search_url, settle)
            for p in range(1, pages + 1):
                data = None
                ok = False
                for attempt in (1, 2):
                    try:
                        value = cdp_eval(ws, build_fetch_js(kw, city_code, p, page_size))
                        body = (value or {}).get("body", "")
                        data = json.loads(body)
                    except Exception as e:
                        data = None
                        print(f"[警告] 「{kw}」第 {p} 页第 {attempt} 次尝试异常: {e}")
                    if (data or {}).get("code") == 0:
                        ok = True
                        break
                    print(f"[警告] 「{kw}」第 {p} 页第 {attempt} 次尝试 code={(data or {}).get('code')} message={(data or {}).get('message')}")
                    if attempt == 1:
                        print("  重新导航页面后再试一次 ...")
                        navigate_and_wait(ws, search_url, settle + 4)
                if not ok:
                    print("  两次尝试均失败，跳过该关键词剩余页。")
                    break
                zp = data.get("zpData") or {}
                page_jobs = zp.get("jobList") or []
                raw_path = os.path.join(RAW_PAGES_DIR, f"{safe_name(kw)}_page_{p}.json")
                with open(raw_path, "w", encoding="utf-8") as f:
                    f.write(body)
                jobs.extend(normalize(j, kw, city_code, p, fetched_at) for j in page_jobs)
                kw_counts[kw] += len(page_jobs)
                print(f"  第 {p}/{pages} 页: {len(page_jobs)} 条 (hasMore={zp.get('hasMore')}, 「{kw}」累计 {kw_counts[kw]})")
                if not zp.get("hasMore"):
                    print("  已到该词最后一页。")
                    break
                if p < pages:
                    delay = random.uniform(min_delay, max_delay)
                    print(f"  等待 {delay:.1f}s ...")
                    time.sleep(delay)
            if kw_counts[kw]:
                print(f"  「{kw}」小计: {kw_counts[kw]} 条")
    finally:
        ws.close()

    # 去重
    seen, unique_jobs = set(), []
    for j in jobs:
        jid = j.get("encrypt_job_id")
        if jid and jid in seen:
            continue
        if jid:
            seen.add(jid)
        unique_jobs.append(j)

    result = {
        "meta": {
            "keywords": keywords,
            "city_code": city_code,
            "pages_per_keyword": pages,
            "fetched_at": fetched_at,
            "total_collected": len(jobs),
            "total_unique": len(unique_jobs),
        },
        "jobs": unique_jobs,
    }
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 简要统计
    k_salaries = []
    part_time = 0
    for j in unique_jobs:
        m = re.search(r"(\d+)-(\d+)K", j.get("salary_desc", ""), re.I)
        if m:
            k_salaries.append((float(m.group(1)) + float(m.group(2))) / 2)
        if re.search(r"元/(天|周|小时)", j.get("salary_desc", "")):
            part_time += 1
    print("\n=== 采集完成 ===")
    print(f"共采集 {len(jobs)} 条，去重后 {len(unique_jobs)} 条，已保存: {OUTPUT_PATH}")
    print("  分词统计: " + " | ".join(f"{k}:{v}" for k, v in kw_counts.items()))
    if k_salaries:
        print(f"月薪(K)中位数参考: {sorted(k_salaries)[len(k_salaries)//2]:.0f}K | 范围 {min(k_salaries):.0f}-{max(k_salaries):.0f}K（按/天计酬的除外）")
    if part_time:
        print(f"其中按天计酬（多为实习/兼职）约 {part_time} 条")
    print("下一步: 运行 analyzer.py 生成匹配打分与 Excel 报告")
    return 0


if __name__ == "__main__":
    sys.exit(main())


