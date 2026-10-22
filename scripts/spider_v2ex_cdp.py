import urllib.request
import json
import os
import websocket

def fetch_v2ex_via_cdp():
    print("Connecting to Chrome debug port 9222...")
    try:
        req = urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=5)
        tabs = json.loads(req.read().decode("utf-8"))
        target_tab = None
        for tab in tabs:
            if "v2ex.com" in tab.get("url", ""):
                target_tab = tab
                break
        
        if not target_tab and tabs:
            target_tab = tabs[0] # Fallback to active tab
            
        if target_tab:
            print(f"Found target tab: {target_tab.get('title')} ({target_tab.get('url')})")
            ws_url = target_tab.get("webSocketDebuggerUrl")
            
            # Connect via websocket to extract job titles from DOM
            ws = websocket.create_connection(ws_url, suppress_origin=True)
            # Evaluate JS to get job topics
            script = """
            Array.from(document.querySelectorAll('.item_title a')).map(a => ({
                title: a.innerText,
                url: 'https://www.v2ex.com' + a.getAttribute('href')
            }))
            """
            msg = json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}})
            ws.send(msg)
            res = json.loads(ws.recv())
            ws.close()
            
            result = res.get("result", {}).get("result", {}).get("value", [])
            jobs = []
            for item in result:
                jobs.append({
                    "title": item.get("title"),
                    "company": "V2EX实战抓取",
                    "salary": "面议",
                    "url": item.get("url"),
                    "source": "V2EX-CDP"
                })
            
            out_path = os.path.join("data", "raw", "raw_jobs_v2ex_cdp.json")
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2)
            print(f"Successfully scraped {len(jobs)} V2EX job postings via Chrome CDP!")
            return jobs
    except Exception as e:
        print(f"CDP scraping failed: {e}")
    return []

if __name__ == "__main__":
    fetch_v2ex_via_cdp()
