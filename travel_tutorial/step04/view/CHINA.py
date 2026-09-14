from component.country_card import render_country_page
# 특정 함수만 호출할 때

render_country_page(
    flag="🇨🇳",
    country_name="중국",
    country_description=(
        "동아시아에 위치한 인구 약 14억 명의 광대한 국가로, 수도는 베이징입니다.\n\n"
        "세계 2위 규모의 거대한 내수 시장과 제조업 경쟁력을 기반으로 글로벌 경제의 핵심 축을 담당하고 있습니다.\n\n"
        "만리장성, 자금성 등 수천 년의 유구한 역사 유적과 지역별로 다채롭게 발전한 전통 음식 및 생활 문화를 자랑합니다."
    ),
    country_url="https://www.mct.gov.cn"
)