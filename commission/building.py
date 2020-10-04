from selenium import webdriver
import re
import pandas as pd
import time

Data = {
    '지역' : [],
    '위치' : [],
    '사업명' : [],
    '공급규모' : [],
    '시행사' : [],
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
url = "https://www.applyhome.co.kr/ai/aib/selectSubscrptCalenderView.do#a"
driver.get(url)  # url 접속
time.sleep(1) # 1초 지연  페이지로드 할때나 이동할때 (변화가 있을때) 넣는다

year_list = ["2019","2020"]

page = 1

# 년도 선택
for y in year_list:
    if y == "2020":
        count = 1

    year = driver.find_element_by_xpath("//option[@value='" + y + "']")
    year.click()
    time.sleep(2);

    # 월 선택
    months = driver.find_elements_by_css_selector('.cal_bottom >ul> li > button')
    for button in months:
        print(page)
        #if page < 2:
            #page += 1
            #continue
        if y == "2020" and count == 11:
            break

        driver.execute_script("arguments[0].click();",button)
        time.sleep(2)


        container = driver.find_elements_by_css_selector('div.cal_wrap >table.tbl_st >tbody > tr >td')

        for td in container:
            links = td.find_elements_by_css_selector('a')
            for link in links:
                # 창 열기
                link.click()
                time.sleep(1)
                iframe = driver.find_element_by_css_selector('iframe.ui-dialog-content')
                driver.switch_to_frame(iframe)

                # 0 공급위치
                # 1 공급규모
                # 4 모집공고일
                # 5 당첨자발표일
                texts = driver.find_elements_by_css_selector('table.tbl_st >tbody >tr>td.txt_l')
                content = texts[0].text
                content = content.replace('\u3000',' ')
                local = content     # 위치
                content = content.split(" ")        # 지역

                title = driver.find_element_by_css_selector('th[colspan="2"]').text
                size = texts[1].text
                size = size.split("세대")[0]


                # 모집공고일
                table = driver.find_elements_by_css_selector('table.tbl_st')
                table = table[1].find_elements_by_css_selector('tbody >tr > td')
                announce_date = table[0].text.split("(")
                announce_date = announce_date[0].split("-")
                months = int(announce_date[1])
                day = int(announce_date[2])
                announce_date = [announce_date[0]," " + str(months)," " + str(day)]
                announce_date = ".".join(announce_date)
                #print(announce_date)

                table = driver.find_elements_by_css_selector('table.tbl_st')
                table = table[1].find_elements_by_css_selector('tbody> tr> td.txt_l')
                if len(table) == 4:
                    draw = table[2].text.split("(")
                else:
                    draw = table[1].text.split("(")
                draw = draw[0].split("-")
                months = int(draw[1])
                day = int(draw[2])
                draw = [draw[0], " " + str(months), " " + str(day)]
                draw = ".".join(draw)

                move_in = driver.find_elements_by_css_selector('ul.inde_txt')
                none = False
                if len(move_in) == 4:
                    move_in = move_in[2].find_element_by_css_selector('li').text
                elif len(move_in) == 2:
                    move_in= move_in[0].find_element_by_css_selector('li').text
                elif len(move_in) == 3:
                    move_in = move_in[1].find_element_by_css_selector('li').text
                else :
                    move_in = driver.find_elements_by_css_selector('ul.inde_txt>li')
                    none = True

                if none == False:
                    origin = move_in.split(':')[1]
                else:
                    if len(move_in) >1:
                        origin = move_in[2].text.split(':')[1]
                    else:
                        origin = move_in[0].text.split(':')[1]

                move_in = origin.split('.')
                # 형식이 - 로 되있는 경우
                if len(move_in) < 2:
                    move_in = origin.split('-')
                months = int(move_in[1])
                move_in = [move_in[0].replace(" ",""), " " + str(months), " 1"]
                move_in = ".".join(move_in)

                print(move_in)



                none = False
                temp = driver.find_elements_by_css_selector('div#printArea >table.tbl_st')
                if len(temp) == 3:
                    temp = temp[2].find_elements_by_css_selector('tbody>tr>td')
                elif len(temp) == 4:
                    temp = temp[3].find_elements_by_css_selector('tbody>tr>td')
                else:
                    none = True

                if none == False:
                    if len(temp) != 2:
                        develpoer = temp[0].text
                        constructor = temp[1].text
                        number = temp[2].find_element_by_css_selector('a').text
                        #print(number)
                    else :
                        develpoer = temp[0].text
                        constructor = "동일"
                        number = temp[1].find_element_by_css_selector('a').text
                        #print(number)
                else :
                    develpoer = "없음"
                    constructor = "없음"


                print(number)

                #print(develpoer)
                #print(constructor)

                Data['지역'].append(content[0])
                Data['위치'].append(local)
                Data['사업명'].append(title)
                Data['공급규모'].append(size)
                Data['시행사'].append(develpoer)
                Data['시공사'].append(constructor)
                Data['모집 공고일'].append(announce_date)
                Data['당첨자 발표일'].append(draw)
                Data['입주예정월'].append(move_in)
                Data['사업주체 전화번호'].append(number)

                driver.switch_to_default_content()

                # 창 닫기
                close_button = driver.find_element_by_css_selector('div.ui-dialog-titlebar > button')
                close_button.click()
        page += 1
        if y == "2020":
            count += 1

print("크롤링 완료!")
final_data = pd.DataFrame(Data)  # 판다스를 이용한 데이터화
final_data.to_excel('청약홈.xlsx', index=False)