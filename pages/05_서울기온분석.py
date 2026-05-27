import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 한글 폰트 설정 (스트림릿 클라우드 리눅스 환경 대응 및 로컬 환경 호환)
# 스트림릿 클라우드(Linux) 환경에서 기본 제공되는 한글 나눔 폰트를 지정합니다.
plt.rcParams['font.family'] = 'NanumGothic' or 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

st.set_page_config(page_title="서울 기온 역사 데이터 분석", layout="wide")

st.title("🌡️ 서울 연도별 특정 날짜 기온 변화 분석기")
st.write("1907년부터 2018년까지의 데이터 중, 원하는 월과 일을 선택해 연도별 기온 추이를 확인하세요.")

# 데이터 로드 및 전처리 함수 (캐싱 적용으로 속도 향상)
@st.cache_data
def load_data():
    # 데이터 불러오기
    df = pd.read_csv("seoul.csv")
    
    # 1. 날짜 컬럼의 공백 및 탭 문자 제거 (\t1907-10-01 -> 1907-10-01)
    df['날짜'] = df['날짜'].astype(str).str.strip()
    
    # 2. 날짜를 datetime 타입으로 변환 (에러 발생 시 NaT 처리)
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    
    # 결측치 제거 (날짜가 제대로 변환되지 않은 행)
    df = df.dropna(subset=['날짜'])
    
    # 3. 분석에 필요한 연, 월, 일 컬럼 추가
    df['연도'] = df['날짜'].dt.year
    df['월'] = df['날짜'].dt.month
    df['일'] = df['날짜'].dt.day
    
    # 4. 기온 데이터 숫자형 변환 및 결측치 처리
    df['최고기온(℃)'] = pd.to_numeric(df['최고기온(℃)'], errors='coerce')
    df['최저기온(℃)'] = pd.to_numeric(df['최저기온(℃)'], errors='coerce')
    
    return df

try:
    df = load_data()

    # 사이드바에서 월, 일 선택 UI 구성
    st.sidebar.header("📅 날짜 선택")
    selected_month = st.sidebar.selectbox("월(Month)을 선택하세요", sorted(df['월'].unique()), index=9) # 기본값 10월
    
    # 선택한 월에 존재하는 일(Day)만 필터링하여 제공
    available_days = sorted(df[df['월'] == selected_month]['일'].unique())
    selected_day = st.sidebar.selectbox("일(Day)을 선택하세요", available_days, index=0) # 기본값 1일

    # 사용자가 선택한 월/일 데이터로 필터링
    filtered_df = df[(df['월'] == selected_month) & (df['일'] == selected_day)].sort_values('연도')

    if not filtered_df.empty:
        st.subheader(f"📊 {selected_month}월 {selected_day}일의 연도별 기온 변화 추이")
        
        # 데이터프레임 요약 정보 보여주기
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 관측 연도 수", f"{len(filtered_df)} 개년")
        with col2:
            max_temp_row = filtered_df.loc[filtered_df['최고기온(℃)'].idxmax()]
            st.metric("역대 가장 높았던 기온", f"{max_temp_row['최고기온(℃)']} ℃", f"{int(max_temp_row['연도'])}년")
        with col3:
            min_temp_row = filtered_df.loc[filtered_df['최저기온(℃)'].idxmin()]
            st.metric("역대 가장 낮았던 기온", f"{min_temp_row['최저기온(℃)']} ℃", f"{int(min_temp_row['연도'])}년")

        # 꺾은선 그래프 그리기
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 요청하신 파스텔 핑크(#FFB7B2)와 파스텔 블루(#A8DADC) 색상 적용
        ax.plot(filtered_df['연도'], filtered_df['최고기온(℃)'], marker='o', markersize=4, 
                color='#FFB7B2', linewidth=2, label='최고기온 (Pastel Pink)')
        ax.plot(filtered_df['연도'], filtered_df['최저기온(℃)'], marker='o', markersize=4, 
                color='#A8DADC', linewidth=2, label='최저기온 (Pastel Blue)')
        
        # 그래프 디테일 설정
        ax.set_title(f"Seoul Temperature Trend on {selected_month}/{selected_day} (1907-2018)", fontsize=14, pad=15)
        ax.set_xlabel("Year (연도)", fontsize=11)
        ax.set_ylabel("Temperature (기온, ℃)", fontsize=11)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(loc='best', fontsize=10)
        
        # 스트림릿에 그래프 출력
        st.pyplot(fig)
        
        # 상세 데이터 테이블 보여주기 익스팬더
        with st.expander("📄 선택한 날짜의 상세 데이터 보기"):
            st.dataframe(filtered_df[['연도', '평균기온(℃)', '최저기온(℃)', '최고기온(℃)']].reset_index(drop=True))
            
    else:
        st.warning("선택한 날짜에 해당하는 데이터가 존재하지 않습니다.")

except FileNotFoundError:
    st.error("❌ `seoul.csv` 파일을 찾을 수 없습니다. GitHub 저장소에 `seoul.csv` 파일이 앱 코드와 같은 위치에 있는지 확인해 주세요.")
