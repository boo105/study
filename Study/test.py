from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

Data = {
    '리뷰 제목' : [],
    '리뷰 내용' : []
}

options = webdriver.ChromeOptions()
#options.add_argument('headless') # 크롤링 동안 크롬창 없이 크롤링
options.add_argument("--log-level=3") # 콘솔로그 제거
driver = webdriver.Chrome("../chromedriver.exe", options=options)
url = "https://www.ybtour.co.kr/eplg/episodeList.yb?pageNo=1&bestYn=&writeDiviCd=&subDspMenu=&srchParam=&srchParamContent=&searchCnd=ALL&searchWrd=%EB%B2%A0%ED%8A%B8%EB%82%A8"
driver.get(url)  # url 접속
time.sleep(1) # 1초 지연  페이지로드 할때나 이동할때 (변화가 있을때) 넣는다


page = 1
count = 0
tr_idx = 0


while True:
    container = driver.find_elements_by_css_selector('table.tbl_board > tbody > tr')  # 여행 리뷰들

    link = container[tr_idx].find_element_by_css_selector('td > a')
    driver.execute_script("arguments[0].click();",link)
    time.sleep(2)

    title = driver.find_element_by_css_selector('span.tit_brd_w').text
    content = driver.find_element_by_css_selector('.editor_area').text
    print(title)
    print(content)

    Data['리뷰 제목'].append(title)
    Data['리뷰 내용'].append(content)

    driver.back()
    time.sleep(1)

    print("tr_idx : " + str(tr_idx))
    print("count : " + str(count))
    if tr_idx == 19:
        tr_idx = 0

        next_button = driver.find_element_by_css_selector('a.btn_page_next')
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(2)
    else :
        tr_idx += 1

    # 500개 크롤링하면 종료
    if count == 500:
        break
    else:
     count += 1


print("크롤링 완료!")
final_data = pd.DataFrame(Data)  # 판다스를 이용한 데이터화
final_data.to_excel('여행지 리뷰.xlsx', index=False)