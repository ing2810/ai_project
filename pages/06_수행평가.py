import streamlit as tf
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(
    page_title="반려동물 이름 트렌드 분석기",
    page_icon="🐾",
    layout="wide"
)

st.title("🐾 반려동물 이름 트렌드 분석 대시보드")
st.markdown("업로드된 반려동물 이름 데이터를 기반으로 인기 순위와 테마별 통계를 보여줍니다.")

# 2. 데이터 로드 함수
@st.cache_data
def load_data():
    # 동일 경로에 pet_name.csv 파일이 있다고 가정합니다.
    df = pd.read_csv("pet_name.csv")
    # 공백 제거 및 데이터 정제
    df['동물이름'] = df['동물이름'].astype(str).str.strip()
    # 공동 순위 처리를 고려해 '횟수' 기준 내림차순 정렬 후 순위 재부여
    df = df.sort_values(by='횟수', ascending=False).reset_index(drop=True)
    df['순위'] = df['횟수'].rank(method='min', ascending=False).astype(int)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("📂 'pet_name.csv' 파일을 찾을 수 없습니다. 대시보드와 같은 폴더에 파일을 위치시켜주세요.")
    st.stop()

# 사용자 요청에 맞는 그라데이션 컬러맵 정의 (파스텔 핑크 -> 파스텔 블루)
# 많은 쪽(위쪽)이 핑크, 적은 쪽(아래쪽)이 블루로 그라데이션 설정
pastel_pink_to_blue = ["#B3C5FF", "#FFC6FF", "#FFB7B2"] # 순서대로 블루 -> 중간 -> 핑크 (Plotly는 값 크기에 따라 매핑)

# 레이아웃 분할
col1, col2 = st.columns([2, 1])

with col1:
    # ----------------------------------------------------
    # 요구사항 2: 가장 많이 쓰이는 반려동물 이름 Top 20 막대그래프
    # ----------------------------------------------------
    st.subheader("🏆 전체 반려동물 이름 Top 20")
    top_20 = df.head(20)
    
    fig_top20 = px.bar(
        top_20,
        x='동물이름',
        y='횟수',
        text='횟수',
        color='횟수',  # 횟수에 따라 색상 그라데이션 적용
        color_continuous_scale=["#B3C5FF", "#FFB7B2"], # 파스텔 블루에서 파스텔 핑크로
        labels={'동물이름': '반려동물 이름', '횟수': '등록 횟수'},
    )
    
    fig_top20.update_traces(texttemplate='%{text}회', textposition='outside')
    fig_top20.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45,
        coloraxis_showscale=False,
        height=450,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_top20, use_container_width=True)

with col2:
    # ----------------------------------------------------
    # 요구사항 4: 이름 검색 기능 (몇위권인지, 없는 이름인지 판별)
    # ----------------------------------------------------
    st.subheader("🔍 우리 아이 이름 순위 검색")
    search_name = st.text_input("반려동물의 이름을 입력하세요 (예: 코코, 만두, 루피)", "").strip()
    
    if search_name:
        result = df[df['동물이름'] == search_name]
        
        if not result.empty:
            rank = result.iloc[0]['순위']
            count = result.iloc[0]['횟수']
            total_unique = len(df)
            
            st.success(f"🎉 **'{search_name}'**(은)는 데이터에 등록되어 있는 이름입니다!")
            
            # 메트릭으로 시각적 효과 부여
            m1, m2 = st.columns(2)
            m1.metric(label="현재 순위", value=f"{rank} 위")
            m2.metric(label="등록 빈도수", value=f"{count} 회")
            
            # 상위 백분율 계산
            percentile = (rank / total_unique) * 100
            st.info(f"💡 전체 {total_unique:,}개의 고유 이름 중 상위 **{percentile:.2f}%**에 해당합니다.")
        else:
            st.error(f"ℹ️ **'{search_name}'**(은)는 현재 파일에 등록되지 않은 아주 개성 넘치는 이름입니다!")

st.markdown("---")

# ----------------------------------------------------
# 요구사항 3: 반려동물 이름 테마별 분석 (Top 10 막대그래프)
# ----------------------------------------------------
st.subheader("🎭 테마별 인기 이름 Top 10 기획")

# 테마 사전 정의 (이전 분석 기반 키워드 매핑)
themes = {
    "🍽️ 음식 & 디저트": ["보리", "초코", "두부", "만두", "감자", "율무", "시루", "누룽지", "쿠키", "망고", "라떼", "크림", "땅콩", "모찌", "후추", "치즈", "타코", "버터", "젤리", "호떡", "짜장", "카레", "모카", "초코", "호두", "탕후루", "초코", "사탕", "앵두", "자두", "호박"],
    "🌱 자연, 날씨 & 계절": ["별이", "구름", "하늘", "달이", "태양", "우주", "봄", "하루", "가을", "여름", "겨울", "바다", "나무", "이슬", "단풍", "태양", "새벽", "노을", "구름이", "별"],
    "✨ 소망, 감정 & 행운(복)": ["사랑이", "해피", "행복", "미소", "기쁨", "럭키", "행운", "희망", "소망", "대박", "장군", "복돌이", "복순이", "오복", "장수", "사랑", "축복"],
    "🐶 외모, 성격 & 신체특징": ["콩이", "토리", "뭉치", "꼬미", "뚱이", "미니", "단추", "까미", "흰둥이", "아롱이", "초롱이", "깜이", "하양이", "탄", "또또", "뽀뽀", "재롱이", "까꿍", "돌돌이", "몽이", "똘이", "둥이", "송이", "짱아"],
    "👑 영문 성명 & 브랜드 캐릭터": ["루이", "레오", "마리", "루비", "베리", "로이", "제니", "구찌", "샤넬", "디올", "미키", "루피", "토르", "코코", "토토", "미미", "나나", "밍키", "조이", "맥스", "샘", "벤", "럭키"],
    "🧑 정감 가득 사람 이름 & 순우리말": ["두리", "철수", "순이", "영심이", "순자", "마루", "누리", "아리", "다온", "라온", "도담", "까치", "신비", "하나", "토리", "나비"]
}

selected_theme = st.selectbox("원하는 이름 테마를 선택해보세요:", list(themes.keys()))

if selected_theme:
    # 선택된 테마의 키워드가 포함되거나 일치하는 데이터 필터링
    keyword_list = themes[selected_theme]
    
    # 이름에 테마 키워드가 정확히 일치하거나 포함된 데이터 추출
    theme_df = df[df['동물이름'].isin(keyword_list) | df['동물이름'].apply(lambda x: any(kw in x for kw in keyword_list if len(kw) > 1))]
    # 중복 제거 및 상위 10개 추출
    theme_top10 = theme_df.drop_duplicates(subset=['동물이름']).head(10)
    
    if not theme_top10.empty:
        fig_theme = px.bar(
            theme_top10,
            x='동물이름',
            y='횟수',
            text='횟수',
            color='횟수',
            color_continuous_scale=["#B3C5FF", "#FFB7B2"], # 파스텔 블루 -> 파스텔 핑크 그라데이션
            labels={'동물이름': '테마 내 이름', '횟수': '등록 횟수'},
        )
        fig_theme.update_traces(texttemplate='%{text}회', textposition='outside')
        fig_theme.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale=False,
            height=400,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_theme, use_container_width=True)
    else:
        st.info("이 테마에 해당하는 이름이 상위 데이터에 충분하지 않습니다.")
