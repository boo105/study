from selenium import webdriver # 동적 페이지 크롤링을 위한 selenium
import pandas as pd # 데이터 조작 및 저장을 위한 pandas
import time # 페이지 로드를 위해서 시간 지연을 주기 위한 time

music = {
    'title' : [],
    'artist' : [],
    'album' : []
}

options = webdriver.ChromeOptions()
options.add_argument('headless') # 크롤링 동안 크롬창 없이 크롤링
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
#options.add_argument("--log-level=3") # 콘솔로그 제거
driver = webdriver.Chrome('chromedriver.exe',options=options)
url = 'https://vibe.naver.com/chart/total'
driver.get(url)
time.sleep(2)
# div.tracklist > table > tbody > tr 반복
# div.title_badge_wrap > span > a.link_text 제목 태그
# td.artist 가수
# td.album > a 앨범
close_button = driver.find_element_by_css_selector('div.ly_popup > a.btn_close')
driver.execute_script("arguments[0].click();", close_button)
time.sleep(0.5)

button = driver.find_element_by_css_selector('a.link > span.text')
driver.execute_script("arguments[0].click();",button)
time.sleep(2)

container = driver.find_elements_by_css_selector('div.tracklist > table > tbody > tr')
for tr in container:
    music['title'].append(tr.find_element_by_css_selector('div.title_badge_wrap > span > a.link_text').text)
    music['artist'].append(tr.find_element_by_css_selector('td.artist').text)
    music['album'].append(tr.find_element_by_css_selector('td.album > a').text)

print(music)
final_data = pd.DataFrame(music)
final_data.to_excel('crawl.xlsx',index=False)