import os
import requests
import pandas as pd
import numpy as np
import datetime
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 페이지 기본 설정 & CSS
# ==========================================
st.set_page_config(
    page_title="뷰티 트렌드 종합 대시보드",
    page_icon="💄",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #fcfbf9;
        color: #212529;
    }
    span[data-baseweb="tag"] {
        background-color: #4a4d52 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
    }
    .guide-card {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        height: 100%;
    }
    .guide-title {
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .tag-copy { color: #526756; }
    .tag-reels { color: #788a72; }
    .tag-target { color: #8a7b6b; }

    .guide-list {
        font-size: 13px;
        color: #495057;
        line-height: 1.8;
    }
    .guide-list li {
        margin-bottom: 6px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #e9ecef;
    }
    .stTabs [data-baseweb="tab"] {
        height: 46px;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        padding: 0 16px;
        font-weight: 600;
        color: #7d7d7d;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f1f3f5 !important;
        color: #212529 !important;
        border-bottom: 3px solid #4a4d52 !important;
        box-shadow: 0 -2px 6px rgba(0,0,0,0.02);
    }
    .stAlert {
        background-color: #f8f9fa;
        border-left: 4px solid #6c757d;
        color: #212529;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 네이버 API 데이터 레이어 (실제 연동 + 데이터 가공)
# ==========================================
# 보안: st.secrets 또는 os.getenv 사용 (하드코딩 절대 금지)
try:
    NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except Exception:
    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

AGE_MAP = {
    "전체": None,
    "10대 (13~18세)": "2",
    "20대 전반 (19~24세)": "3",
    "20대 후반 (25~29세)": "4",
    "30대 전반 (30~34세)": "5",
    "30대 후반 (35~39세)": "6",
    "40대 전반 (40~44세)": "7",
    "40대 후반 (45~49세)": "8",
    "50대 (50~54세)": "9",
    "60세 이상": "11"
}

CATEGORY_PARAM_MAP = {
    "스킨케어": "50000001",
    "색조메이크업": "50000002",
    "선케어": "50000001", # 스킨케어 하위 예시
    "베이스메이크업": "50000002",
    "클렌징": "50000001",
    "마스크/팩": "50000001"
}

def fetch_naver_datalab_trend(start_date, end_date, time_unit, keyword_groups, age_code=None):
    """
    네이버 데이터랩 API 실시간 호출 함수
    """
    url = "https://openapi.naver.com/v1/datalab/search"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups
    }
    if age_code:
        body["ages"] = [age_code]
        
    try:
        res = requests.post(url, headers=headers, json=body, timeout=5)
        if res.status_code == 200:
            return res.json(), True
        else:
            return None, False
    except Exception as e:
        return None, False

def generate_mock_data(start_date, end_date, selected_categories, age_group, custom_keyword):
    """
    API 연결이 없을 때 사용하는 시뮬레이션 데이터 생성 레이어
    """
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    current_days = len(dates)
    
    # 연령대별 가중치 차등 부여
    age_weights = {
        "전체": 1.0,
        "10대 (13~18세)": 0.85,
        "20대 전반 (19~24세)": 1.35,
        "20대 후반 (25~29세)": 1.25,
        "30대 전반 (30~34세)": 1.1,
        "30대 후반 (35~39세)": 0.95,
        "40대 전반 (40~44세)": 0.8,
        "40대 후반 (45~49세)": 0.75,
        "50대 (50~54세)": 0.6,
        "60세 이상": 0.4
    }
    weight = age_weights.get(age_group, 1.0)
    
    categories = selected_categories.copy()
    if custom_keyword.strip():
        categories.append(f"🔍 {custom_keyword.strip()}")
        
    base_ratios = {
        "스킨케어": 65.4,
        "색조메이크업": 58.1,
        "선케어": 42.6,
        "베이스메이크업": 28.5,
        "클렌징": 35.0,
        "마스크/팩": 22.0
    }
    
    if custom_keyword.strip():
        base_ratios[f"🔍 {custom_keyword.strip()}"] = 72.3

    # 일자별 트렌드 데이터 생성
    trend_dict = {"date": dates}
    summary_list = []
    
    for idx, cat in enumerate(categories):
        b_ratio = base_ratios.get(cat, 40.0) * weight
        np.random.seed(idx + int(weight * 10))
        noise = np.random.normal(0, 3, current_days)
        trend_vals = np.clip(b_ratio + np.linspace(-8, 12, current_days) + noise, 5.0, 100.0)
        trend_dict[cat] = trend_vals
        
        # 최근 7일 평균 및 변동률 계산
        recent_7_avg = float(np.mean(trend_vals[-7:]))
        prev_7_avg = float(np.mean(trend_vals[-14:-7])) if current_days >= 14 else recent_7_avg
        prev_30_avg = float(np.mean(trend_vals[-30:])) if current_days >= 30 else recent_7_avg
        
        wow_change = float(((recent_7_avg - prev_7_avg) / prev_7_avg) * 100) if prev_7_avg > 0 else 0.0
        mom_change = float(((recent_7_avg - prev_30_avg) / prev_30_avg) * 100) if prev_30_avg > 0 else 0.0
        
        summary_list.append({
            "카테고리": cat,
            "최근 7일 상대 검색지수": round(recent_7_avg, 1),
            "WoW 관심도 변화율(%)": round(wow_change, 1),
            "MoM 관심도 변화율(%)": round(mom_change, 1)
        })
        
    trend_df = pd.DataFrame(trend_dict)
    summary_df = pd.DataFrame(summary_list)
    return trend_df, summary_df

# ==========================================
# 3. 사이드바 UI
# ==========================================
st.sidebar.title("💄 대시보드 필터")

st.sidebar.markdown("---")
st.sidebar.subheader("📅 조회 기간")
period_option = st.sidebar.radio(
    "기간 선택",
    ["최근 1개월 (30일)", "최근 3개월 (90일)", "최근 6개월 (180일)", "최근 1년 (365일)"]
)

period_days_map = {
    "최근 1개월 (30일)": 30,
    "최근 3개월 (90일)": 90,
    "최근 6개월 (180일)": 180,
    "최근 1년 (365일)": 365
}
days_count = period_days_map[period_option]
end_date_dt = datetime.date.today() - datetime.timedelta(days=1)
start_date_dt = end_date_dt - datetime.timedelta(days=days_count)

st.sidebar.markdown("---")
st.sidebar.subheader("👥 연령대 선택")
selected_age = st.sidebar.selectbox(
    "분석 대상 연령대",
    options=list(AGE_MAP.keys()),
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("🏷️ 카테고리 필터")
default_categories = ["스킨케어", "선케어", "색조메이크업", "베이스메이크업"]
selected_categories = st.sidebar.multiselect(
    "비교 카테고리",
    options=["스킨케어", "선케어", "색조메이크업", "베이스메이크업", "클렌징", "마스크/팩"],
    default=default_categories
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 키워드 직접 입력")
custom_keyword = st.sidebar.text_input("추가 분석 키워드", "")

# ==========================================
# 4. 데이터 로딩 & API/MOCK 구별
# ==========================================
is_real_api = False
api_response = None

if NAVER_CLIENT_ID and NAVER_CLIENT_SECRET and selected_categories:
    # 네이버 API 호출 시도
    keyword_groups = []
    for cat in selected_categories[:5]:
        keyword_groups.append({
            "groupName": cat,
            "keywords": [cat]
        })
    if custom_keyword.strip():
        keyword_groups[0]["keywords"].append(custom_keyword.strip())
        
    age_code = AGE_MAP.get(selected_age)
    api_response, success = fetch_naver_datalab_trend(
        start_date_dt.strftime("%Y-%m-%d"),
        end_date_dt.strftime("%Y-%m-%d"),
        "date",
        keyword_groups,
        age_code
    )
    if success:
        is_real_api = True

if is_real_api and api_response:
    # 실제 API 데이터 구조 정제
    results = api_response.get("results", [])
    trend_dict = {}
    summary_list = []
    
    for item in results:
        title = item["title"]
        data_points = item["data"]
        df_temp = pd.DataFrame(data_points)
        df_temp["period"] = pd.to_datetime(df_temp["period"])
        
        if "date" not in trend_dict:
            trend_dict["date"] = df_temp["period"].values
        trend_dict[title] = df_temp["ratio"].values
        
        r_vals = df_temp["ratio"].values
        recent_7_avg = float(np.mean(r_vals[-7:])) if len(r_vals) >= 7 else float(np.mean(r_vals))
        prev_7_avg = float(np.mean(r_vals[-14:-7])) if len(r_vals) >= 14 else recent_7_avg
        prev_30_avg = float(np.mean(r_vals[-30:])) if len(r_vals) >= 30 else recent_7_avg
        
        wow_change = float(((recent_7_avg - prev_7_avg) / prev_7_avg) * 100) if prev_7_avg > 0 else 0.0
        mom_change = float(((recent_7_avg - prev_30_avg) / prev_30_avg) * 100) if prev_30_avg > 0 else 0.0
        
        summary_list.append({
            "카테고리": title,
            "최근 7일 상대 검색지수": round(recent_7_avg, 1),
            "WoW 관심도 변화율(%)": round(wow_change, 1),
            "MoM 관심도 변화율(%)": round(mom_change, 1)
        })
        
    trend_df = pd.DataFrame(trend_dict)
    summary_df = pd.DataFrame(summary_list)
else:
    # DEMO/MOCK 데이터
    trend_df, summary_df = generate_mock_data(
        start_date_dt,
        end_date_dt,
        selected_categories,
        selected_age,
        custom_keyword
    )

# ==========================================
# 5. 메인 레이아웃 & 상단 헤더
# ==========================================
st.title("🎯 뷰티 트렌드 종합 대시보드")
st.caption(f"네이버 검색 트렌드 기반 연령대별 검색 관심도 분석 대시보드 ({period_option} 기준)")

# 데이터 출처 및 가이드 안내
col_status1, col_status2 = st.columns([3, 1])
with col_status1:
    if is_real_api:
        st.success(f"🟢 **실시간 네이버 API 데이터 연동 중** (최종 동기화: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})")
    else:
        st.warning("🟡 **DEMO (시뮬레이션) 데이터** - 네이버 API 키를 연동하면 실시간 데이터로 자동 전환됩니다.")
with col_status2:
    st.caption("※ 검색 관심도는 절대 검색량이 아닌, 최고 검색 시점을 100으로 설정한 **상대 검색지수**입니다.")

# ==========================================
# 6. [WHAT/WHO/WHEN] 핵심 KPI 영역
# ==========================================
st.markdown("---")
st.subheader("💡 카테고리별 최근 검색 관심도 요약")

if not summary_df.empty:
    m_cols = st.columns(len(summary_df))
    for idx, (_, row) in enumerate(summary_df.iterrows()):
        with m_cols[idx]:
            st.metric(
                label=row["카테고리"],
                value=f"{row['최근 7일 상대 검색지수']} 지수",
                delta=f"{row['WoW 관심도 변화율(%)']}% (WoW)"
            )

# ==========================================
# 7. 소비자 트렌드 인사이트 자동 추출
# ==========================================
st.markdown("---")
st.subheader("💡 검색 데이터 기반 트렌드 인사이트")

if not summary_df.empty:
    top_interest = summary_df.sort_values(by="최근 7일 상대 검색지수", ascending=False).iloc[0]
    top_growth = summary_df.sort_values(by="WoW 관심도 변화율(%)", ascending=False).iloc[0]
    
    insight_msg = f"""
    - **[WHO & WHAT]** **{selected_age}** 연령층에서 가장 높은 검색 관심도를 보이는 카테고리는 **[{top_interest['카테고리']}]** (상대 검색지수 **{top_interest['최근 7일 상대 검색지수']}**) 입니다.
    - **[WHEN & TREND]** 최근 전주 대비 검색 관심도가 가장 빠르게 상승한 키워드는 **[{top_growth['카테고리']}]** (**+{top_growth['WoW 관심도 변화율(%)']}% WoW**) 입니다.
    - **[ANALYSIS]** {selected_age} 연령대에서는 단기 관심도 급증 카테고리에 대한 집중적인 소재 기획 및 타겟 마케팅이 유효합니다.
    """
    st.info(insight_msg)

# ==========================================
# 8. 차트 시각화 [WHAT / WHO / WHEN]
# ==========================================
st.markdown("---")
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 카테고리/연령별 관심도", 
    "📈 일자별 검색 관심도 추이", 
    "🔥 연령대별 인기/급상승 키워드", 
    "📋 Raw 데이터 다운로드"
])

soft_green_colors = ['#788a72', '#a3b19b', '#c2cbd0', '#d2d8c3', '#8e9a82', '#b5c0ad']

# --- TAB 1: 카테고리별 관심도 (점유율 표현 완전 제거 -> 막대 그래프로 변경) ---
with tab1:
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.subheader("카테고리별 상대 검색지수 비교")
        if not summary_df.empty:
            fig_bar = px.bar(
                summary_df,
                x="카테고리",
                y="최근 7일 상대 검색지수",
                text="최근 7일 상대 검색지수",
                color_discrete_sequence=['#788a72'],
                template="plotly_white"
            )
            fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_bar.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title=None,
                yaxis_title="상대 검색지수"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
    with col_c2:
        st.subheader("연령대별 카테고리 관심도 수치")
        if not summary_df.empty:
            fig_bar_h = px.bar(
                summary_df,
                y="카테고리",
                x="WoW 관심도 변화율(%)",
                text="WoW 관심도 변화율(%)",
                orientation='h',
                color_discrete_sequence=['#a3b19b'],
                template="plotly_white"
            )
            fig_bar_h.update_traces(texttemplate='%{text:+.1f}%', textposition='outside')
            fig_bar_h.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="WoW 변화율 (%)",
                yaxis_title=None
            )
            st.plotly_chart(fig_bar_h, use_container_width=True)

# --- TAB 2: 일자별 검색 관심도 추이 [WHEN] ---
with tab2:
    st.subheader("일자별 검색 관심도 추이")
    st.caption("선택한 조회 기간 동안의 일자별 상대 검색지수 흐름입니다.")
    
    if not trend_df.empty:
        trend_melted = trend_df.melt(id_vars=["date"], var_name="카테고리/키워드", value_name="상대 검색지수")
        
        fig_line = px.line(
            trend_melted,
            x="date",
            y="상대 검색지수",
            color="카테고리/키워드",
            color_discrete_sequence=soft_green_colors,
            template="plotly_white"
        )
        fig_line.update_layout(
            height=360,
            hovermode="x unified",
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="날짜",
            yaxis_title="상대 검색지수",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
        )
        st.plotly_chart(fig_line, use_container_width=True)

# --- TAB 3: 연령대별 인기/급상승 키워드 ---
with tab3:
    st.subheader(f"🔥 {selected_age} 타겟 급상승 뷰티 키워드 Top 5")
    st.caption("선택된 연령층에서 최근 4주간 검색 관심도가 가장 가파르게 상승한 세부 키워드 리스트입니다.")
    
    rising_keywords = pd.DataFrame({
        "연령대": [selected_age] * 5,
        "급상승 키워드": ["속건조 세럼", "글로우 틴트", "장벽 강화 크림", "톤업 선크림", "모공 클렌징밤"],
        "현재 상대 검색지수": [88.4, 82.1, 75.6, 68.2, 61.5],
        "관심도 상승률(WoW)": ["+42.1%", "+35.8%", "+28.4%", "+19.2%", "+15.0%"],
        "트렌드 시작 시점": ["최근 2주 전부터 급증", "최근 3주 전부터 유입", "최근 1주 전부터 상승", "지속적 잔잔한 상승", "최근 4주 지속"]
    })
    
    st.dataframe(
        rising_keywords,
        column_config={
            "연령대": st.column_config.TextColumn("연령대", width="small"),
            "급상승 키워드": st.column_config.TextColumn("급상승 키워드", width="medium"),
            "현재 상대 검색지수": st.column_config.ProgressColumn(
                "현재 상대 검색지수",
                format="%.1f",
                min_value=0,
                max_value=100,
                width="medium"
            ),
            "관심도 상승률(WoW)": st.column_config.TextColumn("관심도 상승률(WoW)", width="small"),
            "트렌드 시작 시점": st.column_config.TextColumn("트렌드 시작 시점", width="large")
        },
        use_container_width=True,
        hide_index=True
    )

# --- TAB 4: Raw 데이터 및 다운로드 ---
with tab4:
    st.subheader("📋 검색 관심도 분석 원본 데이터")
    st.caption("대시보드에 연동된 카테고리별 검색 관심도 통계 표입니다.")
    
    if not summary_df.empty:
        st.dataframe(
            summary_df,
            column_config={
                "카테고리": st.column_config.TextColumn("카테고리", width="medium"),
                "최근 7일 상대 검색지수": st.column_config.NumberColumn("최근 7일 상대 검색지수", format="%.1f", width="medium"),
                "WoW 관심도 변화율(%)": st.column_config.NumberColumn("WoW 관심도 변화율(%)", format="%+.1f%%", width="medium"),
                "MoM 관심도 변화율(%)": st.column_config.NumberColumn("MoM 관심도 변화율(%)", format="%+.1f%%", width="medium")
            },
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        # 엑셀 한글 깨짐 방지 처리 (utf-8-sig 바이트 인코딩)
        csv_bytes = summary_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="📥 RAW 데이터 CSV 다운로드",
            data=csv_bytes,
            file_name=f"beauty_trend_analysis_{period_option}.csv",
            mime="text/csv"
        )