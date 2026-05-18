import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. 페이지 기본 설정
st.set_page_config(page_title="Seoul Discovery Guide", layout="wide")

# 2. 디자인 고도화 (구글 폰트 Poppins + 밝은 핫핑크 네온)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;800&display=swap');

    .stApp {
        background-color: #ffffff;
    }
    
    /* 영어 타이틀 + Poppins 폰트 + 강력한 핫핑크 네온 광채 */
    .pink-glow-title {
        color: #111111;
        font-size: 52px;
        font-weight: 800;
        text-align: center;
        text-shadow: 0 0 15px rgba(255, 105, 180, 0.8), 0 0 30px rgba(255, 20, 147, 0.4);
        padding: 30px;
        font-family: 'Poppins', sans-serif;
        letter-spacing: -1px;
    }
    
    .pink-glow-text {
        color: #222222;
        text-shadow: 0 0 10px rgba(255, 105, 180, 0.5);
        font-size: 22px;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
    }
    
    /* 정보 창 스타일 (더 밝고 선명한 테두리) */
    .info-box {
        border: 3px solid #FF69B4;
        border-radius: 20px;
        padding: 25px;
        background-color: rgba(255, 105, 180, 0.08);
        box-shadow: 0 10px 25px rgba(255, 105, 180, 0.2);
        font-family: 'Poppins', sans-serif;
    }
    
    .info-title {
        color: #111111;
        font-weight: 800;
        margin-bottom: 15px;
        border-bottom: 2px solid #FF69B4;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 영문 타이틀 표시
st.markdown('<div class="pink-glow-title">Top 10 Seoul Attractions Foreigners Love</div>', unsafe_allow_html=True)

# 4. 데이터 (지하철 및 놀거리 정보)
tourist_spots = [
    {"name": "Gyeongbokgung Palace", "lat": 37.5796, "lon": 126.9770, "info": "🚇Line 3 Gyeongbokgung Stn | 🎡Watch the Changing of the Guard & wear a Hanbok"},
    {"name": "N Seoul Tower", "lat": 37.5512, "lon": 126.9882, "info": "🚇Line 4 Myeongdong Stn | 🎡Take the cable car for panoramic views & Love Locks"},
    {"name": "Myeongdong Street", "lat": 37.5633, "lon": 126.9850, "info": "🚇Line 4 Myeongdong Stn | 🎡Explore K-Beauty shops & try iconic street food"},
    {"name": "Bukchon Hanok Village", "lat": 37.5826, "lon": 126.9833, "info": "🚇Line 3 Anguk Stn | 🎡Walk through historic alleys & visit traditional tea houses"},
    {"name": "Hongdae Street", "lat": 37.5565, "lon": 126.9235, "info": "🚇Line 2 Hongik Univ Stn | 🎡Enjoy live busking, indie music, and vibrant nightlife"},
    {"name": "Dongdaemun DDP", "lat": 37.5665, "lon": 127.0092, "info": "🚇Line 2/4/5 DDP Stn | 🎡Marvel at futuristic architecture and fashion exhibits"},
    {"name": "Lotte World Tower", "lat": 37.5126, "lon": 127.1025, "info": "🚇Line 2/8 Jamsil Stn | 🎡Visit Seoul Sky Observatory on the 123rd floor"},
    {"name": "Insadong Ssamziegil", "lat": 37.5744, "lon": 126.9873, "info": "🚇Line 3 Anguk Stn | 🎡Shop for traditional crafts & taste Kkultarae candy"},
    {"name": "Ikseon-dong Alleys", "lat": 37.5743, "lon": 126.9897, "info": "🚇Line 1/3/5 Jongno 3-ga | 🎡Cafe hopping in beautifully renovated Hanoks"},
    {"name": "Starfield Library", "lat": 37.5121, "lon": 127.0589, "info": "🚇Line 2 Samseong Stn | 🎡Take photos at the giant 13m high bookshelves"}
]

# 5. 레이아웃
col1, col2 = st.columns([2, 1])

with col1:
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)
    for spot in tourist_spots:
        folium.CircleMarker(
            location=[spot["lat"], spot["lon"]],
            radius=12, popup=spot["name"], color="#FF69B4",
            fill=True, fill_color="#FF69B4", fill_opacity=0.8, tooltip=spot["name"]
        ).add_to(m)
    map_data = st_folium(m, width="100%", height=550, key="seoul_guide_final")

with col2:
    st.markdown('<p class="pink-glow-text">📍 Click a Pink Marker</p>', unsafe_allow_html=True)
    if map_data and map_data.get("last_object_clicked"):
        lat, lon = map_data["last_object_clicked"]["lat"], map_data["last_object_clicked"]["lng"]
        selected_spot = next((s for s in tourist_spots if abs(s["lat"] - lat) < 0.005 and abs(s["lon"] - lon) < 0.005), None)
        if selected_spot:
            st.markdown(f"""
            <div class="info-box">
                <h2 class="info-title">{selected_spot['name']}</h2>
                <p style="color:#333333; font-size:19px; line-height:1.6; font-weight:500;">{selected_spot['info']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Click a vibrant pink marker on the map to see transit and activity details!")

st.markdown('<div style="text-align:center; color:#bbbbbb; margin-top:60px; font-family:Poppins;">Explore the vibrant soul of Seoul.</div>', unsafe_allow_html=True)
