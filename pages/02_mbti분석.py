import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 페이지 설정
st.set_page_config(page_title="World MBTI Neon Dashboard", layout="wide")

# 스타일링 (배경색 및 폰트)
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    h1 { color: #FF10F0; text-shadow: 0 0 10px #FF10F0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧪 Global MBTI Neon Explorer")

# 데이터 로드 함수
@st.cache_data
def load_data():
    file_path = 'countriesMBTI_16types.csv'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # 컬럼명 앞뒤 공백 제거 (데이터 클렌징)
        df.columns = df.columns.str.strip()
        return df
    else:
        return None

df = load_data()

if df is not None:
    # 1. 국가 리스트 추출 (선택 상자가 비어있지 않도록 보장)
    country_list = sorted(df['Country'].unique().tolist())
    
    # 2. 사이드바 국가 선택
    selected_country = st.sidebar.selectbox(
        "분석할 국가를 선택하세요", 
        country_list,
        index=country_list.index('South Korea') if 'South Korea' in country_list else 0
    )

    # 3. 데이터 가공
    row = df[df['Country'] == selected_country].drop(columns=['Country'])
    plot_df = row.T.reset_index()
    plot_df.columns = ['MBTI', 'Value']
    plot_df = plot_df.sort_values(by='Value', ascending=False)

    # 4. 네온 컬러 그라데이션 생성
    # 1등: 네온 핑크 (#FF10F0)
    # 나머지: 네온 그린 (#39FF14) -> 어두운 그린 그라데이션
    colors = []
    n = len(plot_df)
    for i in range(n):
        if i == 0:
            colors.append('#FF10F0') # 1등 핑크
        else:
            # i가 커질수록 점점 어두워지는 그린 (RGB 조정)
            intensity = max(50, 255 - (i * 12)) 
            colors.append(f'rgb(57, {intensity}, 20)')

    # 5. 플로틀리 인터랙티브 차트
    fig = go.Figure(go.Bar(
        x=plot_df['MBTI'],
        y=plot_df['Value'],
        marker=dict(
            color=colors,
            line=dict(color='#FFFFFF', width=0.5)
        ),
        text=plot_df['Value'].apply(lambda x: f'{x*100:.1f}%'),
        textposition='outside',
        hovertemplate='<b>%{x}</b>: %{y:.2%}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=f"✨ {selected_country} MBTI Distribution",
            font=dict(size=24, color='#39FF14')
        ),
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(tickangle=0, font=dict(color='#39FF14')),
        yaxis=dict(showgrid=False, showticklabels=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(fig, use_container_width=True)

    # 6. 하단 요약 카드
    col1, col2, col3 = st.columns(3)
    top_type = plot_df.iloc[0]
    col1.metric("Most Common", top_type['MBTI'], f"{top_type['Value']*100:.1f}%")
    col2.info(f"선택된 국가: **{selected_country}**")
    col3.success(f"데이터 샘플 수: {len(df)}개 국가")

else:
    st.error("❌ 'countriesMBTI_16types.csv' 파일을 찾을 수 없습니다. 깃허브 저장소에 파일이 있는지 확인해주세요!")
