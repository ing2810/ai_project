import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- 1. 스트림릿 페이지 설정 ---
st.set_page_config(page_title="서울시 연령별 인구 분석", layout="centered")

# --- 2. 데이터 로드 및 전처리 ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("population.csv", encoding='cp949')
    except Exception:
        df = pd.read_csv("population.csv", encoding='utf-8')
    
    # 공백 불일치 해결: 연속된 공백을 하나로 줄인 후 필터링
    df['행정구역_정리'] = df['행정구역'].astype(str).apply(lambda x: re.sub(r'\s+', ' ', x))
    
    # '서울특별시'가 포함되면서 '구 (' 형태를 가진 행만 정확히 필터링
    df = df[df['행정구역_정리'].str.contains('서울특별시') & df['행정구역_정리'].str.contains('구 \(')]
    
    # 구 이름 깨끗하게 추출
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
st.write("선택한 연령대의 인구수가 가장 많은 **상위 10개 행정구**의 인구 크기를 비교합니다.")
selected_age = st.selectbox("기준이 될 연령대 선택", age_cols, index=3) # 기본값 '30~39세'

# 선택한 연령대 기준으로 내림차순 정렬 후 상위 10개 구 추출
top10_df = df.sort_values(by=selected_age, ascending=False).head(10)

# --- 5. 인터랙티브 꺾은선 그래프 그리기 (축 방향 변경) ---
# [변경 포인트] x축을 '구_이름'으로, y축을 선택한 연령대('selected_age')로 지정했습니다.
fig = px.line(
    top10_df, 
    x='구_or_이름' if '구_or_이름' in top10_df.columns else '구_이름', 
    y=selected_age, 
    markers=True,  # 꺾은선 점 표시
    title=f"👉 '{selected_age}' 인구수 상위 10개 구 비교",
    labels={'구_이름': '행정구 (District)', selected_age: '인구수 (Population)'},
    template='plotly_white'
)

# 그래프 선 및 마커 스타일링, 마우스 오버 팝업 설정
fig.update_traces(
    line=dict(color='#FF69B4', width=3),  # 선 두께 및 색상 (핫핑크 계열)
    marker=dict(size=8, color='#C71585'), # 마커 크기 및 색상
    hovertemplate="<b>%{x}</b><br>선택 연령대: " + selected_age + "<br>인구수: %{y:,}명<extra></extra>" 
)

# 그래프 배경색(하늘색) 및 레이아웃 설정
fig.update_layout(
    plot_bgcolor='#E6F2F7',   # 그래프 내부 하늘색
    paper_bgcolor='#E6F2F7',  # 그래프 외부 배경 하늘색
    title_font=dict(size=15, color='#333333'),
    xaxis=dict(showgrid=True, gridcolor='white', tickfont=dict(size=12)),
    yaxis=dict(showgrid=True, gridcolor='white', tickformat=',d'), # Y축 콤마 표시
    margin=dict(l=50, r=40, t=60, b=50)
)

# 스트림릿 화면에 그래프 렌더링
st.plotly_chart(fig, use_container_width=True)

# --- 6. 데이터 테이블 보기 ---
with st.expander("순위 데이터 요약 보기 (상위 10개 구)"):
    display_df = top10_df[['구_이름'] + age_cols].copy()
    display_df = display_df.rename(columns={'구_이름': '행정구'}).set_index('행정구')
    st.dataframe(display_df, use_container_width=True)
