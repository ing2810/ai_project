import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import urllib.request
import os

# --- 1. 스트림릿 페이지 설정 ---
st.set_page_config(page_title="서울시 인구 현황", layout="centered")

# --- 2. 한글 폰트 설정 (Streamlit Cloud 환경 대응) ---
@st.cache_data
def load_korean_font():
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        urllib.request.urlretrieve(font_url, font_path)
    return font_path

try:
    font_p = load_korean_font()
    font_name = fm.FontProperties(fname=font_p).get_name()
    plt.rc('font', family=font_name)
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
except Exception as e:
    st.warning(f"폰트 로드 중 오류 발생: {e}. 기본 폰트를 사용합니다.")

# --- 3. 데이터 로드 및 전처리 ---
@st.cache_data
def load_data():
    # 업로드된 population.csv 파일을 읽어옵니다. (앱과 같은 폴더에 있어야 합니다)
    df = pd.read_csv("population.csv")
    
    # '서울특별시' 전체 행 제외하고 구 단위 행정구역만 필터링 (구 코드가 있는 행)
    df = df[df['행정구역'].str.contains('구 \(')]
    
    # 깨끗한 구 이름 추출 (예: '서울특별시 서초구 (1165000000)' -> '서초구')
    df['구_이름'] = df['행정구역'].apply(lambda x: x.split()[1] if len(x.split()) > 1 else x)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 파일을 읽을 수 없습니다. 'population.csv' 파일이 같은 경로에 있는지 확인해주세요. 에러: {e}")
    st.stop()

# --- 4. 제목 스타일링 (분홍색 네온 글로우 효과) ---
neon_title_html = """
<style>
.neon-text {
    text-align: center;
    font-size: 2.5rem;
    font-weight: bold;
    color: #fff;
    text-shadow: 
        0 0 5px #fff,
        0 0 10px #ff007f,
        0 0 20px #ff007f,
        0 0 40px #ff007f;
    margin-bottom: 30px;
    padding: 10px;
    background-color: #111; /* 네온 효과가 돋보이도록 어두운 배경 박스 처리 */
    border-radius: 10px;
}
</style>
<div class="neon-text">서울시 행정구별 인구수</div>
"""
st.markdown(neon_title_html, unsafe_allow_html=True)

# --- 5. UI 및 인터랙션 ---
st.write("분석할 서울시 행정구를 선택하세요.")
selected_gu = st.selectbox("행정구 선택", df['구_이름'].unique())

# 선택된 구의 데이터 추출
gu_data = df[df['구_이름'] == selected_gu].iloc[0]

# 연령대 컬럼 정의 (가로축에 쓰일 나이 구간)
age_columns = [
    '2026년04월_거주자_10~19세', '2026년04월_거주자_20~29세', '2026년04월_거주자_30~39세',
    '2026년04월_거주자_40~49세', '2026년04월_거주자_50~59세', '2026년04월_거주자_60~69세',
    '2026년04월_거주자_70~79세', '2026년04월_거주자_80~89세', '2026년04월_거주자_90~99세',
    '2026년04월_거주자_100세 이상'
]
age_labels = ['10대', '20대', '30대', '40대', '50대', '60대', '70대', '80대', '90대', '100세 이상']

# 인구수 값 가져오기 및 숫자 변환 (쉼표 제거)
population_values = []
for col in age_columns:
    val = str(gu_data[col]).replace(',', '')
    population_values.append(int(val) if val.isdigit() else 0)

# --- 6. 그래프 그리기 (조건 반영) ---
fig, ax = plt.subplots(figsize=(10, 5))

# 조건 4-1: 그래프 바탕색을 연한 하늘색으로 설정
ax.set_facecolor('#E6F2F7')      # 차트 내부 배경 (Light Sky Blue 계열)
fig.patch.set_facecolor('#E6F2F7') # 차트 외부 배경

# 조건 4-2: 꺾은선 그래프의 색상을 분홍색(#FF69B4)으로 설정
ax.plot(age_labels, population_values, marker='o', linewidth=3, color='#FF69B4', markersize=8)

# 그래프 디테일 설정
ax.set_xlabel('연령대 (나이)', fontsize=12, fontweight='bold')
ax.set_ylabel('인구수 (명)', fontsize=12, fontweight='bold')
ax.set_title(f"[{selected_gu}] 연령대별 인구 분포", fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.5, color='white') # 가독성을 위한 하얀 그리드

# Y축 천단위 콤마 표시
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

# 스트림릿에 그래프 출력
st.pyplot(fig)

# 데이터 테이블 추가 확인용 (선택 사항)
with st.expander("상세 데이터 보기"):
    data_table = pd.DataFrame({'연령대': age_labels, '인구수(명)': population_values})
    st.dataframe(data_table.set_index('연령대'), use_container_width=True)
