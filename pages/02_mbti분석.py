import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="Global MBTI Explorer", layout="wide")

# 2. 샘플 데이터 (국가별 MBTI 분포 예시 데이터)
# 실제 프로젝트 시에는 정확한 통계 CSV 파일을 로드하여 사용하세요.
data = {
    'Country': ['South Korea', 'USA', 'Japan', 'Brazil', 'France', 'India', 'Canada', 'Australia', 'Germany', 'UK'],
    'INFJ': [2.1, 1.5, 1.2, 1.8, 1.6, 2.0, 1.7, 1.4, 1.9, 1.5],
    'ENFP': [8.2, 8.1, 6.5, 9.0, 7.5, 7.0, 8.0, 8.5, 7.2, 7.8],
    'ISTJ': [11.0, 11.6, 15.0, 10.5, 12.0, 13.0, 11.5, 10.8, 12.5, 11.2],
    'ENTP': [3.5, 4.5, 3.2, 4.0, 4.2, 3.8, 4.3, 4.1, 4.0, 4.4],
    'INTJ': [2.5, 2.1, 1.9, 2.2, 2.4, 2.6, 2.3, 2.0, 2.7, 2.2],
    # ... 다른 MBTI 유형들도 이와 유사하게 데이터프레임화 됩니다.
}
df = pd.DataFrame(data)

# 나머지 MBTI 유형들에 대해 랜덤 데이터 생성 (데모용)
all_mbtis = ['ENFP', 'INFJ', 'INTJ', 'ENTP', 'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 
             'ISTP', 'ISFP', 'ESTP', 'ESFP', 'ENFJ', 'ENTJ', 'INFP', 'INTP']

for mbti in all_mbtis:
    if mbti not in df.columns:
        import numpy as np
        df[mbti] = np.random.uniform(1.0, 12.0, size=len(df))

# 3. UI 구성
st.title("🌏 국가별 MBTI 분포 탐색기")
st.markdown("특정 MBTI가 어느 국가에 가장 많이 분포해 있는지 확인해보세요.")

selected_mbti = st.selectbox("궁금한 MBTI를 선택하세요", sorted(all_mbtis))

# 4. 데이터 가공
# 선택한 MBTI 기준으로 내림차순 정렬
filtered_df = df[['Country', selected_mbti]].sort_values(by=selected_mbti, ascending=False).reset_index(drop=True)

# 5. 색상 설정 (1위는 분홍색, 나머지는 파스텔 블루 그라데이션 느낌)
# Plotly의 color_discrete_sequence를 커스텀합니다.
colors = ['#FFB6C1'] + ['#AEC6CF', '#95B9C7', '#7DA6B5', '#6593A3', '#4D8091'] * 2
filtered_df['color_rank'] = range(len(filtered_df))

# 6. 플로틀리 그래프 그리기
fig = px.bar(
    filtered_df,
    x='Country',
    y=selected_mbti,
    text=selected_mbti,
    title=f"국가별 {selected_mbti} 분포 순위 (단위: %)",
    labels={selected_mbti: '비율 (%)', 'Country': '국가'},
    color='color_rank',
    color_continuous_scale=[[0, '#FFB6C1'], [0.1, '#AEC6CF'], [1, '#4D8091']]
)

# 그래프 디테일 수정
fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig.update_layout(
    showlegend=False,
    coloraxis_showscale=False,
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis_tickangle=-45,
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# 7. 추가 정보
st.info(f"현재 데이터에 따르면 **{filtered_df.iloc[0]['Country']}**에 **{selected_mbti}** 유형이 가장 많이 거주하고 있습니다.")
