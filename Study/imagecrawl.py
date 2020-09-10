from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup as bs
import os



if __name__ == "__main__":
    url = "https://search.naver.com/search.naver?where=image&sm=tab_jum&query="         #네이버 이미지 url
    query = input("검색어 입력 : ")

    url = url + quote_plus(query)    # quote_plus 함수는 공백을 + 로 처리함
    html = urlopen(url)
    soup = bs(html,'html.parser')
    img = soup.find_all(class_='_img')     # 네이버 img에 해당하는 구조

    n = 1

    print(img[0])
    
    # 경로가 없으면 경로생성
    if os.path.isdir('./images') == False:
        os.makedirs('./images')


    for i in img:
        if n > 10:
            break
        print(n)
        imgUrl = i['data-source']
        with urlopen(imgUrl) as f:
            with open('./images/img' + str(n)+ '.jpg','wb') as h:   # 파일명
                img = f.read()
                h.write(img)
        n += 1

    print("이미지 크롤링 종료")