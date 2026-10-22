import urllib.request
import json
import os

def fetch_v2ex_api():
    url = "https://www.v2ex.com/api/v2/nodes/jobs/topics"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                topics = data.get("result", [])
                jobs = []
                for t in topics:
                    jobs.append({
                        "title": t.get("title"),
                        "company": t.get("node", {}).get("title", "V2EX社区"),
                        "salary": "面议",
                        "url": t.get("url"),
                        "source": "V2EX-API"
                    })
                out_path = os.path.join("data", "raw", "raw_jobs_v2ex_api.json")
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(jobs, f, ensure_ascii=False, indent=2)
                print(f"Successfully fetched {len(jobs)} jobs from V2EX API!")
                return jobs
    except Exception as e:
        print(f"V2EX API fetch failed: {e}")
    return []

if __name__ == "__main__":
    fetch_v2ex_api()
