from selenium import webdriver
import pandas as pd
import time

reviews = {
    'UserId' : [],
    'Date' : [],
    'Option' : [],
    'Review' : [],
    'Score' : []
}

options = webdriver.ChromeOptions()
options.add_argument('headless') # 크롤링 동안 크롬창 없이 크롤링
options.add_argument("--log-level=3") # 콘솔로그 제거
driver = webdriver.Chrome("chromedriver.exe", options=options)
url = "https://smartstore.naver.com/yomamdde/products/404338042#revw"
driver.get(url)  # url 접속
time.sleep(1) # 1초 지연  페이지로드 할때나 이동할때 (변화가 있을때) 넣는다

# div.tracklist > table > tbody > tr 반복
# div.title_badge_wrap > span > a.link_text 제목 태그
# td.artist 가수
# td.album > a 앨범


# get_attribute('title') 속성값이 뽑힘

page = 1
next_page = 1

while(True):
    print(page)

    contaniner = driver.find_elements_by_css_selector("div.area_user_review")

    # 더보기 버튼 해당 페이지에 모든 리뷰 누르고 시작함
    for tr in contaniner:
        button = driver.find_element_by_css_selector(".button_more_text")
        driver.execute_script("arguments[0].click();", button)  # 버튼에 해당하는 자바 스크립트 실행.button_more_text
        time.sleep(1)

    for tr in contaniner:
       temp = tr.find_elements_by_css_selector("div>div>.area_status_user > span.text_info")
       reviews['UserId'].append(temp[0].text)
       reviews['Date'].append(temp[1].text)
       try:
        reviews['Option'].append(tr.find_element_by_css_selector("div.area_status_user >  p").text)
       except:
        reviews['Option'].append(None)
       reviews['Review'].append(tr.find_element_by_css_selector(".review_text._review_text > .text").text)
       reviews['Score'].append(tr.find_element_by_css_selector("div.area_star_small > .number_grade").text)

    if(page==100):
        break

    try:
        # 10페이지 단위당 다음 버튼을 클릭함
        if(page%10 == 0):
            next_button = driver.find_element_by_css_selector("a.page.next")
            driver.execute_script("arguments[0].click();", next_button)  # 버튼에 해당하는 자바 스크립트 실행
            next_page = 1
            time.sleep(1)
        else:   # 한페이지 단위로 넘김
            next_button = driver.find_elements_by_css_selector(".module_pagination._review_list_page > .page.number")[next_page]
            driver.execute_script("arguments[0].click();", next_button)  # 버튼에 해당하는 자바 스크립트 실행
            next_page +=1
            time.sleep(1)
    except IndexError:
        break

    page += 1


print(reviews)
final_data = pd.DataFrame(reviews)  # 판다스를 이용한 데이터화
final_data.to_excel('pythoncide.xlsx', index=True)