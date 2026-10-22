import urllib.request
import json
import socket

def inspect_chrome_cdp():
    print("Inspecting Chrome debugging port 9222...")
    try:
        req = urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=3)
        tabs = json.loads(req.read().decode("utf-8"))
        print(f"Found {len(tabs)} active browser tabs/targets:")
        for idx, tab in enumerate(tabs, 1):
            print(f"  [{idx}] {tab.get('title')} -> {tab.get('url')}")
            if "v2ex.com" in tab.get("url", ""):
                print(f"       🎯 Matched target V2EX tab!")
    except Exception as e:
        print(f"Failed to connect to Chrome CDP port 9222: {e}")

if __name__ == "__main__":
    inspect_chrome_cdp()
