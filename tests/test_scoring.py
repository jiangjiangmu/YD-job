import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import analyzer_engine as AE

PROFILE = {
    "skills": ["桌面运维", "运维", "Linux", "网络", "Python"],
    "years_of_experience": 4,
    "min_salary_k": 8,
    "max_salary_k": 12,
    "own_degree": "大专",
    "preferred_districts": ["宝安区", "南山区"],
    "excluded_keywords": ["外包", "驻场"],
}

def job(**over):
    base = {
        "job_name": "IT运维工程师", "salary_desc": "8-12K", "skills": ["运维", "Linux"],
        "experience": "3-5年", "degree": "大专", "district": "宝安区",
        "company": "测试公司", "city": "深圳", "job_url": "http://example.com/job",
    }
    base.update(over)
    return base

def test_weights_sum_100():
    assert sum(AE.WEIGHTS.values()) == 100, f"Weights 必须合计 100: {AE.WEIGHTS}"

def test_degree_levels():
    assert AE.degree_level("本科") == 3
    assert AE.degree_level("大专") == 2
    assert AE.degree_level("学历不限") == 0
    assert AE.degree_level(None) == -1
    assert AE.degree_level("未知学历") == -1

def test_parse_salary():
    assert AE.parse_salary("8K-12K")[0:2] == (8.0, 12.0)
    assert AE.parse_salary("8-12K")[2] == "k"
    assert AE.parse_salary("12K以上")[0] == 12.0
    assert AE.parse_salary("面议")[2] == "negotiable"
    assert AE.parse_salary("200元/天")[2] == "daily"
    assert AE.parse_salary("")[2] == "negotiable"

def test_parse_expected_salary():
    lo, hi = AE.parse_expected_salary("8K-12K")
    assert (lo, hi) == (8.0, 12.0)

def test_experience_unlimited():
    score, note = AE.experience_score("经验不限", 4)
    assert score == 15 * 0.8, f"经验不限应为 12 分: {score}"

def test_exclusion_penalty_minus20():
    r = AE.score_job(job(job_name="外包运维工程师"), PROFILE)
    r_clean = AE.score_job(job(), PROFILE)
    assert r["total"] <= r_clean["total"] - 20, f"排除词应至少 -20: {r_clean['total']} -> {r['total']}"

def test_degree_hardgate_downgrade():
    # 自身大专，岗位要求本科：满分岗位也应降一档（⭐必投 -> 去）
    r = AE.score_job(job(degree="本科"), PROFILE)
    band = AE.build_advice(r, PROFILE)[1]
    assert band == "去", f"学历硬门槛应降一档为「去」: {band}"

def test_band_thresholds():
    r_high = AE.score_job(job(), PROFILE)
    assert r_high["total"] >= 70, f"全匹配岗位应 >=70: {r_high['total']}"
    assert AE.build_advice(r_high, PROFILE)[0][1] == "⭐必投" or AE.build_advice(r_high, PROFILE)[1] == "⭐必投"
    r_low = AE.score_job(job(salary_desc="面议", degree="硕士", district="罗湖区"), PROFILE)
    b = AE.build_advice(r_low, PROFILE)[1]
    assert b in ("缓", "不去"), f"低分岗位应为缓/不去: {b}"

if __name__ == "__main__":
    test_weights_sum_100()
    test_degree_levels()
    test_parse_salary()
    test_parse_expected_salary()
    test_experience_unlimited()
    test_exclusion_penalty_minus20()
    test_degree_hardgate_downgrade()
    test_band_thresholds()
    print("[PASS] scoring unit tests: weights / salary / degree / exclusion / bands")