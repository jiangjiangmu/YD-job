import os
import sys
import json
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_config():
    with open(os.path.join(ROOT, "config.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)

def check_fail(msg):
    raise AssertionError(msg)

def test_config_contract():
    cfg = load_config()
    # search 段
    assert isinstance(cfg.get("search", {}).get("keywords"), list) and cfg["search"]["keywords"], "search.keywords 必须为非空列表"
    assert cfg.get("search", {}).get("city_code"), "search.city_code 必填"
    # browser 段
    assert cfg.get("browser", {}).get("remote_debugging_port") == 9222, "browser.remote_debugging_port 必须为 9222"
    # spider 节奏（search-policy 契约：勿调小）
    assert cfg.get("spider", {}).get("min_delay_seconds", 0) >= 10, "min_delay_seconds 不得低于 10"
    assert cfg.get("spider", {}).get("max_delay_seconds", 0) >= 10, "max_delay_seconds 不得低于 10"
    # profile 段必填字段
    p = cfg.get("profile", {})
    for key in ("skills", "experience_years", "expected_salary", "own_degree",
                "preferred_regions", "excluded_keywords", "exclude_part_time"):
        assert key in p, f"profile.{key} 缺失"
    assert isinstance(p["skills"], list) and p["skills"], "profile.skills 非空"

def test_raw_jobs_schema():
    path = os.path.join(ROOT, "data", "raw_jobs.json")
    assert os.path.exists(path), "data/raw_jobs.json 缺失（先跑 job-search 采集）"
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    jobs = d.get("jobs", d) if isinstance(d, dict) else d
    assert isinstance(jobs, list) and len(jobs) >= 100, f"岗位数异常: {len(jobs)}"
    for j in jobs:
        for key in ("job_name", "salary_desc", "company", "city", "job_url"):
            assert j.get(key) not in (None, ""), f"岗位缺必填字段 {key}: {j.get('job_name')}"
        assert isinstance(j.get("skills"), list), "skills 必须为数组"
    # 去重：encrypt_job_id 存在时不得重复
    ids = [j.get("encrypt_job_id") for j in jobs if j.get("encrypt_job_id")]
    assert len(ids) == len(set(ids)), f"encrypt_job_id 存在重复 {len(ids) - len(set(ids))} 条"

def test_references_contract():
    refs = ["scoring-rubric.md", "search-policy.md", "delivery-contract.md",
            "data-contract.md", "profile-schema.md", "communication-templates.md",
            "version-policy.md"]
    for r in refs:
        assert os.path.exists(os.path.join(ROOT, "references", r)), f"references/{r} 缺失"

def test_skills_contract():
    for s in ("job-search", "job-analyze", "job-communication"):
        assert os.path.exists(os.path.join(ROOT, "skills", s, "SKILL.md")), f"skills/{s}/SKILL.md 缺失"

if __name__ == "__main__":
    test_config_contract()
    test_raw_jobs_schema()
    test_references_contract()
    test_skills_contract()
    print("[PASS] contract tests: config / raw_jobs schema / references / skills")