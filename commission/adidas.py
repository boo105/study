from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time
import os
import re

if __name__ == "__main__":
    url_man = "https://shop.adidas.co.kr/PF070801.action?S_CTGR_CD=01001&pageNo=1390&S_ORDER_BY=1&PROD_CL_CD=1&S_SIZE=&S_COLOR=&S_COLOR2=&S_PRICE=&S_STATE1=&S_STATE2=&S_STATE3=&NFN_ST=Y"  # 아디다스 남성신발
    url_woman = "https://shop.adidas.co.kr/PF070801.action?S_CTGR_CD=01002&pageNo=1390&S_ORDER_BY=1&PROD_CL_CD=1&S_SIZE=&S_COLOR=&S_COLOR2=&S_PRICE=&S_STATE1=&S_STATE2=&S_STATE3=&NFN_ST=Y" # 아디다스 여성신발

    options = webdriver.ChromeOptions()
    options.add_argument('headless')  # 크롤링 동안 크롬창 없이 크롤링
    options.add_argument("--log-level=3")  # 콘솔로그 제거
    driver = webdriver.Chrome("C:\\Users\\user\\Desktop\\MinHo\\GitHub\\study\\chromedriver.exe", options=options)
    driver.get(url_woman)  # url 접속
    time.sleep(1)  # 1초 지연  페이지로드 할때나 이동할때 (변화가 있을때) 넣는다

    # 경로가 없으면 경로생성
    if os.path.isdir('./woman') == False:
        os.makedirs('./woman')

    page = 1
    while(True):
        print(str(page) + "번째 페이지입니다.")

        html = driver.page_source
        soup = bs(html, 'html.parser')

        # 이미지
        # 아디다스는 item performance 와 item originals 두 종류로 나눠져 태그를 이룸
        img_first = soup.select('.item.performance > .inner > .img > a > img')  # img에 해당하는 구조      59개
        img_second = soup.select('.item.originals > .inner > .img > a > img')  # .item.originals > .inner > .img > a        41개

        # print(img_first)
        # print(img_second)

        try:
            for img in img_first:
                title = img['alt']
                """
                temp = title.split(']')
                if len(temp) > 2:
                    title = temp[2]
                else:
                    title = temp[1]
                """
                imgUrl = img['src']
                imgUrl = "http:" +imgUrl
                code = imgUrl.split('/')[7].split('-')[0]   # 제품코드

                with urlopen(imgUrl) as f:
                    with open('./woman/' + str(title) + " (" + code + ').jpg', 'wb') as h:  # 파일명
                        img = f.read()
                        h.write(img)

            print("---- Second ----")
            for img in img_second:
                title = img['alt']
                """
                if len(temp) > 2:
                    title = temp[2]
                else:
                    title = temp[1]
                """
                imgUrl = img['src']
                imgUrl = "http:" + imgUrl
                code = imgUrl.split('/')[7].split('-')[0]  # 제품코드

                with urlopen(imgUrl) as f:
                    with open('./woman/' + str(title) + " (" + code + ').jpg', 'wb') as h:  # 파일명
                        img = f.read()
                        h.write(img)
        except IndexError:
            break

        if page == 4:
            break

        button = driver.find_element_by_css_selector(".paging_button > a.next")  # 다음 버튼
        driver.execute_script("arguments[0].click();", button)  # 버튼에 해당하는 자바 스크립트 실행.button_more_text
        page += 1

    print("이미지 크롤링 종료")