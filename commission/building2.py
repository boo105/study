from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

Data = {
    '지역' : [],
    '위치' : [],
    '사업명' : [],
    '공급규모' : [],
    '시공사' : [],
    '모집 공고일' : [],
    '당첨자 발표일' : [],
    '입주예정월' : [],
    '사업주체 전화번호' : []
}

options = webdriver.ChromeOptions()
#options.add_argument('headless') # 크롤링 동안 크롬창 없이 크롤링
options.add_argument("--log-level=3") # 콘솔로그 제거
driver = webdriver.Chrome("chromedriver.exe", options=options)
url = "https://onland.kbstar.com/quics?page=C059693&QSL=F"
driver.get(url)  # url 접속
time.sleep(1) # 1초 지연  페이지로드 할때나 이동할때 (변화가 있을때) 넣는다

koreas_count = 0
next_page_list = [9,9,4,6,2,5,1,0,3,3,3,7,3,4,2,4,1]
list_page_list = [62,22,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
final_next_page_list = [8,11,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

while True:
    iframe = driver.find_element_by_css_selector('iframe#kms')
    driver.switch_to_frame(iframe)
    try:
        koreas = driver.find_elements_by_css_selector('div#fltAddrArea1 > ul.sel_list > li > a')
        element = koreas[koreas_count]
    except:
        break

    driver.execute_script("arguments[0].click();", element)
    time.sleep(1)
    button = driver.find_element_by_css_selector('.SYListView > button')
    driver.execute_script("arguments[0].click();",button)
    time.sleep(1)

    page = 1
    print(page)
    page += 1

    next_page = next_page_list[koreas_count]
    tr_idx = 0
    first = False
    driver.switch_to_default_content()

    while True:
        iframe = driver.find_element_by_css_selector('iframe#kms')
        driver.switch_to_frame(iframe)

        # 한 페이지에 정보를 다 읽었다면
        if tr_idx == 10:
            print("현재 페이지 : " + str(page))
            if list_page_list[koreas_count] != 0:
                if page >= list_page_list[koreas_count]:
                    next_page = final_next_page_list[koreas_count]
                    print("ㅎㅇ")
                    print(final_next_page_list[koreas_count])
            try :
                next_button = driver.find_elements_by_css_selector('span.PagingContent')
                next_button = next_button[1].find_elements_by_css_selector('a')
                driver.execute_script("arguments[0].click();",next_button[next_page])
                time.sleep(1)
            except:        # 다음버튼이 없으면 끝이라는 소리이므로 중지
                break

            # 페이지 카운트 및 tr 정보 초기화
            tr_idx = 0
            page += 1
            if first == False:
                next_page = next_page + 2
                first = True
            print("10개 끝")

        #if page < 70 :
            #tr_idx = 10
            #driver.switch_to_default_content()
            #continue

        print(tr_idx)
        # 10개의 tr정보를 가져옴
        tr = driver.find_elements_by_css_selector('table > tbody > tr')
        print(tr)
        try:
            link = tr[tr_idx].find_element_by_css_selector('td > a')
        except:
            break

        driver.execute_script("arguments[0].click();",link)
        time.sleep(1)

        table = driver.find_elements_by_css_selector('.tbl_read > table')
        table = table[0].find_elements_by_css_selector('tbody > tr')

        location = table[0].find_element_by_css_selector('td').text
        local = location.split(" ")[0]

        title = driver.find_element_by_css_selector('.hgroup > div >h3').text

        size = table[1].find_element_by_css_selector('td>p').text

        if '실' in size:
            size = size.split("실")[0].split("총 ")[1]
        else :
            size = size.split("세")[0].split("총 ")[1]
        size = size.replace(",","")
        #print(size)

        if len(table) == 9:
            try:
                temp = table[7].find_element_by_css_selector('th > div').text
                print(temp)
                if temp != "건설사":
                    developer = "없음"
                else:
                    developer = table[7].find_element_by_css_selector('td > div').text
            except :
                developer = "없음"
            number = table[8].find_element_by_css_selector('td').text
        elif len(table) == 10:
            developer = table[8].find_element_by_css_selector('td > div').text
            number = table[9].find_element_by_css_selector('td').text
        elif len(table) == 8:
            developer = "없음"
            number = table[7].find_element_by_css_selector('td').text


        announce_date = table[2].find_element_by_css_selector('td').text
        if announce_date != "":
            announce_date = announce_date.split(".")
            month = int(announce_date[1])
            day = int(announce_date[2])
            announce_date = ".".join([announce_date[0]," " + str(month)," " + str(day)])
        else :
            announce_date = "미정"


        move_in = table[3].find_element_by_css_selector('td').text
        if "상반기" in move_in:
            move_in = move_in.split("상반기")[0]
            move_in = ".".join([move_in[0], " 1"," 1"])
        else:
            print(move_in)
            if move_in == "":
                move_in = "미정"
            elif move_in == "미정":
                move_in = "미정"
            else :
                move_in= move_in.split(".")
                if len(move_in) > 1:
                    month = int(move_in[1])
                    move_in = ".".join([move_in[0]," " + str(month)," 1"])
                else:
                    move_in = ".".join([move_in[0], " 1"," 1"])

        draw = driver.find_elements_by_css_selector('.tbl_list > table >tbody >tr')
        if len(draw) < 4 or len(draw) >= 7:
            draw = "없음"
        else :
            draw = draw[2].find_element_by_css_selector('td').text
            draw = draw.split("~")[0]
            draw = draw.split(".")
            month = int(draw[1])
            day = int(draw[2])
            draw = ".".join([draw[0], " " + str(month), " " + str(day)])

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

        # 정보 크롤링 하는 내용
        driver.back()

        tr_idx += 1
        driver.switch_to_default_content()

    koreas_count += 1
    driver.switch_to_default_content()


print("크롤링 완료!")
final_data = pd.DataFrame(Data)  # 판다스를 이용한 데이터화
final_data.to_excel('KB부동산.xlsx', index=False)