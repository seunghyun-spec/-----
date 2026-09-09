"""
네이버 데이터랩 쇼핑인사이트 API 클라이언트 모듈
- 공식 엔드포인트: POST https://openapi.naver.com/v1/datalab/shopping/categories
- 문서 참조: docs/03_데이터랩_쇼핑인사이트_API.md
"""

import os
import json
import time
import math
import random
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv

# .env 환경변수 로드
load_dotenv(override=True)

API_ENDPOINT = "https://openapi.naver.com/v1/datalab/shopping/categories"

class NaverDataLabClient:
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id or os.getenv("NAVER_CLIENT_ID", "").strip()
        self.client_secret = client_secret or os.getenv("NAVER_CLIENT_SECRET", "").strip()
        
    def is_configured(self) -> bool:
        """API 키가 실제 값으로 설정되어 있는지 확인"""
        dummy_keys = ["", "your_client_id_here", "your_client_secret_here", "none"]
        return bool(
            self.client_id and 
            self.client_secret and 
            self.client_id.lower() not in dummy_keys and 
            self.client_secret.lower() not in dummy_keys
        )

    def get_headers(self) -> Dict[str, str]:
        return {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "Content-Type": "application/json"
        }

    def fetch_category_trends(
        self,
        categories: List[Dict[str, Any]],
        start_date: str,
        end_date: str,
        time_unit: str = "date",
        device: str = "",
        gender: str = "",
        ages: Optional[List[str]] = None
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        쇼핑인사이트 분야별 트렌드 API 호출 (최대 3개 카테고리/요청)
        Returns: (success: bool, data: dict, error_message: str)
        """
        if not self.is_configured():
            return False, {}, "NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET이 설정되지 않았거나 기본 템플릿 값입니다."

        payload = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": time_unit,
            "category": categories,
            "device": device,
            "gender": gender,
            "ages": ages or []
        }

        try:
            response = requests.post(
                API_ENDPOINT,
                headers=self.get_headers(),
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                return True, response.json(), ""
            
            error_msg = f"HTTP {response.status_code}"
            try:
                err_data = response.json()
                error_msg += f" - {err_data.get('message', response.text)}"
            except Exception:
                error_msg += f" - {response.text}"

            if response.status_code == 403:
                error_msg += " (네이버 개발자 센터 > 내 애플리케이션 > API 설정에서 '데이터랩 (쇼핑인사이트)' 권한이 활성화되어 있는지 확인하세요)"
            elif response.status_code == 429:
                error_msg += " (일일 호출 한도 1,000회를 초과했습니다)"

            return False, {}, error_msg

        except requests.exceptions.RequestException as e:
            return False, {}, f"네트워크 요청 실패: {str(e)}"

    @staticmethod
    def generate_simulated_trends(
        category_name: str,
        category_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        실제 뷰티 카테고리 계절성/주간 패턴을 반영한 고정밀 시뮬레이션 데이터 생성기
        (API Key 미입력 시 대시보드 시연 및 사전 검증용)
        """
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        total_days = (end_dt - start_dt).days + 1

        # 카테고리별 특성 (기본치, 계절 피크 월, 진폭)
        season_profiles = {
            "50000191": {"name": "선케어", "peak_month": 6, "amplitude": 35.0, "base": 30.0},        # 6~7월 여름 피크
            "50000190": {"name": "스킨케어", "peak_month": 11, "amplitude": 25.0, "base": 55.0},      # 11~1월 환절기/겨울 피크
            "50000192": {"name": "클렌징", "peak_month": 7, "amplitude": 18.0, "base": 45.0},        # 여름/환절기
            "50000194": {"name": "베이스메이크업", "peak_month": 3, "amplitude": 22.0, "base": 50.0},  # 봄 개강/환절기
            "50000195": {"name": "색조메이크업", "peak_month": 4, "amplitude": 26.0, "base": 48.0},    # 봄/연말
            "50000193": {"name": "마스크/팩", "peak_month": 12, "amplitude": 24.0, "base": 40.0},      # 겨울 보습
            "50000198": {"name": "헤어케어", "peak_month": 8, "amplitude": 15.0, "base": 42.0},       # 여름 두피
            "50000197": {"name": "바디케어", "peak_month": 1, "amplitude": 28.0, "base": 38.0},       # 한겨울 건조
            "50000200": {"name": "향수", "peak_month": 2, "amplitude": 32.0, "base": 35.0},          # 2월 발렌타인/3월 화이트데이/5월 선물
            "50000002": {"name": "화장품/미용", "peak_month": 5, "amplitude": 20.0, "base": 60.0},     # 5월/연말
        }

        profile = season_profiles.get(category_id, {"name": category_name, "peak_month": 5, "amplitude": 20.0, "base": 50.0})
        peak_m = profile["peak_month"]
        amp = profile["amplitude"]
        base = profile["base"]

        random.seed(hash(category_id) % 100000)
        
        raw_ratios = []
        for i in range(total_days):
            cur_dt = start_dt + timedelta(days=i)
            # 1. 연간 계절성 (Sine Wave)
            month_angle = ((cur_dt.month - peak_m) % 12) / 12.0 * 2 * math.pi
            season_factor = math.cos(month_angle) * amp
            
            # 2. 주간 패턴 (일요일/월요일 쇼핑 클릭 증가)
            weekday_boost = 6.0 if cur_dt.weekday() in [0, 6] else 0.0
            
            # 3. 노이즈 및 간헐적 프로모션(올리브영 세일 등 분기별 이벤트)
            noise = random.uniform(-4.0, 4.0)
            promo_boost = 15.0 if (cur_dt.month in [3, 6, 9, 12] and 1 <= cur_dt.day <= 7) else 0.0

            val = base + season_factor + weekday_boost + promo_boost + noise
            raw_ratios.append((cur_dt.strftime("%Y-%m-%d"), max(5.0, val)))

        # 네이버 규격: 최고값을 정확히 100.0으로 정규화
        max_val = max(r[1] for r in raw_ratios)
        normalized = []
        for period_str, val in raw_ratios:
            norm_ratio = round((val / max_val) * 100.0, 4)
            normalized.append({
                "period": period_str,
                "ratio": norm_ratio
            })

        return normalized
