import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="MBTI Neon Explorer", layout="wide")

# 네온 스타일 입히기
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    h1 { color: #FF10F0; text-shadow: 0 0 10px #FF10F0; }
    </style>
    """, unsafe_allow_html=True)

st.title("💖 Global MBTI Neon Dashboard")

# 2. 데이터 불러오기
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('countriesMBTI_16types.csv')
        # 컬럼명에 있을지 모를 공백 제거
        df.columns = df.columns.str.strip()
        return df
    except:
        return None

df = load_data()

if df is not None:
    # --- 핵심: 국가 선택 상자 만들기 ---
    # 데이터의 'Country' 컬럼에서 목록을 뽑아 사이드바에 넣습니다.
    country_list = sorted(df['Country'].unique().tolist())
    
    st.sidebar.header("설정")
    selected_country = st.sidebar.selectbox("보고 싶은 국가를 선택하세요 👇", country_list)

    # 선택된 국가의 데이터만 필터링
    selected_data = df[df['Country'] == selected_country].iloc[0]
    
    # MBTI 유형들만 따로 빼서 정렬 (Country 제외)
    mbti_types = [col for col in df.columns if col != 'Country']
    values = [selected_data[mbti] for mbti in mbti_types]
    
    # 그래프를 위한 데이터프레임 생성 및 정렬
    plot_df = pd.DataFrame({'MBTI': mbti_types, 'Value': values})
    plot_df = plot_df.sort_values(by='Value', ascending=False)

    # 3. 네온 컬러 그라데이션 설정
    colors = []
    for i in range(len(plot_df)):
        if i == 0:
            colors.append('#FF10F0') # 1등은 무조건 네온 핑크
        else:
            # 나머지는 순위에 따라 어두워지는 네온 그린
            green_val = max(50, 255 - (i * 12))
            colors.append(f'rgb(57, {green_val}, 20)')

    # 4. 플로틀리 막대 그래프
    fig = go.Figure(go.Bar(
        x=plot_df['MBTI'],
        y=plot_df['Value'],
        marker_color=colors,
        text=plot_df['Value'].apply(lambda x: f'{x*100:.1f}%'),
        textposition='outside'
    ))

    fig.update_layout(
        title=f"✨ {selected_country} MBTI 분포 (상위 유형 강조)",
        template="plotly_dark",
        yaxis_tickformat='.1%',
        xaxis={'categoryorder':'total descending'}
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # 간단한 요약
    st.info(f"💡 {selected_country}에서 가장 높은 비중을 차지하는 MBTI는 **{plot_df.iloc[0]['MBTI']}** 입니다.")

else:
    st.error("파일을 찾을 수 없습니다. 'countriesMBTI_16types.csv' 파일이 app.py와 같은 폴더에 있는지 확인해주세요!")
