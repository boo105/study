from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

Data = {
    '지역': [],
    '위치': [],
    '사업명': [],
    '공급규모': [],
    '시공사': [],
    '모집 공고일': [],
    '당첨자 발표일': [],
    '입주예정월': [],
    '사업주체 전화번호': []
}

options = webdriver.ChromeOptions()
options.add_argument('headless')  # 크롤링 동안 크롬창 없이 크롤링
options.add_argument("--log-level=3")  # 콘솔로그 제거
driver = webdriver.Chrome("chromedriver.exe", options=options)
url = "https://drapt.com/e_sale/index.htm?page_name=cal&menu_key=0"
driver.get(url)  # url 접속
time.sleep(1)  # 1초 지연  페이지로드 할때나 이동할때 (변화가 있을때) 넣는다

page = 1

year_list = [["2017.01.01","2017.04.01"],["2017.04.02","2017.07.01"],["2017.07.02","2017.10.01"],
             ["2018.01.01","2018.04.01"],["2018.04.02","2018.07.01"],["2018.07.02","2018.10.01"],
             ["2019.01.01","2019.04.01"],["2019.04.02","2019.07.01"],["2019.07.02","2019.10.01"],
             ["2020.01.01","2020.04.01"],["2020.04.02","2020.07.01"],["2020.07.02","2020.10.01"]]
test = ["2020.09.01","2020.10.01"]

idx = 0

def get_date(text):
    # 예외 처리
    text = text.split("~")
    text = text[0]
    try:
        text = text.split("년")
        year = text[0]  # 문자열
        text = text[1].split("월")
        month = int(text[0])
        if text[1] != '':
            day = int(text[1].replace("일", ""))
        else :
            day = "1"
        text = ".".join([year, " " + str(month), " " + str(day)])
    except :
        print("Fuck")
    return text

sucess = False
isPass = False

while True:
    if idx == 12:
        break

    date_input = driver.find_elements_by_css_selector('span.calendar_setting_02_inn > input')
    first_date = date_input[0]
    second_date = date_input[1]

    first_date.clear()
    second_date.clear()
    first_date.send_keys(year_list[idx][0])
    second_date.send_keys(year_list[idx][1])
    #first_date.send_keys(test[0])
    #second_date.send_keys(test[1])
    second_date.send_keys(Keys.RETURN)  # 엔터키를 누른다
    time.sleep(2)

    try:
        alert = driver.switch_to_alert()
        alert.accept()
        driver.switch_to_default_content()
        time.sleep(1)
    except:
        tr = driver.find_elements_by_css_selector('tbody#myList > tr')
        if len(tr) > 50:
            sucess = True
            print("성공")
        else:
            print("조회안됨")
            sucess = False

        """
        if idx < 11:
            if sucess == True:
                idx += 1
                sucess = False
            isPass = True
        else:
            isPass = False
        """

        if sucess == True : #and isPass == False:
            tr = driver.find_elements_by_css_selector('tbody#myList > tr')
            for element in tr:
                link = element.find_elements_by_css_selector('a')
                link[0].click()
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(1)
                print(year_list[idx][0] + " ~ " + year_list[idx][1])

                title = driver.find_elements_by_css_selector('.one_tmenu_center > table > tbody >tr >td >h1 >span')
                title = title[0].text

                iframe = driver.find_element_by_css_selector('iframe#contents')
                driver.switch_to_frame(iframe)

                table = driver.find_elements_by_css_selector('div#detail_view  > table > tbody > tr')

                try:
                    print("빨간색 문의처")
                    number = driver.find_element_by_css_selector('p.grayBl_tit > span').text
                    number = number.split(": ")[1].replace("]","")
                    print(number)
                except:
                    print("분양개요 문의처")
                    try:
                        number = driver.find_elements_by_css_selector('div#bun_view1 >.pt07 > table >tbody >tr > td')
                        number = number[1].text
                    except:
                        number = "없음"

                if len(table) == 8:
                    print("신규 특별 양식")
                    table2 = driver.find_elements_by_css_selector('div#bun_view3_1 > table > tbody > tr')
                    developer = table[6].find_element_by_css_selector('td').text

                    for tr in table:
                        th = tr.find_element_by_css_selector('th').text
                        if th == "주소":
                            location = tr.find_element_by_css_selector('td').text
                            local = location.split(" ")[0]
                        elif th == "단지규모":
                            size = tr.find_element_by_css_selector('td').text
                            size = size.split("총")[1].split("가구")[0]
                        elif th == "입주시기":
                            move_in = tr.find_element_by_css_selector('td').text
                            move_in = get_date(move_in)
                        elif th == "시공사":
                            developer = tr.find_element_by_css_selector('td').text

                        isFind = False
                        # 테이블2에 대한것
                        for tr in table2:
                            try:
                                th = tr.find_element_by_css_selector('th').text
                            except:
                                continue
                            if th == "입주자 모집공고" and isFind == False:
                                announce_date = tr.find_element_by_css_selector('td').text
                                announce_date = get_date(announce_date)
                                isFind = True
                            elif th == "당첨자발표":
                                draw = tr.find_element_by_css_selector('td').text
                                draw = get_date(draw)
                else:
                    developer = table[3].find_element_by_css_selector('td').text
                    table2 = driver.find_elements_by_css_selector('div#bun_view2 > div > table > tbody >tr')

                    if (len(table2) == 0):
                        print("옛날정보 양식")
                        # table 1에 대한것
                        for tr in table:
                            th = tr.find_element_by_css_selector('th').text
                            if th == "주소":
                                location = tr.find_element_by_css_selector('td').text
                                local = location.split(" ")[0]
                            elif th == "단지규모":
                                size = tr.find_element_by_css_selector('td').text
                                size = size.split("총")[1].split("가구")[0]
                            elif th == "입주시기":
                                move_in = tr.find_element_by_css_selector('td').text
                                move_in = get_date(move_in)
                            elif th == "시공사":
                                developer = tr.find_element_by_css_selector('td').text

                            announce_date = "없음"
                            draw = "없음"
                    else:
                        print("신규양식")
                        # 넘버 (개별)
                        table2 = driver.find_elements_by_css_selector('div#bun_view2 > div > table > tbody >tr')
                        button = driver.find_element_by_css_selector('div#bun_view2 >.pt07 > ul.common_tab01 > li.on > a')
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(1)

                        # table 1에 대한것
                        for tr in table:
                            th = tr.find_element_by_css_selector('th').text
                            if th == "주소":
                                location = tr.find_element_by_css_selector('td').text
                                local = location.split(" ")[0]
                            elif th == "단지규모":
                                size = tr.find_element_by_css_selector('td').text
                                size = size.split("총")[1].split("가구")[0]
                            elif th == "입주시기":
                                move_in = tr.find_element_by_css_selector('td').text
                                move_in = get_date(move_in)

                        isFind = False
                        # 테이블2에 대한것
                        for tr in table2:
                            try:
                                th = tr.find_element_by_css_selector('th').text
                            except:
                                continue

                            if th == "입주자 모집공고" and isFind == False:
                                announce_date = tr.find_element_by_css_selector('td').text
                                announce_date = get_date(announce_date)
                                isFind = True
                            elif th == "당첨자발표":
                                draw = tr.find_element_by_css_selector('td').text
                                draw = get_date(draw)

                        try:
                            print(announce_date)
                        except:
                            announce_date = "없음"
                        try:
                            print(draw)
                        except:
                            draw = "없음"

                Data['지역'].append(local)
                Data['위치'].append(location)
                Data['사업명'].append(title)
                Data['공급규모'].append(size)
                Data['시공사'].append(developer)
                Data['모집 공고일'].append(announce_date)
                Data['당첨자 발표일'].append(draw)
                Data['입주예정월'].append(move_in)
                Data['사업주체 전화번호'].append(number)

                print("지역 : " + local)
                print("위치 : " + location)
                print("사업명 : " + title)
                print("공급규모 : " + size)
                print("시공사 : " + developer)
                print("모집 공고일 : " + announce_date)
                print("당첨자 발표일 : " + draw)
                print("입주예정월 : " + move_in)
                print("사업주체 전화번호 : " + number + "\n\n\n")

                driver.switch_to_default_content()
                driver.switch_to.window(driver.window_handles[0])  # 맨 처음 탭으로 변경`
            idx += 1
            sucess = False

print("크롤링 완료!")
final_data = pd.DataFrame(Data)  # 판다스를 이용한 데이터화
final_data.to_excel('drapt.xlsx', index=False)