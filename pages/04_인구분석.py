import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import urllib.request
import os
import numpy as np

# --- 1. 스트림릿 페이지 설정 ---
st.set_page_config(page_title="서울시 연령별 인구 분석", layout="centered")

# --- 2. 한글 폰트 다운로드 및 절대 경로 설정 ---
@st.cache_data
def load_korean_font():
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    font_path = os.path.abspath("NanumGothic.ttf")
    if not os.path.exists(font_path):
        urllib.request.urlretrieve(font_url, font_path)
    return font_path

try:
    font_p_path = load_korean_font()
    # [수정 포인트 1] 폰트를 Matplotlib 시스템에 정식 등록합니다.
    fm.font_manager.addfont(font_p_path)
    font_prop = fm.FontProperties(fname=font_p_path)
    font_name = font_prop.get_name()
    
    # [수정 포인트 2] 객체가 아닌 정식 등록된 '폰트 이름 문자열'을 넘겨줍니다.
    plt.rc('font', family=font_name)
    plt.rcParams['axes.unicode_minus'] = False
except Exception as e:
    st.warning(f"폰트 설정 중 알림: {e}")

# --- 3. 데이터 로드 및 전처리 ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("population.csv", encoding='cp949')
    except Exception:
        df = pd.read_csv("population.csv", encoding='utf-8')
    
    # '서울특별시'가 포함되면서 '구' 단위인 행만 필터링 
    df = df[df['행정구역'].str.contains('서울특별시') & df['행정구역'].str.contains('구 \(')]
    
    # 깨끗한 구 이름 추출
    df['구_이름'] = df['행정구역'].apply(lambda x: x.split()[1] if len(x.split()) > 1 else x)
    
    # 인구수 데이터 숫자형 변환 (쉼표 제거)
    age_cols = ['0~9세', '10~19세', '20~29세', '30~39세', '40~49세', '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상']
    for col in age_cols:
        df[col] = df[col].astype(str).str.replace(',', '').astype(int)
        
    return df, age_cols

try:
    df, age_cols = load_data()
except Exception as e:
    st.error(f"데이터 파일 처리 중 오류가 발생했습니다. 'population.csv' 파일 경로를 확인해주세요. 에러: {e}")
    st.stop()

# --- 4. 제목 스타일링 ---
title_html = """
<div style="text-align: center; margin-bottom: 25px;">
    <h1 style="color: #000000; font-size: 2.3rem; font-weight: bold; border-bottom: 3px solid #FF69B4; display: inline-block; padding-bottom: 10px; font-family: sans-serif;">
        서울시 행정구별 인구수
    </h1>
</div>
"""
st.markdown(title_html, unsafe_allow_html=True)

# --- 5. UI 및 인터랙션 (나이대 선택) ---
st.write("선택한 연령대의 인구수가 가장 많은 **상위 10개 행정구**의 전체 연령별 추이를 비교합니다.")
selected_age = st.selectbox("기준이 될 연령대 선택", age_cols, index=3)

# 선택한 연령대 기준으로 내림차순 정렬 후 상위 10개 구 추출
top10_df = df.sort_values(by=selected_age, ascending=False).head(10)

# --- 6. 그래프 그리기 ---
fig, ax = plt.subplots(figsize=(11, 6))

# 그래프 바탕 연한 하늘색 설정
ax.set_facecolor('#E6F2F7')      
fig.patch.set_facecolor('#E6F2F7') 

# 분홍색 그라데이션 컬러맵 적용
colors = plt.cm.RdPu(np.linspace(0.4, 0.9, 10))

# 상위 10개 구를 그래프에 선으로 추가
for i, (_, row) in enumerate(top10_df.iterrows()):
    gu_name = row['구_이름']
    values = row[age_cols].values
    
    markers = ['o', 'v', '^', '<', '>', 's', 'p', '*', 'h', 'D']
    
    # [가로축: age_cols, 세로축: values(population)로 정상 매핑되어 선을 그립니다]
    ax.plot(age_cols, values, marker=markers[i], linewidth=2.5, label=gu_name, color=colors[9-i], markersize=6)

# 그래프 레이블 설정
ax.set_xlabel('연령대 (Age)', fontproperties=font_prop, fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('인구수 (Population)', fontproperties=font_prop, fontsize=12, fontweight='bold', labelpad=10)
ax.set_title(f"👉 '{selected_age}' 인구수 상위 10개 구 비교", fontproperties=font_prop, fontsize=14, pad=15, color='#333333')

# 축 텍스트에 한글 폰트 적용
for label in ax.get_xticklabels():
    label.set_fontproperties(font_prop)
for label in ax.get_yticklabels():
    label.set_fontproperties(font_prop)

# 범례(Legend) 표시
legend = ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='none')
for text in legend.get_texts():
    text.set_fontproperties(font_prop)

# 그리드 및 Y축 콤마 설정
ax.grid(True, linestyle='--', alpha=0.6, color='white')
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

# 스트림릿에 그래프 출력
st.pyplot(fig)

# --- 7. 데이터 테이블 보기 ---
with st.expander("순위 데이터 요약 보기 (상위 10개 구)"):
    display_df = top10_df[['구_이름'] + age_cols].copy()
    display_df = display_df.rename(columns={'구_이름': '행정구'}).set_index('행정구')
    st.dataframe(display_df, use_container_width=True)
