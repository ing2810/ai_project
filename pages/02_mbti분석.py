import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="MBTI Neon Dashboard", layout="wide")

# 네온 스타일 적용
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    h1 { color: #FF10F0; text-shadow: 0 0 10px #FF10F0; font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

st.title("💖 MBTI World Explorer")

# 2. 데이터 로드 (오류 방지 로직 강화)
@st.cache_data
def load_data():
    try:
        # 파일 읽기
        df = pd.read_csv('countriesMBTI_16types.csv')
        # 모든 컬럼명의 앞뒤 공백 제거 및 첫 글자 대문자화
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"데이터 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

df = load_data()

if df is not None:
    # 3. 국가 선택 (사이드바)
    # 'Country' 컬럼이 있는지 확인
    if 'Country' in df.columns:
        countries = sorted(df['Country'].unique())
        selected_country = st.sidebar.selectbox("국가를 선택하세요", countries)
        
        # 4. 선택된 국가 데이터 추출
        country_data = df[df['Country'] == selected_country].iloc[0]
        
        # MBTI 유형(컬럼)들만 추출 (Country 제외)
        mbti_cols = [col for col in df.columns if col != 'Country']
        values = country_data[mbti_cols].values
        
        # 데이터프레임 재구성 및 정렬
        plot_df = pd.DataFrame({
            'MBTI': mbti_cols,
            'Value': values
        }).sort_values(by='Value', ascending=False)

        # 5. 네온 컬러 그라데이션 설정
        colors = []
        for i in range(len(plot_df)):
            if i == 0:
                colors.append('#FF10F0')  # 1등: 네온 핑크
            else:
                # 나머지는 네온 그린 계열로 어두워지는 그라데이션
                green_intensity = max(40, 255 - (i * 15))
                colors.append(f'rgb(57, {green_intensity}, 20)')

        # 6. 플로틀리 차트 생성
        fig = go.Figure(go.Bar(
            x=plot_df['MBTI'],
            y=plot_df['Value'],
            marker_color=colors,
            text=plot_df['Value'].apply(lambda x: f'{x*100:.1f}%'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>비율: %{y:.2%}<extra></extra>'
        ))

        fig.update_layout(
            title=f"✨ {selected_country} MBTI Analysis",
            template="plotly_dark",
            xaxis_title="MBTI Types",
            yaxis_tickformat='.1%',
            margin=dict(t=80, b=40, l=40, r=40),
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)
        
        # 7. 추가 정보 출력
        st.subheader(f"🏆 {selected_country}에서 가장 흔한 유형은 '{plot_df.iloc[0]['MBTI']}'입니다.")
        
    else:
        st.error("CSV 파일에 'Country' 컬럼이 존재하지 않습니다. 컬럼명을 확인해주세요.")
else:
    st.warning("데이터를 불러올 수 없습니다. 파일명을 'countriesMBTI_16types.csv'로 해서 app.py와 같은 위치에 올려주세요.")
