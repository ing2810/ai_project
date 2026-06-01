import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(
    page_title="반려동물 이름 트렌드 분석기",
    page_icon="🐾",
    layout="wide"
)

# ----------------------------------------------------
# 타이틀: 검은색 글씨 + 파스텔 핑크/블루 네온 글로우 효과
# ----------------------------------------------------
st.markdown(
    """
    <style>
    .neon-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #000000; /* 글씨색 검은색 */
        text-align: left;
        padding: 15px 0;
        display: inline-block;
        position: relative;
        letter-spacing: -1px;
        
        /* 파스텔 핑크(#FFB7B2)와 파스텔 블루(#B3C5FF) 네온 효과 */
        text-shadow: 
            0 0 4px #ffffff,   
            0 0 12px #FFB7B2,  
            0 0 22px #B3C5FF,  
            0 0 32px #FFB7B2;  
    }
    .unique-name-box {
        background-color: #f8f9fa;
        border-left: 5px solid #FFB7B2;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 4px;
        font-size: 1.05rem;
    }
    </style>
    
    <h1 class="neon-title">🐾 반려동물 이름 트렌드 분석 대시보드</h1>
    """,
    unsafe_allow_html=True
)

st.markdown("업로드된 반려동물 이름 데이터를 기반으로 인기 순위와 테마별 통계를 보여줍니다.")

# 2. 데이터 로드 함수 (인코딩 에러 예외처리 완료)
@st.cache_data
def load_data():
    file_path = "pet_name.csv"
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except Exception:
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except Exception:
            df = pd.read_csv(file_path, encoding='utf-8')
            
    df['동물이름'] = df['동물이름'].astype(str).str.strip()
    df = df.sort_values(by='횟수', ascending=False).reset_index(drop=True)
    df['순위'] = df['횟수'].rank(method='min', ascending=False).astype(int)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("📂 'pet_name.csv' 파일을 찾을 수 없습니다. 대시보드 파이썬 파일과 같거나 올바른 경로에 파일을 위치시켜주세요.")
    st.stop()

# 사용자 요청 컬러맵 (많은 쪽이 파스텔 핑크, 적은 쪽이 파스텔 블루)
pastel_pink_to_blue = ["#B3C5FF", "#FFB7B2"]

# 레이아웃 분할 (왼쪽: 그래프, 오른쪽: 검색창)
col1, col2 = st.columns([2, 1])

with col1:
    # 요구사항 2: 가장 많이 쓰이는 반려동물 이름 Top 20 막대그래프
    st.subheader("🏆 전체 반려동물 이름 Top 20")
    top_20 = df.head(20)
    
    fig_top20 = px.bar(
        top_20,
        x='동물이름',
        y='횟수',
        text='횟수',
        color='횟수',
        color_continuous_scale=pastel_pink_to_blue,
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
    # 요구사항 4: 이름 검색 기능
    st.subheader("🔍 우리 아이 이름 순위 검색")
    search_name = st.text_input("반려동물의 이름을 입력하세요 (예: 코코, 만두, 루피)", "").strip()
    
    if search_name:
        result = df[df['동물이름'] == search_name]
        
        if not result.empty:
            rank = result.iloc[0]['순위']
            count = result.iloc[0]['횟수']
            total_unique = len(df)
            
            st.success(f"🎉 **'{search_name}'**(은)는 데이터에 등록되어 있는 이름입니다!")
            
            m1, m2 = st.columns(2)
            m1.metric(label="현재 순위", value=f"{rank} 위")
            m2.metric(label="등록 빈도수", value=f"{count} 회")
            
            st.info(f"💡 데이터에 등록된 전체 **{total_unique:,}개**의 고유 이름 중 **{rank}위**에 랭크되어 있습니다.")
        else:
            st.error(f"ℹ️ **'{search_name}'**(은)는 현재 파일에 등록되지 않은 아주 개성 넘치는 이름입니다!")

st.markdown("---")

# ----------------------------------------------------
# 테마별 이름 분석 (옵션 제목 수정 버전)
# ----------------------------------------------------
st.subheader("🎭 테마별 이름 분석")

themes = {
    "🍽️ 음식 & 디저트": ["보리", "초코", "두부", "만두", "감자", "율무", "시루", "누룽지", "쿠키", "망고", "라떼", "크림", "땅콩", "모찌", "후추", "치즈", "타코", "버터", "젤리", "호떡", "짜장", "카레", "모카", "호두", "사탕", "앵두", "자두", "호박"],
    "🌱 자연, 날씨 & 계절": ["별이", "구름", "하늘", "달이", "태양", "우주", "봄", "하루", "가을", "여름", "겨울", "바다", "나무", "이슬", "단풍", "새벽", "노을", "구름이", "별"],
    "✨ 소망, 감정 & 행운(복)": ["사랑이", "해피", "행복", "미소", "기쁨", "럭키", "행운", "희망", "소망", "대박", "장군", "복돌이", "복순이", "오복", "장수", "사랑", "축복"],
    "👑 영문 성명 & BRAND 캐릭터": ["루이", "레오", "마리", "루비", "베리", "로이", "제니", "구찌", "샤넬", "디올", "미키", "루피", "토르", "코코", "토토", "미미", "나나", "밍키", "조이", "맥스"],
    "🧑 사람 이름 & 순우리말": ["두리", "철수", "순이", "영심이", "순자", "마루", "누리", "아리", "다온", "라온", "도담", "까치", "신비", "하나", "나비"],
    "🦄 특이하고 개성 있는 이름": "UNIQUE_MODE"  # [수정] 옵션 텍스트에서 (하위권) 제거
}

selected_theme = st.selectbox("원하는 이름 테마를 선택해보세요:", list(themes.keys()))

if selected_theme == "🦄 특이하고 개성 있는 이름":
    st.write("📋 **데이터 내 등록 횟수가 단 1회뿐인 개성 넘치는 이름 20개 조합입니다.**")
    
    # 횟수가 1회인 데이터만 필터링한 후, 뒤쪽에 위치한 이름 20개 가져오기
    rare_df = df[df['횟수'] == 1].tail(20)
    
    if not rare_df.empty:
        # 화면을 2열로 분할하여 10개씩 정렬
        l_col, r_col = st.columns(2)
        rare_list = rare_df['동물이름'].tolist()
        
        for idx, name in enumerate(rare_list):
            box_html = f"<div class='unique-name-box'>✨ <b>{name}</b> (등록 횟수: 1회)</div>"
            if idx < 10:
                l_col.markdown(box_html, unsafe_allow_html=True)
            else:
                r_col.markdown(box_html, unsafe_allow_html=True)
    else:
        st.info("이름 데이터를 불러올 수 없습니다.")

elif selected_theme:
    keyword_list = themes[selected_theme]
    theme_df = df[df['동물이름'].isin(keyword_list) | df['동물이름'].apply(lambda x: any(kw in x for kw in keyword_list if len(kw) > 1))]
    theme_top10 = theme_df.drop_duplicates(subset=['동물이름']).head(10)
    
    if not theme_top10.empty:
        fig_theme = px.bar(
            theme_top10,
            x='동물이름',
            y='횟수',
            text='횟수',
            color='횟수',
            color_continuous_scale=pastel_pink_to_blue,
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
