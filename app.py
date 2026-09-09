import os
import pandas as pd
import numpy as np
import datetime
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="뷰티 브랜드 SEARCH INTELLIGENCE",
    page_icon="💄",
    layout="wide"
)

# 2. 화이트 모드 전용 대시보드 CSS 스타일링
st.markdown("""
<style>
    /* 전체 배경 화이트 모드 및 글꼴 설정 */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    
    /* 헤더 타이틀 스타일 */
    .brand-header {
        font-size: 22px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #1a1d20;
        margin-bottom: 20px;
    }
    .brand-header span {
        font-size: 14px;
        font-weight: 500;
        color: #6c757d;
        margin-left: 10px;
    }

    /* KPI 요약 카드 스타일 */
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 600;
        color: #8c959f;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 20px;
        font-weight: 700;
        color: #212529;
    }
    .kpi-sub {
        font-size: 11px;
        font-weight: 500;
        color: #6c757d;
        margin-top: 2px;
    }
    .kpi-up { color: #d9381e; font-weight: 700; }
    .kpi-down { color: #0066cc; font-weight: 700; }

    /* 인사이트 요약 박스 */
    .insight-box {
        background-color: #fff9f5;
        border: 1px solid #ffd8c2;
        border-radius: 8px;
        padding: 16px 20px;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    .insight-title {
        font-size: 13px;
        font-weight: 700;
        color: #d9531e;
        margin-bottom: 8px;
    }
    .insight-list {
        font-size: 13px;
        color: #343a40;
        line-height: 1.7;
    }

    /* 탭 디자인 커스텀 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 2px solid #e9ecef;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        background-color: transparent;
        border: none;
        color: #6c757d;
        font-weight: 600;
        font-size: 14px;
        padding: 0 16px;
    }
    .stTabs [aria-selected="true"] {
        color: #1a1d20 !important;
        border-bottom: 3px solid #1a1d20 !important;
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. API Key 설정
try:
    NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except Exception:
    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

# 4. 사이드바 설정
st.sidebar.title("⚙️ SEARCH INTELLIGENCE 설정")

if NAVER_CLIENT_ID and NAVER_CLIENT_SECRET:
    st.sidebar.success("네이버 API 연동 완료")
else:
    st.sidebar.error("API 키 확인 필요")

st.sidebar.markdown("---")
st.sidebar.subheader("📅 기간 조건")
period_option = st.sidebar.radio(
    "기간 선택",
    ["최근 4주", "최근 13주", "최근 52주", "YTD", "전체"]
)

period_factors = {
    "최근 4주": {"days": 28, "factor": 1.0},
    "최근 13주": {"days": 91, "factor": 1.25},
    "최근 52주": {"days": 364, "factor": 1.6},
    "YTD": {"days": 180, "factor": 1.3},
    "전체": {"days": 365, "factor": 1.5}
}
current_factor = period_factors.get(period_option, {"days": 28, "factor": 1.0})["factor"]
current_days = period_factors.get(period_option, {"days": 28, "factor": 1.0})["days"]

st.sidebar.markdown("---")
st.sidebar.subheader("🏷️ 카테고리 필터")
default_categories = ["스킨케어", "선케어", "색조메이크업", "베이스메이크업"]
selected_categories = st.sidebar.multiselect(
    "유형 선택",
    options=["스킨케어", "선케어", "색조메이크업", "베이스메이크업", "클렌징", "마스크/팩"],
    default=default_categories
)

st.sidebar.markdown("---")
custom_keyword = st.sidebar.text_input("추가 세부 키워드 검색", "")

# 5. 상단 헤더
st.markdown('<div class="brand-header">BEAUTY BRAND <span>SEARCH INTELLIGENCE</span></div>', unsafe_allow_html=True)

# 6. 상단 대시보드 메인 탭
tab_overview, tab_brand, tab_trends, tab_category, tab_ai, tab_data = st.tabs([
    "Overview", "Brand Search", "Trends", "Category", "AI 소재가이드", "Data"
])

# 샘플 데이터 계산
base_data = {
    "카테고리": ["스킨케어", "색조메이크업", "선케어", "베이스메이크업"],
    "최근 7일 평균 지수": [round(54750 * current_factor, 0), round(25900 * current_factor, 0), round(18800 * current_factor, 0), round(12400 * current_factor, 0)],
    "WoW 변동률(%)": [9.1, -1.2, 15.4, -0.8],
    "YoY 변동률(%)": [-32.7, 3.4, 42.0, 1.2]
}
rank_df = pd.DataFrame(base_data)

if selected_categories:
    rank_df = rank_df[rank_df["카테고리"].isin(selected_categories)]

if custom_keyword.strip():
    new_row = pd.DataFrame({
        "카테고리": [f"🔍 {custom_keyword.strip()}"],
        "최근 7일 평균 지수": [round(35000 * current_factor, 0)],
        "WoW 변동률(%)": [18.2],
        "YoY 변동률(%)": [25.0]
    })
    rank_df = pd.concat([new_row, rank_df], ignore_index=True)

with tab_brand:
    # 7. KPI 요약 카드 6종 (상단 대시보드 레이아웃)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    total_query = int(rank_df["최근 7일 평균 지수"].sum()) if not rank_df.empty else 0
    
    with c1:
        st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-label">LATEST WEEK</div>
            <div class="kpi-value">FY27-23</div>
            <div class="kpi-sub">{total_query:,} 쿼리</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with c2:
        st.markdown('''
        <div class="kpi-card">
            <div class="kpi-label">WOW</div>
            <div class="kpi-value kpi-up">▲ 9.1%</div>
            <div class="kpi-sub">전 주 대비</div>
        </div>
        ''', unsafe_allow_html=True)

    with c3:
        st.markdown('''
        <div class="kpi-card">
            <div class="kpi-label">YOY</div>
            <div class="kpi-value kpi-down">▼ 32.7%</div>
            <div class="kpi-sub">vs FY26-23</div>
        </div>
        ''', unsafe_allow_html=True)

    with c4:
        st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-label">누적 쿼리</div>
            <div class="kpi-value">{total_query * 4:,}</div>
            <div class="kpi-sub">{period_option} 기준</div>
        </div>
        ''', unsafe_allow_html=True)

    with c5:
        st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-label">주평균</div>
            <div class="kpi-value">{int(total_query / 4):,}</div>
            <div class="kpi-sub">피크 FY27-23</div>
        </div>
        ''', unsafe_allow_html=True)

    with c6:
        st.markdown('''
        <div class="kpi-card">
            <div class="kpi-label">키워드 수</div>
            <div class="kpi-value">68</div>
            <div class="kpi-sub">전체 유형</div>
        </div>
        ''', unsafe_allow_html=True)

    # 8. 오늘의 인사이트 요약
    st.markdown('''
    <div class="insight-box">
        <div class="insight-title">오늘의 인사이트</div>
        <div class="insight-list">
            • <b>최근 주(FY27-23)</b> 54,750회 — WoW +9.1%, YoY -32.7%.<br>
            • <b>누적 점유 1위 유형은 스킨케어 (54.8%)</b> — 브랜드 인텐트 검색의 핵심 동력.<br>
            • <b>누적 톱 키워드</b>: 글로우 틴트 · 24,960 · 피크 FY27-23.<br>
            • <b>WoW 톱 상승 키워드</b>: 선케어 톤업 로션 (+328.6%).<br>
            • <b>WoW 톱 하락 키워드</b>: 베이스 메이크업 쿠션 (-100.0%) — 원인 점검 필요.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # 9. 차트 영역 (영역 추이 차트 + 도넛 차트)
    col_left, col_right = st.columns([1.5, 1])

    colors = ['#3385ff', '#ff6666', '#f2b035', '#28a745', '#9966ff', '#20c997']

    with col_left:
        st.subheader("유형별 주간 추이 (누적)")
        dates = pd.date_range(end=pd.Timestamp.now(), periods=current_days)
        trend_dict = {"날짜": dates}
        for idx, cat in enumerate(rank_df["카테고리"]):
            base_val = rank_df[rank_df["카테고리"] == cat]["최근 7일 평균 지수"].values[0]
            np.random.seed(idx + 10)
            noise = np.random.normal(0, base_val * 0.05, current_days)
            trend_dict[cat] = np.maximum(0, base_val + np.linspace(-base_val*0.2, base_val*0.3, current_days) + noise)
            
        trend_df = pd.DataFrame(trend_dict)
        trend_melted = trend_df.melt(id_vars=["날짜"], var_name="카테고리", value_name="검색쿼리")

        fig_area = px.area(
            trend_melted,
            x="날짜",
            y="검색쿼리",
            color="카테고리",
            color_discrete_sequence=colors,
            template="plotly_white"
        )
        fig_area.update_layout(
            height=380,
            hovermode="x unified",
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_area, use_container_width=True)

    with col_right:
        st.subheader("유형별 점유율")
        if not rank_df.empty:
            fig_donut = px.pie(
                rank_df,
                names="카테고리",
                values="최근 7일 평균 지수",
                hole=0.55,
                color_discrete_sequence=colors,
                template="plotly_white"
            )
            fig_donut.update_traces(textinfo='percent', hoverinfo='label+value+percent')
            fig_donut.update_layout(
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0)
            )
            st.plotly_chart(fig_donut, use_container_width=True)

# --- TAB Data (표 디자인 유지) ---
with tab_data:
    st.subheader("📋 검색 데이터 원본")
    if not rank_df.empty:
        max_val = float(rank_df["최근 7일 평균 지수"].max()) if rank_df["최근 7일 평균 지수"].max() > 0 else 100.0
        st.dataframe(
            rank_df,
            column_config={
                "WoW 변동률(%)": st.column_config.NumberColumn(format="%+.1f%%"),
                "YoY 변동률(%)": st.column_config.NumberColumn(format="%+.1f%%"),
                "최근 7일 평균 지수": st.column_config.ProgressColumn(
                    format="%d",
                    min_value=0,
                    max_value=max_val
                )
            },
            use_container_width=True
        )

# --- TAB AI 소재가이드 ---
with tab_ai:
    st.subheader("✍️ 퍼포먼스 마케팅 소재 소구점 아이디어")
    c_ai1, c_ai2 = st.columns(2)
    with c_ai1:
        st.info("🎯 **추천 메인 헤드카피**\n- \"검색량 폭발! 지금 스킨케어 안 쓰면 손해인 이유\"\n- \"환절기 피부 고민 완벽 해결!\"")
    with c_ai2:
        st.success("🎬 **추천 숏폼(Reels) 영상 구도**\n- **0~3초**: 제형 줌인 및 3초 피부 광채 비포애프터 연출\n- **CTA**: 프로필 링크에서 단독 기획전 확인")