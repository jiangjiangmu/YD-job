import urllib.request
import json
import os

def scrape_v2ex_real():
    print("Fetching active targets from Chrome 9222...")
    try:
        req = urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=3)
        tabs = json.loads(req.read().decode("utf-8"))
        
        target_tab = None
        for tab in tabs:
            if "v2ex.com" in tab.get("url", ""):
                target_tab = tab
                break
        if not target_tab and tabs:
            target_tab = tabs[0]
            
        if target_tab:
            print(f"Target Tab found!")
            print(f"Title: {target_tab.get('title')}")
            print(f"URL: {target_tab.get('url')}")
            print(f"WebSocket: {target_tab.get('webSocketDebuggerUrl')}")
            
            temp_path = "C:\\Users\\jiang\\.dsh\\_tmp\\v2ex_tab_meta.json"
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(target_tab, f, ensure_ascii=False, indent=2)
            print(f"Successfully wrote tab meta to C temp: {temp_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scrape_v2ex_real()
