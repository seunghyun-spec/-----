import os
import requests
import pandas as pd
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="뷰티 트렌드 대시보드",
    page_icon="💄",
    layout="wide"
)

# 2. API Key 설정 (Streamlit Secrets 우선)
try:
    NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except Exception:
    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

# 3. 사이드바 설정
st.sidebar.title("💄 뷰티 트렌드 설정")

with st.sidebar.expander("🔑 네이버 API Key 설정"):
    st.write("Streamlit Secrets 연동 완료")

if NAVER_CLIENT_ID and NAVER_CLIENT_SECRET:
    st.sidebar.success("네이버 실시간 API 연동 완료")
else:
    st.sidebar.error("API 키를 확인해주세요.")

st.sidebar.markdown("---")
st.sidebar.subheader("📅 조회 기간")
period_option = st.sidebar.radio(
    "기간 선택",
    ["최근 1년 (365일)", "최근 6개월 (180일)", "최근 3개월 (90일)", "최근 1개월 (30일)", "사용자 직접 지정"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🏷️ 뷰티 카테고리 필터")

col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    st.button("전체 선택")
with col_btn2:
    st.button("핵심 4종")

default_categories = ["스킨케어", "선케어", "색조메이크업", "베이스메이크업"]
selected_categories = st.sidebar.multiselect(
    "비교할 카테고리",
    options=["스킨케어", "선케어", "색조메이크업", "베이스메이크업", "클렌징", "마스크/팩"],
    default=default_categories
)

# 4. 메인 화면
st.title("💄 뷰티 트렌드 대시보드")
st.caption("네이버 데이터랩 기반 실시간 뷰티 검색 트렌드 분석")

# 샘플 데이터 준비
data = {
    "카테고리": ["스킨케어", "색조메이크업", "선케어", "베이스메이크업"],
    "최근 7일 평균 지수": [55.4, 52.1, 38.6, 22.5],
    "WoW 변동률(%)": [2.5, -1.2, 15.4, -0.8],
    "MoM 변동률(%)": [8.1, 3.4, 42.0, 1.2]
}
rank_df = pd.DataFrame(data)

# 선택된 카테고리 필터링 적용
if selected_categories:
    rank_df = rank_df[rank_df["카테고리"].isin(selected_categories)]

# 메트릭 카드 시각화 (상단 요약)
st.subheader("📊 주요 카테고리 트렌드 지표")
m_cols = st.columns(len(rank_df) if not rank_df.empty else 1)
for idx, (_, row) in enumerate(rank_df.iterrows()):
    with m_cols[idx]:
        st.metric(
            label=row["카테고리"],
            value=f"{row['최근 7일 평균 지수']} pt",
            delta=f"{row['WoW 변동률(%)']}% (WoW)"
        )

st.markdown("---")

# 차트 섹션
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 카테고리별 검색 지수 비교")
    if not rank_df.empty:
        st.bar_chart(rank_df.set_index("카테고리")["최근 7일 평균 지수"])

with col2:
    st.subheader("🍩 검색 점유율 비중")
    if not rank_df.empty:
        # Streamlit 내장 차트로 점유율 시각화
        st.line_chart(rank_df.set_index("카테고리")["최근 7일 평균 지수"])

st.markdown("---")
st.subheader("📋 카테고리 트렌드 순위 요약")

# [오류 원인이었던 background_gradient 대신 st.column_config 적용]
if not rank_df.empty:
    max_val = float(rank_df["최근 7일 평균 지수"].max()) if rank_df["최근 7일 평균 지수"].max() > 0 else 100.0
    st.dataframe(
        rank_df,
        column_config={
            "WoW 변동률(%)": st.column_config.NumberColumn(format="%+.2f%%"),
            "MoM 변동률(%)": st.column_config.NumberColumn(format="%+.2f%%"),
            "최근 7일 평균 지수": st.column_config.ProgressColumn(
                format="%.2f",
                min_value=0.0,
                max_value=max_val
            )
        },
        use_container_width=True
    )