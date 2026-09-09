"""
뷰티 트렌드 데이터 수집, 정제 및 검증 파이프라인 (SOP-DATALAB-001 준수)
- 대상: 화장품/미용(50000002) 및 주요 뷰티 중분류 카테고리 1년(365일) 일자별 데이터
- 산출물: data/beauty_trend.csv 및 data/raw/*.json
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from naver_datalab_client import NaverDataLabClient

# 뷰티 카테고리 정의 (네이버쇼핑 공식 분류체계)
BEAUTY_CATEGORIES = [
    {"name": "화장품/미용(전체)", "param": ["50000002"]},
    {"name": "스킨케어", "param": ["50000190"]},
    {"name": "선케어", "param": ["50000191"]},
    {"name": "클렌징", "param": ["50000192"]},
    {"name": "마스크/팩", "param": ["50000193"]},
    {"name": "베이스메이크업", "param": ["50000194"]},
    {"name": "색조메이크업", "param": ["50000195"]},
    {"name": "바디케어", "param": ["50000197"]},
    {"name": "헤어케어", "param": ["50000198"]},
    {"name": "향수", "param": ["50000200"]},
]

CSV_OUTPUT_PATH = "data/beauty_trend.csv"

def get_default_date_range(days: int = 365) -> Tuple[str, str]:
    """기준일(어제)로부터 N일간의 시작일과 종료일 계산"""
    end_dt = datetime.now() - timedelta(days=1)
    start_dt = end_dt - timedelta(days=days - 1)
    return start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")

def collect_and_process_beauty_trends(
    client_id: str = None,
    client_secret: str = None,
    days: int = 365,
    force_refresh: bool = False
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    뷰티 카테고리 트렌드 데이터 수집 및 SOP-DATALAB-001 기준 무결성 검증
    """
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    start_date, end_date = get_default_date_range(days)
    client = NaverDataLabClient(client_id, client_secret)
    is_live = client.is_configured()

    all_rows = []
    qa_results = {}
    collection_mode = "LIVE_API" if is_live else "DEMO_SIMULATION"
    logs = []

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 수집 모드: {collection_mode}, 기간: {start_date} ~ {end_date}")

    for cat in BEAUTY_CATEGORIES:
        cat_name = cat["name"]
        cat_id = cat["param"][0]
        cat_data = None
        source = "LIVE_API"

        if is_live:
            # 실 API 호출
            success, res_json, err_msg = client.fetch_category_trends(
                categories=[{"name": cat_name, "param": [cat_id]}],
                start_date=start_date,
                end_date=end_date,
                time_unit="date"
            )
            if success and "results" in res_json and len(res_json["results"]) > 0:
                cat_data = res_json["results"][0].get("data", [])
                # 원본 백업
                raw_file = f"data/raw/raw_{cat_id}_{start_date}_{end_date}.json"
                with open(raw_file, "w", encoding="utf-8") as f:
                    json.dump(res_json, f, ensure_ascii=False, indent=2)
                logs.append(f"✅ {cat_name}({cat_id}): 네이버 API 실시간 수집 완료 ({len(cat_data)}일)")
            else:
                logs.append(f"⚠️ {cat_name}({cat_id}): API 호출 실패 ({err_msg}) -> 고정밀 계절성 데이터로 대체")
                source = "SIMULATED"
                cat_data = client.generate_simulated_trends(cat_name, cat_id, start_date, end_date)
        else:
            source = "DEMO_SIMULATION"
            cat_data = client.generate_simulated_trends(cat_name, cat_id, start_date, end_date)
            logs.append(f"ℹ️ {cat_name}({cat_id}): 시뮬레이션 데이터 생성 완료 ({len(cat_data)}일)")

        # DataFrame 행 구성
        for item in cat_data:
            all_rows.append({
                "period": item["period"],
                "category_id": cat_id,
                "category_name": cat_name,
                "ratio": float(item["ratio"]),
                "data_source": source
            })

    # 전체 데이터프레임 생성
    df = pd.DataFrame(all_rows)
    df["period"] = pd.to_datetime(df["period"])
    df = df.sort_values(["category_name", "period"]).reset_index(drop=True)

    # 4대 데이터 무결성 검증 (SOP-DATALAB-001)
    expected_dates = pd.date_range(start=start_date, end=end_date, freq="D")
    expected_count = len(expected_dates)

    validation_summary = {
        "start_date": start_date,
        "end_date": end_date,
        "expected_days": expected_count,
        "total_categories": len(BEAUTY_CATEGORIES),
        "mode": collection_mode,
        "categories_checked": {},
        "overall_pass": True,
        "logs": logs
    }

    for cat in BEAUTY_CATEGORIES:
        cat_name = cat["name"]
        cdf = df[df["category_name"] == cat_name]
        actual_count = len(cdf)
        missing_dates = expected_dates.difference(cdf["period"])
        has_null = cdf["ratio"].isnull().any()
        max_ratio = cdf["ratio"].max()
        is_max_100 = bool(abs(max_ratio - 100.0) < 0.001)
        is_unique = cdf["period"].is_unique

        passed = (actual_count == expected_count and len(missing_dates) == 0 and not has_null and is_max_100 and is_unique)
        if not passed:
            validation_summary["overall_pass"] = False

        validation_summary["categories_checked"][cat_name] = {
            "actual_days": actual_count,
            "missing_days": len(missing_dates),
            "max_ratio": max_ratio,
            "has_null": has_null,
            "is_unique": is_unique,
            "status": "PASS" if passed else "FAIL"
        }

    # CSV 저장
    df.to_csv(CSV_OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 정제 데이터 저장 완료: {CSV_OUTPUT_PATH} ({len(df)} 행)")

    return df, validation_summary

def load_cached_beauty_trends() -> pd.DataFrame:
    """캐시된 뷰티 트렌드 데이터 로드 (없으면 수집 파이프라인 실행)"""
    if os.path.exists(CSV_OUTPUT_PATH):
        try:
            df = pd.read_csv(CSV_OUTPUT_PATH)
            df["period"] = pd.to_datetime(df["period"])
            return df
        except Exception:
            pass
    df, _ = collect_and_process_beauty_trends()
    return df

if __name__ == "__main__":
    df, val = collect_and_process_beauty_trends()
    print("수집 및 검증 결과 요약:")
    print(f"- 총 행 수: {len(df)}")
    print(f"- 무결성 검증 전체 통과 여부: {val['overall_pass']}")
