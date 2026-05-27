import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="서울 기온 역사 데이터 분석", layout="wide")

st.title("🌡️ 서울 연도별 특정 날짜 기온 변화 분석기")
st.write("1907년부터 2018년까지의 데이터 중, 원하는 월과 일을 선택해 연도별 기온 추이를 확인하세요.")

# 데이터 로드 및 전처리 함수 (캐싱 적용)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("seoul.csv", encoding="cp949")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv("seoul.csv", encoding="euc-kr")
        except UnicodeDecodeError:
            df = pd.read_csv("seoul.csv", encoding="utf-8", errors="ignore")
    
    # 1. 날짜 컬럼의 공백 및 탭 문자 제거
    df['날짜'] = df['날짜'].astype(str).str.strip()
    
    # 2. 날짜를 datetime 타입으로 변환
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    df = df.dropna(subset=['날짜'])
    
    # 3. 분석에 필요한 연, 월, 일 컬럼 추가
    df['연도'] = df['날짜'].dt.year
    df['월'] = df['날짜'].dt.month
    df['일'] = df['날짜'].dt.day
    
    # 4. 기온 데이터 숫자형 변환
    df['최고기온(℃)'] = pd.to_numeric(df['최고기온(℃)'], errors='coerce')
    df['최저기온(℃)'] = pd.to_numeric(df['최저기온(℃)'], errors='coerce')
    df['평균기온(℃)'] = pd.to_numeric(df['평균기온(℃)'], errors='coerce')
    
    return df

try:
    df = load_data()

    # [수정] 사이드바가 아닌 본문(창 내부)에 가로로 월/일 선택 상자 배치
    st.markdown("### 📅 조회할 날짜 선택")
    select_col1, select_col2 = st.columns(2)
    
    with select_col1:
        selected_month = st.selectbox("월(Month)", sorted(df['월'].unique()), index=9) # 기본값 10월
    
    with select_col2:
        available_days = sorted(df[df['월'] == selected_month]['일'].unique())
        selected_day = st.selectbox("일(Day)", available_days, index=0) # 기본값 1일

    # 데이터 필터링
    filtered_df = df[(df['월'] == selected_month) & (df['일'] == selected_day)].sort_values('연도')

    if not filtered_df.empty:
        st.subheader(f"📊 {selected_month}월 {selected_day}일의 연도별 기온 변화 추이")
        
        # 상단 요약 지표 (Metrics)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 관측 연도 수", f"{len(filtered_df)} 개년")
        with col2:
            valid_max = filtered_df.dropna(subset=['최고기온(℃)'])
            if not valid_max.empty:
                max_temp_row = valid_max.loc[valid_max['최고기온(℃)'].idxmax()]
                st.metric("역대 가장 높았던 기온", f"{max_temp_row['최고기온(℃)']} ℃", f"{int(max_temp_row['연도'])}년")
            else:
                st.metric("역대 가장 높았던 기온", "데이터 없음")
        with col3:
            valid_min = filtered_df.dropna(subset=['최저기온(℃)'])
            if not valid_min.empty:
                min_temp_row = valid_min.loc[valid_min['최저기온(℃)'].idxmin()]
                st.metric("역대 가장 낮았던 기온", f"{min_temp_row['최저기온(℃)']} ℃", f"{int(min_temp_row['연도'])}년")
            else:
                st.metric("역대 가장 낮았던 기온", "데이터 없음")

        # [수정] Plotly를 이용한 마우스 오버(툴팁) 지원 인터랙티브 꺾은선 그래프
        fig = go.Figure()

        # 최고기온 선 (파스텔 핑크: #FFB7B2)
        fig.add_trace(go.Scatter(
            x=filtered_df['연도'],
            y=filtered_df['최고기온(℃)'],
            mode='lines+markers',
            name='최고기온',
            line=dict(color='#FFB7B2', width=2.5),
            marker=dict(size=5),
            # 마우스 올렸을 때 나타날 툴팁 텍스트 커스텀 설정
            hovertemplate='<b>%{x}년 최고기온</b><br>🌡️ 기온: %{y} ℃<extra></extra>'
        ))

        # 최저기온 선 (파스텔 블루: #A8DADC)
        fig.add_trace(go.Scatter(
            x=filtered_df['연도'],
            y=filtered_df['최저기온(℃)'],
            mode='lines+markers',
            name='최저기온',
            line=dict(color='#A8DADC', width=2.5),
            marker=dict(size=5),
            hovertemplate='<b>%{x}년 최저기온</b><br>❄️ 기온: %{y} ℃<extra></extra>'
        ))

        # 그래프 레이아웃 및 툴팁 스타일 설정
        fig.update_layout(
            title=dict(
                text=f"Seoul Temperature Trend on {selected_month}/{selected_day} (1907-2018)",
                x=0.5, y=0.95, xanchor='center', yanchor='top',
                font=dict(size=16)
            ),
            xaxis_title="Year (연도)",
            yaxis_title="Temperature (기온, ℃)",
            hovermode="x unified",  # 마우스를 대면 같은 연도의 최고/최저 기온이 동시에 표시됩니다.
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=80, b=40)
        )
        
        # 격자선(Grid) 추가
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.3)', tickmode='linear', dtick=10)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.3)')

        # 스트림릿 웹 화면에 Plotly 그래프 출력 (화면 너비에 맞춤)
        st.plotly_chart(fig, use_container_width=True)
        
        # 상세 데이터 테이블 보여주기 익스팬더
        with st.expander("📄 선택한 날짜의 상세 데이터 보기"):
            st.dataframe(filtered_df[['연도', '평균기온(℃)', '최저기온(℃)', '최고기온(℃)']].reset_index(drop=True))
            
    else:
        st.warning("선택한 날짜에 해당하는 데이터가 존재하지 않습니다.")

except FileNotFoundError:
    st.error("❌ `seoul.csv` 파일을 찾을 수 없습니다. GitHub 저장소 구성을 다시 확인해 주세요.")
