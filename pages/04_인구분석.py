import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import urllib.request
import os

# --- 1. 스트림릿 페이지 설정 ---
st.set_page_config(page_title="서울시 연령별 인구 분석", layout="centered")

# --- 2. 한글 폰트 다운로드 및 절대 경로 설정 (Streamlit Cloud 한글 깨짐 완벽 방지) ---
@st.cache_data
def load_korean_font():
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    font_path = os.path.abspath("NanumGothic.ttf")
    if not os.path.exists(font_path):
        urllib.request.urlretrieve(font_url, font_path)
    return font_path

try:
    font_p_path = load_korean_font()
    font_prop = fm.FontProperties(fname=font_p_path)
    # 전역 폰트 설정이 먹히지 않을 때를 대비해 각 텍스트 요소에 font_prop를 직접 주입합니다.
    plt.rc('font', family=font_prop.get_name())
    plt.rcParams['axes.unicode_minus'] = False
except Exception as e:
    st.warning(f"폰트 설정 중 알림: {e}")

# --- 3. 데이터 로드 및 전처리 ---
@st.cache_data
def load_data():
    # 파일 인코딩 예외 처리 (수정된 파일 구조 반영)
    try:
        df = pd.read_csv("population.csv", encoding='cp949')
    except Exception:
        df = pd.read_csv("population.csv", encoding='utf-8')
    
    # '서울특별시'가 포함되면서 '구' 단위인 행만 필터링 
    # (예: '서울특별시 종로구 (1111000000)' 형태만 남기고 '전국', '서울특별시' 전체 행은 제외)
    df = df[df['행정구역'].str.contains('서울특별시') & df['행정구역'].str.contains('구 \(')]
    
    # 깔끔한 구 이름 추출 (예: '서울특별시 서초구 (1165000000)' -> '서초구')
    df['구_이름'] = df['행정구역'].apply(lambda x: x.split()[1] if len(x.split()) > 1 else x)
    
    # 인구수 데이터가 문자열(쉼표 포함)인 경우 정수형으로 변환
    age_cols = ['0~9세', '10~19세', '20~29세', '30~39세', '40~49세', '50~59세', '60~69세', '70~79세', '80~89세', '90~99세', '100세 이상']
    for col in age_cols:
        df[col] = df[col].astype(str).str.replace(',', '').astype(int)
        
    return df, age_cols

try:
    df, age_cols = load_data()
except Exception as e:
    st.error(f"데이터 파일 처리 중 오류가 발생했습니다. 파일명과 컬럼을 확인해주세요. 에러: {e}")
    st.stop()

# --- 4. 제목 스타일링 (검은색 글씨 디자인) ---
title_html = """
<div style="text-align: center; margin-bottom: 25px;">
    <h1 style="color: #000000; font-size: 2.3rem; font-weight: bold; border-bottom: 3px solid #FF69B4; display: inline-block; padding-bottom: 10px;">
        서울시 행정구별 인구수
    </h1>
</div>
"""
st.markdown(title_html, unsafe_allow_html=True)

# --- 5. UI 및 인터랙션 (나이대 선택) ---
st.write("특정 연령대를 선택하면, 해당 연령대 인구가 가장 많은 **상위 10개 행정구**의 전체 인구 추이를 비교합니다.")
selected_age = st.selectbox("기준이 될 연령대 선택", age_cols, index=3) # 기본값 '30~39세'

# 선택한 연령대 기준으로 내림차순 정렬 후 상위 10개 구 추출
top10_df = df.sort_values(by=selected_age, ascending=False).head(10)

# --- 6. 그래프 그리기 (조건 반영) ---
fig, ax = plt.subplots(figsize=(11, 6))

# 조건 4: 그래프 바탕 연한 하늘색
ax.set_facecolor('#E6F2F7')      
fig.patch.set_facecolor('#E6F2F7') 

# 상위 10개 구를 하나씩 꺾은선 그래프로 추가
# 조건 4: 기본 선 색상은 분홍색 계열로 유지하되, 10개 선이 구분되도록 투명도(alpha)와 마커 스타일, 혹은 분홍/핫핑크 톤을 조합합니다.
# 완전히 똑같은 분홍색이면 구분이 안 되므로, matplotlib의 'spring' 이나 'RdPu' 핑크톤 컬러맵을 활용해 10개 선을 구분해줍니다.
colors = plt.cm.spring(iter([i/12 for i in range(10)])) 

for i, (_, row) in enumerate(top10_df.iterrows()):
    gu_name = row['구_이름']
    values = row[age_cols].values
    
    # 상위 1위 구는 눈에 띄는 진한 분홍색, 나머지는 점진적인 핑크/선 스타일 변화
    ax.plot(age_cols, values, marker='o', linewidth=2.5, label=gu_name, markersize=5)

# 그래프 레이블 및 폰트 깨짐 방지 설정
ax.set_xlabel('연령대', fontproperties=font_prop, fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('인구수 (명)', fontproperties=font_prop, fontsize=12, fontweight='bold', labelpad=10)
ax.set_title(f"👉 '{selected_age}' 인구수 상위 10개 구 비교", fontproperties=font_prop, fontsize=14, pad=15, color='#333333')

# 축 단위 글꼴 깨짐 방지 적용
for label in ax.get_xticklabels():
    label.set_fontproperties(font_prop)
for label in ax.get_yticklabels():
    label.set_fontproperties(font_prop)

# 범례(Legend) 표시 및 한글 적용
legend = ax.legend(loc='upper right')
for text in legend.get_texts():
    text.set_fontproperties(font_prop)

# 그리드 및 Y축 콤마 설정
ax.grid(True, linestyle='--', alpha=0.6, color='white')
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

# 스트림릿에 그래프 출력
st.pyplot(fig)

# --- 7. 데이터 테이블 탑 10 확인 ---
with st.expander("순위 데이터 요약 보기 (상위 10개 구)"):
    display_df = top10_df[['구_이름'] + age_cols].copy()
    display_df = display_df.rename(columns={'구_이름': '행정구'}).set_index('행정구')
    st.dataframe(display_df, use_container_width=True)
