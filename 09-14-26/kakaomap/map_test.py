import os
import math
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

load_dotenv()
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

st.set_page_config(page_title="🚂 어디갈래? - 기차 여행 & 코스 플래너", layout="wide", page_icon="🚂")

# 세션 상태 관리 (여행 코스 & 이전 기준역 추적)
if "my_trip" not in st.session_state:
    st.session_state.my_trip = []
if "last_station" not in st.session_state:
    st.session_state.last_station = None

# 스타일 커스텀
st.markdown("""
<style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚂 어디갈래? | 기차역 & 세부 동네 여행 코스 만들기")
st.caption("도착역과 가고 싶은 세부 동네를 설정하고, 장소 간 이동시간을 한눈에 계산해 보세요.")

if not KAKAO_API_KEY:
    st.error(".env 파일에 KAKAO_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요.")
    st.stop()

# ----------------------------------------------------
# 1. 거리 및 이동 시간 계산 함수 (하버사인 공식)
# ----------------------------------------------------
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # 지구 반지름 (m)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def estimate_travel_time(distance_m):
    real_dist = distance_m * 1.3  # 실제 도로 굴곡 계수 반영
    # 도보: 시속 4km (분당 약 66.7m)
    walk_min = max(1, round(real_dist / (4000 / 60)))
    # 차량/택시: 시내 평균 시속 25km (분당 약 416.7m) + 신호대기 2분
    car_min = max(1, round((real_dist / (25000 / 60)) + 2))
    return walk_min, car_min, round(real_dist)

# ----------------------------------------------------
# 2. 카카오 API 함수
# ----------------------------------------------------
def search_keyword(query, api_key):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": query, "size": 1}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            docs = res.json().get("documents", [])
            return docs[0] if docs else None
    except Exception:
        pass
    return None

def search_category(category_code, lat, lng, radius, api_key):
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {
        "category_group_code": category_code,
        "x": str(lng),
        "y": str(lat),
        "radius": int(radius),
        "sort": "distance",
        "size": 15
    }
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            return res.json().get("documents", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=3600, show_spinner=False)
def get_place_image(place_name, api_key):
    url = "https://dapi.kakao.com/v2/search/image"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": place_name, "size": 1}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=4)
        if res.status_code == 200:
            docs = res.json().get("documents", [])
            if docs:
                return docs[0].get("image_url")
    except Exception:
        pass
    return None

# ----------------------------------------------------
# 3. 날씨 & 환율 API 함수
# ----------------------------------------------------
def get_weather_and_air(lat, lng):
    weather_data = {}
    w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
    try:
        w_res = requests.get(w_url, timeout=3)
        if w_res.status_code == 200:
            curr = w_res.json().get("current", {})
            weather_data["temp"] = curr.get("temperature_2m")
            weather_data["humidity"] = curr.get("relative_humidity_2m")
            weather_data["wind"] = curr.get("wind_speed_10m")
    except Exception:
        pass

    aq_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lng}&current=pm10,pm2_5"
    try:
        aq_res = requests.get(aq_url, timeout=3)
        if aq_res.status_code == 200:
            aq_curr = aq_res.json().get("current", {})
            weather_data["pm10"] = aq_curr.get("pm10")
            weather_data["pm2_5"] = aq_curr.get("pm2_5")
    except Exception:
        pass

    return weather_data

def get_air_quality_status(pm10, pm2_5):
    if pm10 is None or pm2_5 is None:
        return "정보 없음", "⚪"
    if pm10 <= 30 and pm2_5 <= 15:
        return "좋음", "🟢"
    elif pm10 <= 80 and pm2_5 <= 35:
        return "보통", "🟡"
    elif pm10 <= 150 and pm2_5 <= 75:
        return "나쁨", "🟠"
    else:
        return "매우 나쁨", "🔴"

def get_outfit_recommendation(temp):
    if temp is None:
        return {"title": "날씨 수신 대기 중", "desc": "기온 정보를 불러오는 중입니다.", "items": ["편안한 운동화"]}
    if temp >= 28:
        return {"title": "무더운 한여름", "desc": "린넨, 반팔 등 통풍이 잘되는 옷차림 권장", "items": ["반팔 / 린넨", "반바지 / 쿨슬랙스", "모자 / 양산 / 휴대용 선풍기"]}
    elif 23 <= temp < 28:
        return {"title": "초여름 맑은 날", "desc": "열차 및 실내 에어컨 대비 얇은 겉옷 챙기기", "items": ["반팔티 / 얇은 셔츠", "면바지 / 슬랙스", "실내용 가디건"]}
    elif 20 <= temp < 23:
        return {"title": "쾌적한 간절기", "desc": "동네 골목 뚜벅이 여행에 가장 좋은 날씨", "items": ["맨투맨 / 긴팔 티", "가벼운 셔츠 아우터", "청바지 / 워킹화"]}
    elif 17 <= temp < 20:
        return {"title": "선선한 환절기", "desc": "일교차 대비 겉옷 필수", "items": ["니트 / 맨투맨", "자켓 / 블루종", "긴바지"]}
    elif 12 <= temp < 17:
        return {"title": "쌀쌀한 날씨", "desc": "트렌치코트나 두꺼운 외투 추천", "items": ["트렌치코트 / 자켓", "도톰한 니트", "슬랙스"]}
    elif 9 <= temp < 12:
        return {"title": "초겨울 추위", "desc": "코트나 경량 패딩 착용", "items": ["울 코트 / 경량 패딩", "방한 이너", "목도리"]}
    else:
        return {"title": "한파 영하권 날씨", "desc": "롱패딩과 방한용품 무장 필요", "items": ["롱패딩 / 헤비 아우터", "기모 팬츠", "장갑 / 핫팩"]}

def get_rate(base_currency, target_currency):
    if base_currency == target_currency:
        return 1.0
    url = f"https://api.frankfurter.app/latest?from={base_currency}&to={target_currency}"
    try:
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            return res.json().get("rates", {}).get(target_currency, None)
    except requests.exceptions.RequestException:
        return None
    return None

# ----------------------------------------------------
# 사이드바: 1단계 기차역 + 2단계 세부 동네/지역 검색
# ----------------------------------------------------
st.sidebar.header("🚂 기차역 및 여행 지역 선택")

station_presets = ["강릉역", "부산역", "광주송정역", "여수EXPO역", "동대구역", "경주역", "전주역", "대전역", "춘천역", "직접 입력"]
selected_station = st.sidebar.selectbox("1. 도착 기차역 선택", station_presets, index=0)

if selected_station == "직접 입력":
    station_name = st.sidebar.text_input("기차역 이름 입력", value="강릉역")
else:
    station_name = selected_station

# 기차역이 변경되었을 때 이전 코스 리셋 안내 및 자동 초기화 로직
if st.session_state.last_station != station_name:
    if st.session_state.my_trip:
        st.sidebar.warning(f"도착역이 '{st.session_state.last_station}'에서 '{station_name}'(으)로 변경되었습니다.")
        if st.sidebar.button("🔄 코스 비우고 새로 시작하기"):
            st.session_state.my_trip = []
            st.session_state.last_station = station_name
            st.rerun()
    else:
        st.session_state.last_station = station_name

# 2단계: 세부 지역/동네 이름 검색
sub_area = st.sidebar.text_input("2. 세부 동네/명소 입력 (선택사항)", placeholder="예: 안목해변, 초당마을, 광안리")

radius = st.sidebar.slider("탐색 반경 (미터)", min_value=300, max_value=3000, value=1500, step=100)

st.sidebar.markdown("---")
st.sidebar.subheader("🎟️ 기차표 빠른 예매")
st.sidebar.link_button("🚆 코레일톡 (KTX / 일반열차)", "https://www.letskorail.com/", use_container_width=True)
st.sidebar.link_button("🚅 SRT 승차권 예매 (수서발)", "https://etk.srail.kr/", use_container_width=True)

# ----------------------------------------------------
# 중심 좌표 결정 로직
# ----------------------------------------------------
station_place = search_keyword(station_name, KAKAO_API_KEY)
if not station_place:
    st.error(f"'{station_name}' 정보를 찾을 수 없습니다. 올바른 역명을 입력해 주세요.")
    st.stop()

st_lat = float(station_place["y"])
st_lng = float(station_place["x"])
st_official_name = station_place["place_name"]

# 세부 동네 입력이 있으면 [기차역명 + 동네명]으로 검색하여 탐색 중심으로 설정
if sub_area.strip():
    target_query = f"{station_name} {sub_area.strip()}"
    target_place = search_keyword(target_query, KAKAO_API_KEY)
    if not target_place:
        # 역명을 뺀 단독 검색 시도
        target_place = search_keyword(sub_area.strip(), KAKAO_API_KEY)
else:
    target_place = station_place

if target_place:
    center_lat = float(target_place["y"])
    center_lng = float(target_place["x"])
    center_name = target_place["place_name"]
    center_addr = target_place.get("road_address_name") or target_place.get("address_name")
    
    # 상단 안내 배너
    col_banner1, col_banner2 = st.columns([3, 1])
    with col_banner1:
        if sub_area.strip() and center_name != st_official_name:
            # 기차역 -> 세부 동네 이동 거리 및 시간 계산
            to_sub_dist = calculate_distance(st_lat, st_lng, center_lat, center_lng)
            w_min, c_min, r_dist = estimate_travel_time(to_sub_dist)
            st.info(
                f"🚆 **도착역:** {st_official_name} ➔ 📍 **탐색 지역:** **{center_name}** ({center_addr})\n\n"
                f"*(역에서 {center_name}까지: 약 {r_dist/1000:.1f}km | 택시/차량 약 {c_min}분)*"
            )
        else:
            st.info(f"📍 탐색 기준: **{center_name}** ({center_addr}) | 🚶 반경 **{radius}m** 내 맛집/카페/관광지 탐색")
            
    with col_banner2:
        st.link_button("🎫 코레일 시간표 조회", "https://www.letskorail.com/", use_container_width=True)

    spots = search_category("AT4", center_lat, center_lng, radius, KAKAO_API_KEY)
    cafes = search_category("CE7", center_lat, center_lng, radius, KAKAO_API_KEY)
    restaurants = search_category("FD6", center_lat, center_lng, radius, KAKAO_API_KEY)

    col_map, col_details = st.columns([1.3, 1])

    # ----------------------------------------------------
    # 지도 렌더링
    # ----------------------------------------------------
    with col_map:
        m = folium.Map(location=[center_lat, center_lng], zoom_start=14)
        
        # 기차역 마커 (검은색 별)
        folium.Marker(
            location=[st_lat, st_lng],
            popup=f"<b>[기차역] {st_official_name}</b>",
            tooltip=f"출발 기차역: {st_official_name}",
            icon=folium.Icon(color="black", icon="star")
        ).add_to(m)

        # 세부 동네가 별도인 경우 파란색 핀 마커 표시
        if center_name != st_official_name:
            folium.Marker(
                location=[center_lat, center_lng],
                popup=f"<b>[세부 탐색지] {center_name}</b>",
                tooltip=f"동네 중심: {center_name}",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)

        # 탐색 반경 원
        folium.Circle(
            radius=radius,
            location=[center_lat, center_lng],
            color="#3186cc",
            fill=True,
            fill_opacity=0.08
        ).add_to(m)

        # 카테고리 마커
        def add_category_markers(items, color, icon_name, tag):
            for item in items:
                lat = float(item["y"])
                lng = float(item["x"])
                name = item["place_name"]
                dist = item.get("distance", "")
                dist_str = f"({dist}m)" if dist else ""
                folium.Marker(
                    location=[lat, lng],
                    popup=folium.Popup(f"<b>[{tag}] {name}</b><br>{dist_str}", max_width=250),
                    tooltip=f"[{tag}] {name} {dist_str}",
                    icon=folium.Icon(color=color, icon=icon_name)
                ).add_to(m)

        add_category_markers(spots, "green", "info-sign", "관광")
        add_category_markers(cafes, "orange", "heart", "카페")
        add_category_markers(restaurants, "red", "bookmark", "맛집")

        # 담은 코스 마커(보라색) 및 연결선
        if st.session_state.my_trip:
            route_coords = [[st_lat, st_lng]]
            for idx, p in enumerate(st.session_state.my_trip, 1):
                route_coords.append([p["lat"], p["lng"]])
                folium.Marker(
                    location=[p["lat"], p["lng"]],
                    popup=folium.Popup(f"<b>[코스 {idx}번] {p['name']}</b>", max_width=250),
                    tooltip=f"⭐ 내 코스 {idx}번: {p['name']}",
                    icon=folium.Icon(color="purple", icon="flag")
                ).add_to(m)

            folium.PolyLine(
                locations=route_coords,
                color="#6366f1",
                weight=4,
                opacity=0.8,
                dash_array="8, 8"
            ).add_to(m)

        st_folium(m, width="100%", height=530)

    # ----------------------------------------------------
    # 우측 탭별 목록 (담기 버튼)
    # ----------------------------------------------------
    with col_details:
        tab_spot, tab_cafe, tab_food = st.tabs([
            f"🏛️ 관광지 ({len(spots)})", 
            f"☕ 감성 카페 ({len(cafes)})", 
            f"🍽️ 현지 맛집 ({len(restaurants)})"
        ])
        
        def render_place_list_with_add(items, empty_text, category_tag):
            if not items:
                st.caption(empty_text)
                return
            for idx, item in enumerate(items, 1):
                name = item.get("place_name")
                addr = item.get("road_address_name") or item.get("address_name")
                phone = item.get("phone") or "전화번호 정보 없음"
                dist = item.get("distance")
                p_lat = float(item.get("y"))
                p_lng = float(item.get("x"))
                url = item.get("place_url")
                
                title = f"{idx}. {name}" + (f" (기준점에서 {dist}m)" if dist else "")
                with st.expander(title):
                    img_url = get_place_image(name, KAKAO_API_KEY)
                    if img_url:
                        st.image(img_url, use_container_width=True)
                    else:
                        st.caption("📷 등록된 이미지가 없습니다.")

                    st.write(f"**주소**: {addr}")
                    st.write(f"**전화번호**: {phone}")
                    if url:
                        st.markdown(f"[카카오맵 상세보기]({url})")

                    already_added = any(p["name"] == name for p in st.session_state.my_trip)
                    if not already_added:
                        if st.button(f"➕ 내 코스에 담기", key=f"add_{category_tag}_{idx}"):
                            st.session_state.my_trip.append({
                                "name": name,
                                "category": category_tag,
                                "addr": addr,
                                "lat": p_lat,
                                "lng": p_lng
                            })
                            st.rerun()
                    else:
                        if st.button(f"❌ 코스에서 제외", key=f"del_{category_tag}_{idx}"):
                            st.session_state.my_trip = [p for p in st.session_state.my_trip if p["name"] != name]
                            st.rerun()

        with tab_spot:
            render_place_list_with_add(spots, "반경 내 관광명소가 없습니다.", "관광")

        with tab_cafe:
            render_place_list_with_add(cafes, "반경 내 카페 정보가 없습니다.", "카페")

        with tab_food:
            render_place_list_with_add(restaurants, "반경 내 맛집 정보가 없습니다.", "맛집")

    st.markdown("---")

    # ----------------------------------------------------
    # 내 여행 코스 타임라인 & 이동시간
    # ----------------------------------------------------
    st.subheader(f"🗺️ {st_official_name} 출발 나만의 여행 코스 & 이동시간")

    if not st.session_state.my_trip:
        st.info("💡 위 추천 리스트에서 **[➕ 내 코스에 담기]**를 누르면 장소 간 이동시간과 동선이 자동으로 계산됩니다.")
    else:
        col_c_head, col_c_btn = st.columns([4, 1])
        with col_c_head:
            st.write(f"현재 총 **{len(st.session_state.my_trip)}개**의 장소가 담겼습니다. (지도 위 보라색 깃발과 점선 확인)")
        with col_c_btn:
            if st.button("🗑️ 코스 전체 비우기", use_container_width=True):
                st.session_state.my_trip = []
                st.rerun()

        # 기차역 출발 기준 경로 구성
        full_route = [{
            "name": f"🚆 {st_official_name} (도착역/출발점)",
            "category": "기차역",
            "lat": st_lat,
            "lng": st_lng,
            "addr": station_place.get("road_address_name") or station_place.get("address_name")
        }] + st.session_state.my_trip

        total_walk_time = 0
        total_car_time = 0
        total_distance = 0

        for i in range(len(full_route)):
            curr_place = full_route[i]
            
            with st.container(border=True):
                col_info, col_del = st.columns([5, 1])
                with col_info:
                    st.markdown(f"**Step {i+1} : {curr_place['name']}** `[{curr_place['category']}]`")
                    st.caption(f"위치: {curr_place['addr']}")
                with col_del:
                    if i > 0:
                        if st.button("삭제", key=f"remove_course_{i}"):
                            st.session_state.my_trip.pop(i - 1)
                            st.rerun()

            if i < len(full_route) - 1:
                next_place = full_route[i + 1]
                dist = calculate_distance(curr_place["lat"], curr_place["lng"], next_place["lat"], next_place["lng"])
                w_time, c_time, r_dist = estimate_travel_time(dist)
                
                total_distance += r_dist
                total_walk_time += w_time
                total_car_time += c_time

                # 거리가 10km 이상으로 너무 멀면 장거리 알림 표시
                dist_warning = " ⚠️ *(동선이 멉니다)*" if r_dist > 10000 else ""
                
                st.markdown(
                    f"""
                    <div style="margin-left: 30px; padding: 6px 12px; border-left: 2px dashed #6366f1; color: #475569; font-size: 0.9em;">
                        ⬇️ 이동 거리: <b>약 {r_dist:,}m</b>{dist_warning} | 🚶 도보 <b>약 {w_time}분</b> | 🚕 택시/차량 <b>약 {c_time}분</b>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

        st.success(
            f"📊 **코스 총 이동 통계:** 총 이동거리 **약 {total_distance/1000:.1f}km** | "
            f"도보 누적 **약 {total_walk_time}분** | 차량/택시 누적 **약 {total_car_time}분**"
        )

    st.markdown("---")

    # ----------------------------------------------------
    # 하단 2x2 그리드 (날씨 / 옷차림 / 환율 / 계산기)
    # ----------------------------------------------------
    col_left, col_right = st.columns(2)

    weather_info = get_weather_and_air(center_lat, center_lng)
    temp = weather_info.get("temp")
    humidity = weather_info.get("humidity")
    wind = weather_info.get("wind")
    pm10 = weather_info.get("pm10")
    pm2_5 = weather_info.get("pm2_5")
    air_status, air_icon = get_air_quality_status(pm10, pm2_5)

    with col_left:
        with st.container(border=True):
            st.markdown(f"#### ⛅ {center_name} 실시간 날씨 & 공기질")
            w_c1, w_c2, w_c3 = st.columns(3)
            with w_c1:
                st.metric("현재 기온", f"{temp} °C" if temp is not None else "-")
            with w_c2:
                st.metric("습도", f"{humidity} %" if humidity is not None else "-")
            with w_c3:
                st.metric("풍속", f"{wind} km/h" if wind is not None else "-")

            st.markdown("---")
            a_c1, a_c2 = st.columns(2)
            with a_c1:
                st.write(f"**미세먼지 상태:** {air_icon} {air_status}")
            with a_c2:
                st.caption(f"PM10: {pm10}㎍/㎥ | 초미세: {pm2_5}㎍/㎥" if pm10 is not None else "측정 중")

    with col_right:
        with st.container(border=True):
            st.markdown("#### 👕 기차 여행 맞춤 옷차림 & 팁")
            outfit = get_outfit_recommendation(temp)
            st.write(f"**{outfit['title']}** : {outfit['desc']}")
            st.markdown("**추천 아이템:**")
            st.write(", ".join(outfit["items"]))
            if pm10 and pm10 > 80:
                st.warning("⚠️ 미세먼지가 높습니다. 마스크를 챙기세요.")
            else:
                st.success("✨ 쾌적한 뚜벅이 여행이 가능한 날씨입니다.")

    with col_left:
        with st.container(border=True):
            st.markdown("#### 💵 실시간 주요 환율 (USD)")
            usd_krw = get_rate("USD", "KRW")
            usd_jpy = get_rate("USD", "JPY")
            usd_eur = get_rate("USD", "EUR")

            r1, r2, r3 = st.columns(3)
            with r1:
                if usd_krw:
                    st.metric("USD / KRW", f"{usd_krw:,.2f} 원")
            with r2:
                if usd_jpy:
                    st.metric("USD / JPY", f"{usd_jpy:,.2f} 엔")
            with r3:
                if usd_eur:
                    st.metric("USD / EUR", f"{usd_eur:,.4f} €")
            st.caption("실시간 국제 외환 시장 기준")

    with col_right:
        with st.container(border=True):
            st.markdown("#### 💱 실시간 환율 계산기")
            currencies = ["USD", "KRW", "JPY", "EUR", "CNY", "GBP"]
            c_top1, c_top2, c_top3 = st.columns([1.5, 1, 1])
            with c_top1:
                c_amount = st.number_input("금액", min_value=0.0, value=100.0, step=10.0, label_visibility="collapsed")
            with c_top2:
                f_curr = st.selectbox("보내는 통화", currencies, index=0, label_visibility="collapsed")
            with c_top3:
                t_curr = st.selectbox("받는 통화", currencies, index=1, label_visibility="collapsed")

            rate = get_rate(f_curr, t_curr)
            if rate is not None:
                conv = c_amount * rate
                st.success(f"**{c_amount:,.2f} {f_curr}** = **{conv:,.2f} {t_curr}**")
                st.caption(f"적용 환율: 1 {f_curr} = {rate:,.4f} {t_curr}")
            else:
                st.caption("환율 계산기 일시 중단")