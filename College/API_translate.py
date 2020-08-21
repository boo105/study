#!/usr/bin/env python
# coding: utf-8

###################################### 1. 구글 번역 API 유료 버전 ####################################################
from google.cloud import translate_v2 as translate
import pandas as pd
import os
import re

default_path = r"C:\Workspace\hotel"  # 경로
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:\Workspace\My First Project-44e9e89515d0.json"  # 권한
client = translate.Client()  # 번역기 시작

os.chdir(default_path)  # C:\Workspace\tour_gosu\hotel
country_list = os.listdir()  # 국가 리스트 추출

# 순회
for country in country_list:
    os.chdir(country)  # C:\Workspace\tour_gosu\tour\country
    city_list = os.listdir()  # 도시 리스트 추출

    for city in city_list:
        os.chdir(city + "\\review")  # C:\Workspace\tour_gosu\tour\country\city\review

        # 저장할 폴더 생성
        try:
            os.makedirs("translated_review")
        except:
            pass

        # 리뷰 리스트 읽어온다.
        review_list = os.listdir()
        try:
            review_list.remove("translated_review")
        except:
            pass
        try:
            review_list.remove("debug.log")
        except:
            pass

        for review in review_list:
            src_review = pd.read_csv(review, sep=",", encoding="UTF-8")
            tar_review = pd.DataFrame(columns=['index', 'title', 'rating', 'content', 'lang'])

            # index-label 매칭
            hotel_urls = pd.read_csv(r'..\hotel_urls.csv', encoding="UTF-8")  # title을 읽어오기 위해 hotel_urls를 불러온다.
            regex = re.compile(r'(hr_)(\d*)(.csv)')  # 정규 표현식
            hotel_index = int(regex.search(review).group(2))  # 파일 이름에서 index 추출.
            temp_hotel_urls = hotel_urls.loc[hotel_index]
            hotel_label = temp_hotel_urls['title']  # index를 통해 title 추출.

            hotel_label = re.sub('[\/:*?"<>|]', '', str(hotel_label))  # 특수문자 제거
            for index in range(0, len(src_review)):
                temp = src_review.loc[index]  # 리뷰 하나 불러오기

                if temp['lang'] == 'en':
                    tar_review.loc[index] = [temp['index'], temp['title'], temp['rating'], temp['content'],
                                             temp['lang']]
                else:
                    result = client.translate(temp['content'], target_language='en')
                    tar_review.loc[index] = [temp['index'], temp['title'], temp['rating'], result['translatedText'],
                                             temp['lang']]

                tar_review.to_csv(r'.\translated_review\hotel_review_{}.csv'.format(hotel_label), encoding="UTF=8",
                                  index=False)
                print(review, '의 ', index, '번 째 번역 완료 !!')
######################################################################################################################


###################################### 2. 구글 번역 API 무료 버전 ####################################################
from googletrans import Translator
import pandas as pd
import os
import re

default_path = r"C:\Workspace\hotel"  # 경로
translator = Translator()  # 번역기 시작

os.chdir(default_path)  # C:\Workspace\tour_gosu\hotel
country_list = os.listdir()  # 국가 리스트 추출

# 순회
for country in country_list:
    os.chdir(country)  # C:\Workspace\tour_gosu\tour\country
    city_list = os.listdir()  # 도시 리스트 추출

    for city in city_list:
        os.chdir(city + "\\review")  # C:\Workspace\tour_gosu\tour\country\city\review

        # 저장할 폴더 생성
        try:
            os.makedirs("translated_review")
        except:
            pass

        # 리뷰 리스트 읽어온다.
        review_list = os.listdir()
        try:
            review_list.remove("translated_review")
        except:
            pass
        try:
            review_list.remove("debug.log")
        except:
            pass

        for review in review_list:
            src_review = pd.read_csv(review, sep=",", encoding="UTF-8")
            tar_review = pd.DataFrame(columns=['index', 'title', 'rating', 'content', 'lang'])

            # index-label 매칭
            hotel_urls = pd.read_csv(r'..\hotel_urls.csv', encoding="UTF-8")  # title을 읽어오기 위해 hotel_urls를 불러온다.
            regex = re.compile(r'(hr_)(\d*)(.csv)')  # 정규 표현식
            hotel_index = int(regex.search(review).group(2))  # 파일 이름에서 index 추출.
            temp_hotel_urls = hotel_urls.loc[hotel_index]
            hotel_label = temp_hotel_urls['title']  # index를 통해 title 추출.

            hotel_label = re.sub('[\/:*?"<>|]', '', str(hotel_label))  # 특수문자 제거
            for index in range(0, len(src_review)):
                temp = src_review.loc[index]  # 리뷰 하나 불러오기

                if temp['lang'] == 'en':
                    tar_review.loc[index] = [temp['index'], temp['title'], temp['rating'], temp['content'],
                                             temp['lang']]
                elif len(temp['content']) > 500:
                    pass
                else:
                    try:
                        result = translator.translate(temp['content'], dest="en")
                        tar_review.loc[index] = [temp['index'], temp['title'], temp['rating'], result.text,
                                                 temp['lang']]
                    except:
                        pass

                tar_review.to_csv(r'.\translated_review\hotel_review_{}.csv'.format(hotel_label), encoding="UTF=8",
                                  index=False)
                print(review, '의 ', index, '번 째 번역 완료 !!')
#######################################################################################################################

############################################# 3. 인덱스 매칭 ############################################################
from googletrans import Translator
import pandas as pd
import os
import re

default_path = r"C:\Workspace\hotel"  # 경로
translator = Translator()  # 번역기 시작

os.chdir(default_path)  # C:\Workspace\tour_gosu\hotel
country_list = os.listdir()  # 국가 리스트 추출

# 순회
for country in country_list:
    os.chdir(country)  # C:\Workspace\tour_gosu\tour\country
    city_list = os.listdir()  # 도시 리스트 추출

    for city in city_list:
        os.chdir(city + "\\review")  # C:\Workspace\tour_gosu\tour\country\city\review

        # 저장할 폴더 생성
        try:
            os.makedirs("translated_review")
        except:
            pass

        # 리뷰 리스트 읽어온다.
        review_list = os.listdir()
        try:
            review_list.remove("translated_review")
        except:
            pass
        try:
            review_list.remove("debug.log")
        except:
            pass

        file_list = review_list
        regex = re.compile(r'(hr_)(\d*)(.csv)')
        hotel_urls = pd.read_csv(r'..\hotel_urls.csv', encoding="UTF-8")  # title을 읽어오기 위해 hotel_urls를 불러온다.

        for file in file_list:
            hotel_index = int(regex.search(file).group(2))
            hotel_label = hotel_urls.iloc[hotel_index]['title']

            hotel_label = re.sub('[\/:*?"<>|]', '', str(hotel_label))  # 특수문자 제거

            if os.path.isfile(
                    r'.\translated_review\hotel_review_{}.csv'.format(hotel_label)):  # (Flag 역할)음식점이름.csv가 존재하는 경우
                print(hotel_index, '. ', hotel_label, ' 을 이미 번역했으므로 Pass 합니다.')
                review_list.remove(file)

        for review in review_list:
            src_review = pd.read_csv(review, sep=",", encoding="UTF-8")
            tar_review = pd.DataFrame(columns=['index', 'title', 'rating', 'content', 'lang'])

            # index-label 매칭
            hotel_urls = pd.read_csv(r'..\hotel_urls.csv', encoding="UTF-8")  # title을 읽어오기 위해 hotel_urls를 불러온다.
            regex = re.compile(r'(hr_)(\d*)(.csv)')  # 정규 표현식
            hotel_index = int(regex.search(review).group(2))  # 파일 이름에서 index 추출.
            temp_hotel_urls = hotel_urls.loc[hotel_index]
            hotel_label = temp_hotel_urls['title']  # index를 통해 title 추출.

            hotel_label = re.sub('[\/:*?"<>|]', '', str(hotel_label))  # 특수문자 제거
            for index in range(0, len(src_review)):
                temp = src_review.loc[index]  # 리뷰 하나 불러오기

                if temp['lang'] == 'en':
                    tar_review.loc[index] = [temp['index'], temp['title'], temp['rating'], temp['content'],
                                             temp['lang']]
                else:
                    result = translator.translate(temp['content'], dest="en")
                    tar_review.loc[index] = [temp['index'], temp['title'], temp['rating'], result.text, temp['lang']]

                tar_review.to_csv(r'.\translated_review\hotel_review_{}.csv'.format(hotel_label), encoding="UTF=8",
                                  index=False)
                print(review, '의 ', index, '번 째 번역 완료 !!')

#######################################################################################################################

