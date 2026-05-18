ㅊimport streamlit as st
import folium
from streamlit_folium import st_folium

# 스트림릿 페이지 설정
st.set_page_config(page_title="서울 주요 관광지 Top 10", layout="wide")

st.title("외국인이 사랑하는 서울 주요 관광지 Top 10 🗺️")
st.markdown("지도의 마커를 클릭하면 **가장 가까운 지하철역**과 **한 줄 요약 정보**를 볼 수 있습니다.")

# 서울 10대 관광지 데이터 (좌표, 지하철역, 한 줄 요약 포함)
tourist_spots = [
    {
        "name": "경복궁 (Gyeongbokgung Palace)",
        "lat": 37.5796, "lon": 126.9770,
        "subway": "3호선 경복궁역 (5번 출구)",
        "desc": "조선 왕조의 정궁에서 수문장 교대식을 관람하고 한복 체험을 즐겨보세요."
    },
    {
        "name": "명동 쇼핑거리 (Myeongdong Street)",
        "lat": 37.5620, "lon": 126.9850,
        "subway": "4호선 명동역 (6번 출구)",
        "desc": "K-뷰티의 메카에서 로드숍 쇼핑과 다채로운 길거리 음식을 탐방해 보세요."
    },
    {
        "name": "N서울타워 (N Seoul Tower)",
        "lat": 37.5512, "lon": 126.9882,
        "subway": "4호선 명동역/충무로역에서 순환버스 이용",
        "desc": "남산 케이블카를 타고 올라가 서울 시내 전경을 감상하고 사랑의 자물쇠를 걸어보세요."
    },
    {
        "name": "북촌한옥마을 (Bukchon Hanok Village)",
        "lat": 37.5826, "lon": 126.9833,
        "subway": "3호선 안국역 (2번 출구)",
        "desc": "전통 한옥 주거지 사이를 거닐며 고즈넉한 골목길 감성과 전통 찻집을 체험하세요."
    },
    {
        "name": "홍대 거리 (Hongdae Street)",
        "lat": 37.5565, "lon": 126.9235,
        "subway": "2호선/공항철도 홍대입구역 (9번 출구)",
        "desc": "거리 버스킹을 관람하고 트렌디한 인스타 감성 카페와 밤문화(클럽)를 즐겨보세요."
    },
    {
        "name": "동대문 디자인 플라자 (DDP)",
        "lat": 37.5665, "lon": 127.0092,
        "subway": "2/4/5호선 동대문역사문화공원역 (1번 출구)",
        "desc": "우주선 모양의 독특한 야경을 배경으로 사진을 찍고 주변 패션 타운에서 심야 쇼핑을 해보세요."
    },
    {
        "name": "인사동 문화거리 (Insadong)",
        "lat": 37.5744, "lon": 126.9873,
        "subway": "3호선 안국역 (6번 출구)",
        "desc": "쌈지길에서 한국 전통 공예품을 구경하고 골목길 숨은 갤러리들을 관람하세요."
    },
    {
        "name": "롯데월드 타워 & 몰 (Lotte World Tower)",
        "lat": 37.5126, "lon": 127.1025,
        "subway": "2/8호선 잠실역 (1, 2번 출구)",
        "desc": "서울스카이 전망대에서 아찔한 스카이워크를 걷고 석촌호수 산책로를 걸어보세요."
    },
    {
        "name": "강남역 & 가로수길 (Gangnam & Garosu-gil)",
        "lat": 37.4980, "lon": 127.0276,
        "subway": "2호선/신분당선 강남역",
        "desc": "싸이 말춤 동상에서 기념사진을 남기고 지하쇼핑몰과 트렌디한 패션 플래그십 스토어를 구경하세요."
    },
    {
        "name": "여의도 한강공원 (Yeouido Hangang Park)",
        "lat": 37.5284, "lon": 126.9331,
        "subway": "5호선 여의나루역 (2, 3번 출구)",
        "desc": "배달 돗자리 피크닉을 즐기며 '한강 라면'을 먹고 한강 유람선을 타보세요."
    }
]

# 레이아웃 나누기 (왼쪽: 지도, 오른쪽: 클릭 정보 상세 표시)
col1, col2 = st.columns([2, 1])

with col1:
    # 서울 중심부 기준으로 folium 지도 초기화
    m = folium.Map(location=[37.555, 126.980], zoom_start=12)

    # 마커 추가
    for spot in tourist_spots:
        # 지도 위 팝업창 디자인 구성
        popup_html = f"""
        <div style="width:220px; font-family: 'Malgun Gothic', sans-serif;">
            <h4 style="margin:0 0 5px 0; color:#1f77b4;">{spot['name']}</h4>
            <p style="margin:0 0 3px 0; font-size:12px;"><b>🚉 역:</b> {spot['subway']}</p>
            <p style="margin:0; font-size:12px; color:#555;"><b>🎡 요약:</b> {spot['desc']}</p>
        </div>
        """
        folium.Marker(
            location=[spot["lat"], spot["lon"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=spot["name"]
        ).add_to(m)

    # 스트림릿에 지도 렌더링하고, 클릭 이벤트를 받아옴
    map_data = st_folium(m, width=800, height=550)

with col2:
    st.subheader("📌 선택한 관광지 정보")
    
    # 사용자가 지도의 마커를 클릭했는지 확인
    if map_data and map_data.get("last_object_clicked"):
        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]
        
        # 클릭한 좌표와 일치하는 관광지 탐색 (소수점 오차 감안)
        selected_spot = None
        for spot in tourist_spots:
            if abs(spot["lat"] - clicked_lat) < 0.001 and abs(spot["lon"] - clicked_lon) < 0.001:
                selected_spot = spot
                break
        
        if selected_spot:
            st.info(f"### {selected_spot['name']}")
            st.success(f"**🚉 가장 가까운 역**\n\n{selected_spot['subway']}")
            st.warning(f"**🎡 한 줄 요약 (놀거리)**\n\n{selected_spot['desc']}")
        else:
            st.write("마커를 정확히 클릭해 주세요.")
    else:
        st.write("지도의 파란색 마커를 클릭하시면 상세 요약 정보가 여기에 표시됩니다.")
