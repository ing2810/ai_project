import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- 1. 스트림릿 페이지 설정 ---
st.set_page_config(page_title="서울시 연령별 인구 분석", layout="centered")

# --- 2. 데이터 로드 및 전처리 (정밀 수정) ---
@st.cache_data
def load_data():
    # 내부 인코딩 오류 방지를 위해 cp949와 utf-8 순차 시도
    try:
        df = pd.read_csv("population.csv", encoding='cp949')
    except Exception:
        df = pd.read_csv("population.csv", encoding='utf-8')
    
    # [수정] 공백 불일치 해결: 연속된 공백을 하나로 줄인 후 필터링
    df['행정구역_정리'] = df['행정구역'].astype(str).apply(lambda x: re.sub(r'\s+', ' ', x))
    
    # '서울특별시'가 포함되면서 '구 (' 형태를 가진 행만 정확히 필터링
    df = df[df['행정구역_정리'].str.contains('서울특별시') & df['행정구역_정리'].str.contains('구 \(')]
    
    # [수정] 구 이름 깨끗하게 추출 (예: '서울특별시 종로구 (1111000000)' -> '종로구')
    df['구_이름'] = df['행정구역_정리'].apply(lambda x: x.split()[1] if len(x.split()) > 1 else x)
    
    # 인구수 데이터 숫자형 변환 (문자열 내 따옴표, 쉼표 완벽 제거)
    age_cols = ['0~9세', '10~19세', '20~29세', '30~39세', '40~49세', '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상']
    for col in age_cols:
        df[col] = df[col].astype(str).str.replace('"', '').str.replace(',', '').astype(int)
        
    return df, age_cols

try:
    df, age_cols = load_data()
except Exception as e:
    st.error(f"데이터 파일 처리 중 오류가 발생했습니다. 에러: {e}")
    st.stop()

# --- 3. 제목 스타일링 ---
title_html = """
<div style="text-align: center; margin-bottom: 25px;">
    <h1 style="color: #000000; font-size: 2.3rem; font-weight: bold; border-bottom: 3px solid #FF69B4; display: inline-block; padding-bottom: 10px; font-family: sans-serif;">
        서울시 행정구별 인구수
    </h1>
</div>
"""
st.markdown(title_html, unsafe_allow_html=True)

# --- 4. UI 및 인터랙션 (나이대 선택) ---
st.write("선택한 연령대의 인구수가 가장 많은 **상위 10개 행정구**의 전체 연령별 추이를 비교합니다.")
selected_age = st.selectbox("기준이 될 연령대 선택", age_cols, index=3) # 기본값 '30~39세'

# 선택한 연령대 기준으로 내림차순 정렬 후 상위 10개 구 추출
top10_df = df.sort_values(by=selected_age, ascending=False).head(10)

# --- 5. 그래프를 위한 데이터 재구조화 (Melt) ---
# Plotly에서 여러 개의 꺾은선을 한 번에 제어하기 위해 가로축(Age)과 세로축(Population) 형태로 변환합니다.
plot_df = top10_df.melt(
    id_vars=['구_이름'], 
    value_vars=age_cols, 
    var_name='연령대', 
    value_name='인구수'
)

# --- 6. 인터랙티브 꺾은선 그래프 그리기 ---
# 요청사항 반영: 가로축(x) = 연령대, 세로축(y) = 인구수, 구분 기준 = 구_이름
fig = px.line(
    plot_df, 
    x='연령대', 
    y='인구수', 
    color='구_이름',
    markers=True,  # 선에 데이터 점(마커) 표시
    title=f"👉 '{selected_age}' 인구수 상위 10개 구의 연령별 추이 비교",
    labels={'연령대': '연령대 (Age)', '인구수': '인구수 (Population)', '구_이름': '행정구'},
    template='plotly_white',
    color_discrete_sequence=px.colors.sequential.RdPu_r # 분홍~보라 톤 계열 색상 배치
)

# 마우스 올렸을 때(Hover) 팝업 레이아웃 및 스타일 세부 설정
fig.update_traces(
    line=dict(width=2.5),
    marker=dict(size=6),
    hovertemplate="<b>%{color}</b><br>연령대: %{x}<br>인구수: %{y:,}명<extra></extra>" # 콤마 포맷팅 포함 팝업
)

# 그래프 배경색 설정 (요청하신 연한 하늘색 반영)
fig.update_layout(
    plot_bgcolor='#E6F2F7',   # 그래프 내부 하늘색
    paper_bgcolor='#E6F2F7',  # 그래프 외부 배경 하늘색
    title_font=dict(size=15, color='#333333'),
    xaxis=dict(showgrid=True, gridcolor='white'),
    yaxis=dict(showgrid=True, gridcolor='white', tickformat=',d'), # Y축 숫자 콤마 지정
    margin=dict(l=50, r=40, t=60, b=50),
    legend=dict(backgroundcolor='white', bordercolor='none')
)

# 스트림릿 화면에 그래프 렌더링
st.plotly_chart(fig, use_container_width=True)

# --- 7. 데이터 테이블 보기 ---
with st.expander("순위 데이터 요약 보기 (상위 10개 구)"):
    display_df = top10_df[['구_이름'] + age_cols].copy()
    display_df = display_df.rename(columns={'구_이름': '행정구'}).set_index('행정구')
    st.dataframe(display_df, use_container_width=True)
