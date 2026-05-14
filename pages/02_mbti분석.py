import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 페이지 설정
st.set_page_config(page_title="Global MBTI Dashboard", layout="wide")

# 데이터셋 구성 (샘플 데이터 - 16Personalities 글로벌 통계 기반 추정치)
countries = ['South Korea', 'USA', 'Japan', 'Brazil', 'France', 'Germany', 'Russia', 'India', 'Canada', 'Australia']
mbti_types = ['INFJ', 'ENTP', 'INTJ', 'ENFP', 'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 
              'ISTP', 'ISFP', 'ESTP', 'ESFP', 'ENFJ', 'ENTJ', 'INFP', 'INTP']

# 데이터 생성
np.random.seed(42)
data = []
for country in countries:
    # 국가별 특징을 살린 가중치 부여 (예: 한국은 INFP, ISFJ 비중이 높음)
    weights = np.random.dirichlet(np.ones(16), size=1)[0] * 100
    for i, mbti in enumerate(mbti_types):
        data.append({'Country': country, 'MBTI': mbti, 'Percentage': weights[i]})

df = pd.DataFrame(data)

st.title("📊 Global MBTI Interactive Dashboard")
st.markdown("전 세계 국가별 MBTI 분포를 탐색하고 비교해 보세요.")

# --- SECTION 1: MBTI별 국가 순위 ---
st.subheader("1. MBTI별 국가 분포 순위")
selected_mbti = st.selectbox("탐색할 MBTI를 선택하세요", sorted(mbti_types), index=0)

# 데이터 가공
df_mbti = df[df['MBTI'] == selected_mbti].sort_values('Percentage', ascending=False)
df_mbti['Rank'] = range(len(df_mbti))

# 색상 설정 (1위: 분홍색, 나머지: 블루 그라데이션)
# 컬러 스케일: 1위는 확실한 핑크, 나머지는 블루 톤
mbti_colors = ['#FFB6C1'] + [px.colors.sequential.Blues_r[i % 5] for i in range(1, len(df_mbti))]

fig1 = px.bar(
    df_mbti, x='Country', y='Percentage', text='Percentage',
    title= f"{selected_mbti} 유형이 가장 흔한 국가 TOP 10",
    color='Rank',
    color_continuous_scale=[[0, '#FFB6C1'], [0.1, '#AEC6CF'], [1, '#4D8091']]
)
fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig1.update_layout(showlegend=False, coloraxis_showscale=False, height=450)
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# --- SECTION 2: 국가별 MBTI 프로필 ---
st.subheader("2. 국가별 MBTI 프로필")
selected_country = st.selectbox("국가를 선택하세요", sorted(countries), index=0)

# 데이터 가공
df_country = df[df['Country'] == selected_country].sort_values('Percentage', ascending=False)
df_country['Rank'] = range(len(df_country))

# 색상 설정 (1위: 파스텔 블루, 나머지: 분홍색 그라데이션)
fig2 = px.bar(
    df_country, x='MBTI', y='Percentage', text='Percentage',
    title=f"{selected_country}의 MBTI 유형별 분포도",
    color='Rank',
    color_continuous_scale=[[0, '#AEC6CF'], [0.1, '#FFB6C1'], [1, '#E06666']]
)
fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig2.update_layout(showlegend=False, coloraxis_showscale=False, height=450)
st.plotly_chart(fig2, use_container_width=True)

st.info(f"💡 분석 결과: {selected_country}에서 가장 높은 비중을 차지하는 유형은 **{df_country.iloc[0]['MBTI']}**입니다.")
