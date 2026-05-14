import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="Global MBTI Explorer", layout="wide")

st.title("🌍 국가별 MBTI 분포 데이터 시각화")
st.markdown("데이터를 분석하여 국가별 MBTI 비율을 확인하세요. (1위 유형은 네온 핑크로 강조됩니다)")

# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv('countriesMBTI_16types.csv')
    return df

try:
    df = load_data()
    
    # 사이드바에서 국가 선택
    countries = df['Country'].unique()
    selected_country = st.sidebar.selectbox("분석할 국가를 선택하세요", countries)

    # 선택된 국가 데이터 추출 및 재구조화
    country_df = df[df['Country'] == selected_country].drop(columns=['Country']).T
    country_df.columns = ['Percentage']
    country_df = country_df.sort_values(by='Percentage', ascending=False).reset_index()
    country_df.columns = ['MBTI', 'Percentage']

    # 색상 설정 (1등은 네온 핑크, 나머지는 네온 그린 그라데이션)
    # 네온 그린 계열: #39FF14 (밝음) -> #0B6623 (어두움)
    colors = []
    n_rows = len(country_df)
    for i in range(n_rows):
        if i == 0:
            colors.append('#FF10F0')  # Neon Pink
        else:
            # 점진적으로 어두워지는 네온 그린 계산 (간단한 선형 보간 느낌)
            green_val = int(255 - (i * (200 / n_rows)))
            colors.append(f'rgb(57, {green_val}, 20)')

    # 플로틀리 그래프 생성
    fig = go.Figure(go.Bar(
        x=country_df['MBTI'],
        y=country_df['Percentage'],
        marker_color=colors,
        text=country_df['Percentage'].apply(lambda x: f'{x*100:.2f}%'),
        textposition='auto',
        hovertemplate='<b>MBTI: %{x}</b><br>비율: %{y:.4f}<extra></extra>'
    ))

    fig.update_layout(
        title=f"<b>{selected_country}</b>의 MBTI 유형별 분포",
        xaxis_title="MBTI 유형",
        yaxis_title="비율",
        template="plotly_dark", # 네온 컬러가 잘 보이도록 다크 모드 적용
        height=600,
        showlegend=False
    )

    # 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

    # 데이터 요약 정보
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"🏆 {selected_country} 1위 유형")
        top_type = country_df.iloc[0]
        st.metric(label=top_type['MBTI'], value=f"{top_type['Percentage']*100:.2f}%")

    with col2:
        st.subheader("📊 데이터 상세보기")
        st.write(country_df)

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.info("파일 이름이 'countriesMBTI_16types.csv'인지 확인해 주세요.")
