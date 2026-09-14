# folium으로 지도에 마커를 표시하는 예제 코드
# import folium
# 서울 시내 명소 4곳의 좌표(경도/위도)와 이름을 리스트로 받아 folium 지도를 만들고
# 각 좌표에 이름표가 붙은 마커를 찍은 다음, basic_map.html 파일로 저장하는 예제 코드입니다.
# 저장된 basic_map.html 웹 브라우저로 열어서 확인
# 실행 : python 09-14_1.py

import folium
import os
import webbrowser

# 1. 서울 시내 명소 4곳 데이터 (이름, 위도, 경도)
places = [
    {"name": "서울시청", "lat": 37.5665, "lon": 126.9780},
    {"name": "경복궁", "lat": 37.5796, "lon": 126.9770},
    {"name": "남산타워", "lat": 37.5512, "lon": 126.9882},
    {"name": "강남역", "lat": 37.4979, "lon": 127.0276},
]

# 지도의 시작 중심 좌표(서울시청 기준) 지정해서 folium지도 객체 생성
# 숫자가 클수록 더 가깝게 보여준다.
# zoom_start 숫자가 클수록 지도를 더 확대(가깝게)해서 보여줍니다.
# 기존 코드:
# seoul_center = folium.Map(location=[places[0]["lat"], places[0]["lon"]], zoom_start=13)

# 수정 코드: CartoDB 타일로 변경
seoul_center = folium.Map(
    location=[places[0]["lat"], places[0]["lon"]],
    zoom_start=13,
    max_zoom=19,
    tiles="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
    attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles style by <a href="https://www.hotosm.org/">Humanitarian OpenStreetMap Team</a>'
)

# 리스트에 담긴 장소들을 하나씩 꺼내며 지도 위 마커를 추가
# 반복문을 돌며 지도에 마커 추가
for place in places:
    folium.Marker(
        location=[place["lat"], place["lon"]],
        popup=folium.Popup(place["name"], max_width=200),
        tooltip=place["name"],
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(seoul_center)

# 1. HTML 파일로 저장
output_file = "basic_map.html"
seoul_center.save(output_file)

# 2. 저장된 파일의 절대 경로를 가져와 기본 브라우저 새 탭으로 열기
file_path = os.path.abspath(output_file)
webbrowser.open_new_tab(f"file://{file_path}")

print(f"지도가 생성되어 브라우저에서 열렸습니다: {output_file}")