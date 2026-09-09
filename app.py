"""
네이버 데이터랩 쇼핑인사이트 기반 뷰티 트렌드 리서치 대시보드
- Streamlit + Plotly 기반
- SOP-DATALAB-001 준수
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key

from naver_datalab_client import NaverDataLabClient
from data_pipeline import (
    BEAUTY_CATEGORIES,
    collect_and_process_beauty_trends,
    load_cached_beauty_trends
)

# 페이지 설정
st.set_page_config(
    page_title="네이버 뷰티 트렌드 리서치 대시보드",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 환경변수 로드
load_dotenv(override=True)
ENV_PATH = os.path.abspath(".env")

# 커스텀 CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-live {
        background-color: #DCFCE7;
        color: #15803D;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-demo {
        background-color: #FEF3C7;
        color: #B45309;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 1. 사이드바 컨트롤러
# -------------------------------------------------------------
st.sidebar.title("💄 뷰티 트렌드 설정")

# (1) API 키 설정 섹션
with st.sidebar.expander("🔑 네이버 API Key 설정", expanded=False):
    cur_client_id = os.getenv("NAVER_CLIENT_ID", "")
    cur_client_secret = os.getenv("NAVER_CLIENT_SECRET", "")
    
    input_id = st.text_input("Client ID", value=cur_client_id if cur_client_id != "your_client_id_here" else "")
    input_secret = st.text_input("Client Secret", value=cur_client_secret if cur_client_secret != "your_client_secret_here" else "", type="password")
    
    if st.button("💾 API Key 저장"):
        if input_id and input_secret:
            set_key(ENV_PATH, "NAVER_CLIENT_ID", input_id)
            set_key(ENV_PATH, "NAVER_CLIENT_SECRET", input_secret)
            os.environ["NAVER_CLIENT_ID"] = input_id
            os.environ["NAVER_CLIENT_SECRET"] = input_secret
            st.success("API Key가 .env에 저장되었습니다!")
            st.rerun()
        else:
            st.warning("Client ID와 Secret을 모두 입력해 주세요.")

# 클라이언트 생성 및 상태 확인
client = NaverDataLabClient()
is_live_mode = client.is_configured()

if is_live_mode:
    st.sidebar.markdown('<span class="badge-live">🟢 네이버 실시간 API 연동</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<span class="badge-demo">🟡 데모/시뮬레이션 모드 (API Key 필요)</span>', unsafe_allow_html=True)
    st.sidebar.caption("※ 상단 '네이버 API Key 설정'에서 유효한 키를 입력하면 실시간 데이터 수집이 활성화됩니다.")

st.sidebar.markdown("---")

# (2) 조회 기간 선택
st.sidebar.subheader("📅 조회 기간")
period_option = st.sidebar.radio(
    "기간 선택",
    options=["최근 1년 (365일)", "최근 6개월 (180일)", "최근 3개월 (90일)", "최근 1개월 (30일)", "사용자 직접 지정"],
    index=0
)

today = datetime.now().date()
max_end_date = today - timedelta(days=1)

if period_option == "최근 1년 (365일)":
    filter_start = max_end_date - timedelta(days=364)
    filter_end = max_end_date
elif period_option == "최근 6개월 (180일)":
    filter_start = max_end_date - timedelta(days=180)
    filter_end = max_end_date
elif period_option == "최근 3개월 (90일)":
    filter_start = max_end_date - timedelta(days=90)
    filter_end = max_end_date
elif period_option == "최근 1개월 (30일)":
    filter_start = max_end_date - timedelta(days=30)
    filter_end = max_end_date
else:
    date_range = st.sidebar.date_input(
        "조회 날짜 범위",
        value=(max_end_date - timedelta(days=90), max_end_date),
        min_value=datetime(2020, 1, 1).date(),
        max_value=max_end_date
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        filter_start, filter_end = date_range
    else:
        filter_start = max_end_date - timedelta(days=90)
        filter_end = max_end_date

st.sidebar.markdown("---")

# (3) 카테고리 선택
st.sidebar.subheader("🏷️ 뷰티 카테고리 필터")
all_cat_names = [c["name"] for c in BEAUTY_CATEGORIES]

col_btn1, col_btn2 = st.sidebar.columns(2)
select_all = col_btn1.button("전체 선택", use_container_width=True)
select_core = col_btn2.button("핵심 4종", use_container_width=True)

default_selection = ["스킨케어", "선케어", "색조메이크업", "베이스메이크업"]
if select_all:
    default_selection = all_cat_names
elif select_core:
    default_selection = ["스킨케어", "선케어", "색조메이크업", "베이스메이크업"]

selected_categories = st.sidebar.multiselect(
    "비교할 카테고리",
    options=all_cat_names,
    default=default_selection
)

if not selected_categories:
    selected_categories = ["스킨케어"]

st.sidebar.markdown("---")

# (4) 차트 부가 옵션
st.sidebar.subheader("⚙️ 차트 옵션")
show_ma = st.sidebar.checkbox("이동평균선(7일 MA) 적용", value=True)
chart_agg = st.sidebar.selectbox("집계 단위", ["일간 (Daily)", "주간 평균 (Weekly)", "월간 평균 (Monthly)"])

# (5) 데이터 새로고침 버튼
st.sidebar.markdown("---")
if st.sidebar.button("🔄 최신 데이터 수집 / 갱신", use_container_width=True):
    with st.spinner("네이버 데이터랩 쇼핑인사이트 수집 파이프라인 실행 중..."):
        df, validation = collect_and_process_beauty_trends(days=365, force_refresh=True)
        st.sidebar.success("데이터 갱신 완료!")
        st.rerun()

# -------------------------------------------------------------
# 2. 데이터 로드 및 필터링
# -------------------------------------------------------------
df = load_cached_beauty_trends()

# 날짜 필터 적용
mask = (df["period"].dt.date >= filter_start) & (df["period"].dt.date <= filter_end)
df_filtered = df.loc[mask].copy()

# 카테고리 필터 적용
df_selected = df_filtered[df_filtered["category_name"].isin(selected_categories)].copy()

# -------------------------------------------------------------
# 3. 메인 화면 레이아웃
# -------------------------------------------------------------
st.markdown('<div class="main-header">💄 네이버 쇼핑트렌드 뷰티 리서치 대시보드</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-header">네이버 데이터랩 쇼핑인사이트 API 연동 | 분석 기간: <b>{filter_start} ~ {filter_end}</b> '
    f'({(filter_end - filter_start).days + 1}일) | 데이터 소스: <code>{"네이버 쇼핑인사이트 실시간 API" if is_live_mode else "사전 검증 시뮬레이션"}</code></div>',
    unsafe_allow_html=True
)

# (1) KPI 메트릭 카드 영역
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

# KPI 1: 최근 7일 평균 1위 카테고리
recent_7d_cutoff = pd.to_datetime(filter_end) - timedelta(days=7)
recent_df = df_selected[df_selected["period"] >= recent_7d_cutoff]
if not recent_df.empty:
    cat_avg = recent_df.groupby("category_name")["ratio"].mean().sort_values(ascending=False)
    top_cat = cat_avg.index[0]
    top_cat_score = cat_avg.iloc[0]
else:
    top_cat = "N/A"
    top_cat_score = 0.0

# KPI 2: 전월 대비(MoM) 최고 성장 카테고리
last_30d_cutoff = pd.to_datetime(filter_end) - timedelta(days=30)
prev_30d_cutoff = last_30d_cutoff - timedelta(days=30)

cur_30d_avg = df_selected[df_selected["period"] >= last_30d_cutoff].groupby("category_name")["ratio"].mean()
prev_30d_avg = df_selected[(df_selected["period"] >= prev_30d_cutoff) & (df_selected["period"] < last_30d_cutoff)].groupby("category_name")["ratio"].mean()

growth_series = ((cur_30d_avg - prev_30d_avg) / prev_30d_avg * 100).dropna().sort_values(ascending=False)
if not growth_series.empty:
    growth_top_cat = growth_series.index[0]
    growth_top_val = growth_series.iloc[0]
else:
    growth_top_cat = "N/A"
    growth_top_val = 0.0

# KPI 3: 기간 내 최고 피크(Peak) 카테고리 및 날짜
if not df_selected.empty:
    peak_row = df_selected.loc[df_selected["ratio"].idxmax()]
    peak_cat = peak_row["category_name"]
    peak_date = peak_row["period"].strftime("%Y-%m-%d")
    peak_ratio = peak_row["ratio"]
else:
    peak_cat, peak_date, peak_ratio = "N/A", "N/A", 0.0

# KPI 4: 데이터 무결성 지표
total_records = len(df_selected)
expected_records = ((filter_end - filter_start).days + 1) * len(selected_categories)
completeness = (total_records / expected_records * 100) if expected_records > 0 else 100.0

with kpi_col1:
    st.metric("🏆 현재 트렌드 1위 분야", f"{top_cat}", f"최근 7일 지수 {top_cat_score:.1f}")

with kpi_col2:
    st.metric("📈 전월 대비 최고 상승(MoM)", f"{growth_top_cat}", f"{growth_top_val:+.1f}%")

with kpi_col3:
    st.metric("⚡ 기간 내 최고 피크", f"{peak_cat} ({peak_ratio:.1f})", f"{peak_date}")

with kpi_col4:
    st.metric("🛡️ 데이터 완결성 (SOP 기준)", f"{completeness:.1f}%", f"{total_records:,} 건 수집")

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. 탭 구성 (종합 트렌드 / 순위 및 분석 / SOP 무결성 리포트)
# -------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 트렌드 비교 시각화", "📋 분야별 순위 및 상세 분석", "🔍 SOP 무결성 검증 리포트"])

with tab1:
    st.subheader("카테고리별 일자별 검색 클릭 트렌드 추이")
    
    # 집계 단위 및 스무딩 처리
    plot_df = df_selected.copy()
    
    if show_ma and chart_agg == "일간 (Daily)":
        plot_df["display_ratio"] = plot_df.groupby("category_name")["ratio"].transform(lambda x: x.rolling(7, min_periods=1).mean())
        y_col = "display_ratio"
        y_title = "검색 클릭 트렌드 지수 (7일 이동평균)"
    elif chart_agg == "주간 평균 (Weekly)":
        plot_df["week"] = plot_df["period"].dt.to_period("W").apply(lambda r: r.start_time)
        plot_df = plot_df.groupby(["category_name", "week"])["ratio"].mean().reset_index()
        plot_df["period"] = plot_df["week"]
        y_col = "ratio"
        y_title = "주간 평균 클릭 트렌드 지수"
    elif chart_agg == "월간 평균 (Monthly)":
        plot_df["month"] = plot_df["period"].dt.to_period("M").apply(lambda r: r.start_time)
        plot_df = plot_df.groupby(["category_name", "month"])["ratio"].mean().reset_index()
        plot_df["period"] = plot_df["month"]
        y_col = "ratio"
        y_title = "월간 평균 클릭 트렌드 지수"
    else:
        y_col = "ratio"
        y_title = "일자별 클릭 트렌드 지수 (0~100)"

    # Plotly 메인 라인 차트
    fig_line = px.line(
        plot_df,
        x="period",
        y=y_col,
        color="category_name",
        labels={"period": "일자", y_col: y_title, "category_name": "분야"},
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    fig_line.update_layout(
        hovermode="x unified",
        height=450,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, 105])
    )
    fig_line.update_traces(line=dict(width=2.5))
    st.plotly_chart(fig_line, use_container_width=True)

    # 하단 2열 보조 차트
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("분야별 기간 평균 클릭 지수")
        cat_mean_df = df_selected.groupby("category_name")["ratio"].mean().reset_index().sort_values("ratio", ascending=True)
        fig_bar = px.bar(
            cat_mean_df,
            x="ratio",
            y="category_name",
            orientation="h",
            labels={"ratio": "평균 지수", "category_name": "분야"},
            template="plotly_white",
            color="ratio",
            color_continuous_scale="Viridis"
        )
        fig_bar.update_layout(height=320, margin=dict(l=20, r=20, t=10, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        st.subheader("분야별 상대 클릭 점유 비중")
        cat_sum_df = df_selected.groupby("category_name")["ratio"].sum().reset_index()
        fig_donut = px.pie(
            cat_sum_df,
            values="ratio",
            names="category_name",
            hole=0.45,
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_donut.update_layout(height=320, margin=dict(l=20, r=20, t=10, b=20))
        st.plotly_chart(fig_donut, use_container_width=True)

with tab2:
    st.subheader("뷰티 분야별 상세 성과 및 트렌드 순위표")

    # 순위 분석 테이블 생성
    analysis_rows = []
    for cat_name in selected_categories:
        cdf = df_selected[df_selected["category_name"] == cat_name].sort_values("period")
        if cdf.empty:
            continue
        
        # 최근 7일 평균
        c_7d = cdf[cdf["period"] >= pd.to_datetime(filter_end) - timedelta(days=7)]["ratio"].mean()
        # 직전 7일 평균
        p_7d = cdf[(cdf["period"] >= pd.to_datetime(filter_end) - timedelta(days=14)) & 
                   (cdf["period"] < pd.to_datetime(filter_end) - timedelta(days=7))]["ratio"].mean()
        wow = ((c_7d - p_7d) / p_7d * 100) if p_7d > 0 else 0.0

        # 최근 30일 vs 직전 30일
        c_30d = cdf[cdf["period"] >= pd.to_datetime(filter_end) - timedelta(days=30)]["ratio"].mean()
        p_30d = cdf[(cdf["period"] >= pd.to_datetime(filter_end) - timedelta(days=60)) & 
                    (cdf["period"] < pd.to_datetime(filter_end) - timedelta(days=30))]["ratio"].mean()
        mom = ((c_30d - p_30d) / p_30d * 100) if p_30d > 0 else 0.0

        # 최고 피크일
        p_row = cdf.loc[cdf["ratio"].idxmax()]
        p_date = p_row["period"].strftime("%Y-%m-%d")
        p_val = p_row["ratio"]

        # 트렌드 상태
        if mom >= 15.0:
            status = "🔥 급상승"
        elif mom >= 5.0:
            status = "📈 상승세"
        elif mom <= -10.0:
            status = "📉 하락세"
        else:
            status = "⚖️ 안정적"

        analysis_rows.append({
            "분야명": cat_name,
            "카테고리 ID": cdf["category_id"].iloc[0],
            "최근 7일 평균 지수": round(c_7d, 2),
            "WoW 변동률(%)": round(wow, 2),
            "MoM 변동률(%)": round(mom, 2),
            "기간 최고 지수": round(p_val, 2),
            "최고 피크 일자": p_date,
            "트렌드 진단": status
        })

    rank_df = pd.DataFrame(analysis_rows).sort_values("최근 7일 평균 지수", ascending=False).reset_index(drop=True)
    rank_df.index = rank_df.index + 1
    rank_df.index.name = "순위"

    st.dataframe(
        rank_df.style.background_gradient(subset=["최근 7일 평균 지수"], cmap="Blues")
                     .format({"WoW 변동률(%)": "{:+.2f}%", "MoM 변동률(%)": "{:+.2f}%"}),
        use_container_width=True
    )

    # CSV 다운로드 버튼
    csv_bytes = df_selected.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="📥 선택된 뷰티 트렌드 데이터 CSV 다운로드",
        data=csv_bytes,
        file_name=f"naver_beauty_trends_{filter_start}_{filter_end}.csv",
        mime="text/csv"
    )

with tab3:
    st.subheader("🔍 데이터 무결성 검증 (SOP-DATALAB-001)")
    
    st.markdown("""
    본 검증은 [SOP-DATALAB-001 작업지시서](file:///c:/Users/wisebirds/Desktop/뷰티트렌드/docs/작업지시서_일자별_쇼핑트렌드_수집_및_검증.md)의 
    **4대 무결성 검증 기준**에 따라 자동 수행됩니다.
    """)

    qa_summary = []
    expected_days = (filter_end - filter_start).days + 1
    expected_range = pd.date_range(start=filter_start, end=filter_end, freq="D")

    for cat_name in selected_categories:
        cdf = df_selected[df_selected["category_name"] == cat_name]
        actual_days = len(cdf)
        missing_count = len(expected_range.difference(cdf["period"]))
        has_null = cdf["ratio"].isnull().any()
        is_unique = cdf["period"].is_unique
        max_ratio = cdf["ratio"].max()

        qa_pass = (actual_days == expected_days and missing_count == 0 and not has_null and is_unique)

        qa_summary.append({
            "분야명": cat_name,
            "기대 일수": f"{expected_days}일",
            "실제 수집 일수": f"{actual_days}일",
            "누락 일수": f"{missing_count}일",
            "피크 Ratio (Max 100)": round(max_ratio, 2),
            "결측치 여부": "없음 (정상)" if not has_null else "결측발견",
            "일자 고유성": "정상" if is_unique else "중복발견",
            "검증 판정": "✅ PASS" if qa_pass else "❌ FAIL"
        })

    st.dataframe(pd.DataFrame(qa_summary), use_container_width=True)

    with st.expander("📄 정제 데이터 원본 미리보기 (상위 50행)"):
        st.dataframe(df_selected.head(50), use_container_width=True)
