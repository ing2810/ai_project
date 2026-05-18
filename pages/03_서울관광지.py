import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. 페이지 기본 설정
st.set_page_config(page_title="Seoul Pink Guide", layout="wide")

# 2. 흰색 바탕 + 검은색 글씨 + 분홍색 네온 글로우 디자인 적용 (CSS)
st.markdown("""
    <style>
    /* 전체 배경을 흰색으로 설정 */
    .stApp {
        background-color: #ffffff;
    }
    
    /* 검은색 글씨 + 분홍색 네온 광채 효과 (밝은 배경용) */
    .pink-glow-title {
        color: #111111;
        font-size: 50px;
        font-weight: bold;
        text-align: center;
        text-shadow: 0 0 10px rgba(255, 20, 147, 0.5), 0 0 20px rgba(255, 105, 180, 0.3);
        padding: 20px;
        font-family: 'Courier New', Courier, monospace;
    }
    
    .pink-glow-text {
        color: #222222;
        text-shadow: 0 0 8px rgba(255, 20, 147, 0.4);
        font-size: 20px;
        font-weight: bold;
    }
    
    /* 정보 창 스타일링 (밝은 배경에 어울리는 부드러운 핑크) */
    .info-box {
        border: 2px solid #ff1493;
        border-radius: 15px;
        padding: 20px;
        background-color: rgba(255, 20, 147, 0.05);
        box-shadow: 0 0 15px rgba(255, 20, 147, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 제목 표시
st.markdown('<div class="pink-glow-title">SEOUL PINK VIBE TOP 10</div>', unsafe_allow_html=True)

# 4. 데이터 (외국인 인기 10대 관광지)
tourist_spots = [
    {"name": "경복궁", "lat": 37.5796, "lon": 126.9770, "info": "🚇3호선 경복궁역 | 🎡한복 입고 광화문 수문장 교대식 관람하기"},
    {"name": "N서울타워", "lat": 37.5512, "lon": 126.9882, "info": "🚇4호선 명동역 | 🎡남산 케이블카 타고 서울 야경 보며 사랑의 자물쇠 걸기"},
    {"name": "명동거리", "lat": 37.5633, "lon": 126.9850, "info": "🚇4호선 명동역 | 🎡K-뷰티 화장품 쇼핑하고 길거리 음식 털기"},
    {"name": "북촌한옥마을", "lat": 37.5826, "lon": 126.9833, "info": "🚇3호선 안국역 | 🎡고즈넉한 한옥 골목에서 인생샷 찍고 전통차 마시기"},
    {"name": "홍대 거리", "lat": 37.5565, "lon": 126.9235, "info": "🚇2호선 홍대입구역 | 🎡거리 버스킹 구경하고 힙한 클럽과 소품샵 탐방하기"},
    {"name": "동대문 DDP", "lat": 37.5665, "lon": 127.0092, "info": "🚇2/4/5호선 동대문역사문화공원역 | 🎡우주선 닮은 건물 야경 보고 패션 전시 관람하기"},
    {"name": "잠실 롯데월드타워", "lat": 37.5126, "lon": 127.1025, "info": "🚇2/8호선 잠실역 | 🎡서울스카이 전망대에서 아찔한 유리바닥 걷기"},
    {"name": "인사동 쌈지길", "lat": 37.5744, "lon": 126.9873, "info": "🚇3호선 안국역 | 🎡전통 공예품 구경하고 꿀타래 먹어보기"},
    {"name": "익선동 한옥거리", "lat": 37.5743, "lon": 126.9897, "info": "🚇1/3/5호선 종로3가역 | 🎡개조된 한옥 카페에서 수플레 팬케이크 먹기"},
    {"name": "스타필드 별마당도서관", "lat": 37.5121, "lon": 127.0589, "info": "🚇2호선 삼성역 | 🎡거대한 책장 앞에서 사진 찍고 코엑스몰 쇼핑하기"}
]

# 5. 레이아웃 (지도와 정보창)
col1, col2 = st.columns([2, 1])

with col1:
    # 밝은 배경에 잘 어울리는 기본 지도(OpenStreetMap) 사용
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)
    
    for spot in tourist_spots:
        # 분홍색 원형 마커
        folium.CircleMarker(
            location=[spot["lat"], spot["lon"]],
            radius=10,
            popup=spot["name"],
            color="#ff1493",
            fill=True,
            fill_color="#ff1493",
            fill_opacity=0.7,
            tooltip=spot["name"]
        ).add_to(m)

    # 지도 출력 및 클릭 데이터 수집
    map_data = st_folium(m, width="100%", height=500)

with col2:
    st.markdown('<p class="pink-glow-text">📍 장소를 클릭하세요</p>', unsafe_allow_html=True)
    
    if map_data and map_data.get("last_object_clicked"):
        lat = map_data["last_object_clicked"]["lat"]
        lon = map_data["last_object_clicked"]["lng"]
        
        # 클릭한 좌표와 일치하는 데이터 찾기
        for spot in tourist_spots:
            if round(spot["lat"], 4) == round(lat, 4):
                st.markdown(f"""
                <div class="info-box">
                    <h2 style="color:#111111; margin-top:0;">{spot['name']}</h2>
                    <p style="color:#333333; font-size:18px; line-height:1.5;">{spot['info']}</p>
                </div>
                """, unsafe_allow_html=True)
                break
    else:
        st.write("지도의 분홍색 마커를 클릭하면 요약 정보가 나타납니다!")

st.markdown('<div style="text-align:center; color:gray; margin-top:50px;">Enjoy your Seoul Trip with Pink Vibe!</div>', unsafe_allow_html=True)
