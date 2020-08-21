from nltk import bigrams, word_tokenize
from nltk.util import ngrams
from tensorflow.keras.preprocessing.text import text_to_word_sequence,Tokenizer
from collections import Counter
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib import font_manager,rc
from konlpy.tag import Okt
import nltk
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
import pickle
from konlpy.tag import *

# 명사 생성
def get_noun(review):
    noun = okt.nouns(review)
    for i, v in enumerate(noun):
        if (len(v) < 2):    # 한글자 단어수는 제외함
            noun.pop(i)
    return noun

# wordcloud 생성
def generate_cloud(text):
    count = Counter(text)           # 추출된 타켓 텍스트를 카운트해줌
    noun_list = count.most_common(100)
   # words = dict(count.most_common())

    wc = WordCloud(font_path='C:/Windows/Fonts/malgun.ttf', background_color='white', colormap="Accent_r", width=1500,
                   height=1000)
    wc.generate(str(noun_list))
   # wc.to_file('noun_cloud.png')

    plt.figure(figsize=(22, 22))  # 이미지 사이즈 지정
    plt.imshow(wc, interpolation='lanczos')  # 이미지의 부드럽기 정도
    plt.axis('off')  # x y 축 숫자 제거
    plt.show()

#ngram 생성
def generate_ngram(review):
    tokens = text_to_word_sequence(review)  # 텐서플로우 토큰들을 생성   (좋게 토큰화 해준거같음)
    # tokens = word_tokenize(review) # nltk 토큰  (별로 인거같음)

    bigram = ngrams(tokens,2)  # ngram을 이용해 바이어그램 생성 및 저장됨 (pad_left=True, pad_right=True, left_pad_symbol="SS", right_pad_symbol="SE") 라는 인자도 가질수 있음
    return bigram

# ngram을 엑셀화 시킴
def ngram_excel(sentences):
    count = Counter(sentences)  # sentences 카운트

    tag_count = []
    tags = []

    for w, f in count.most_common(20):  # sentences 중에서 가장 빈도수가 높은것을 튜플 형태로 반환
        dics = {"word": w, "freq": f}
        if (len(dics['word']) >= 2 and len(tags) <= 49):  # (2글자 이상 49글자 미만)에 맞는 단어
            tag_count.append(dics)
            tags.append(dics['word'])

    # 액셀로 저장
    word_freq_data = pd.DataFrame(tag_count)
    word_freq_data.to_excel("wordData23.xlsx", index=False)

# 빈도수 별 단어 그래프 출력
def graph_words(text):
    text = nltk.Text(text, name='NMSC')
    font_fname = 'c:/windows/fonts/gulim.ttc'
    font_name = font_manager.FontProperties(fname=font_fname).get_name()
    rc('font', family=font_name)
    plt.figure(figsize=(20, 10))
    text.plot(50)

# 평점 전처리
def star_preprocessing(value):
    value = int(value)

    if(value <= 3):
        return '0'
    else :
        return '1'

# 형태소 분석을 위한 함수
def tokenizers(text) :
    okt = Okt()
    return okt.morphs(text)

# 학습데이터, 테스트데이터 분배
def step1_data_preprocessing(text_list,score_list):
    # 80%는 학습, 20%는 test
    text_train, text_test, score_train, score_test = train_test_split(text_list, score_list, test_size=0.2, random_state=0)
    return text_train, text_test, score_train, score_test

# 학습 및 모델 생성 후 저장하는 함수
def step2_learning(X_train, y_train, X_test, y_test):
    # 주어진 데이터를 단어 사전으로 만들고 각 단어의 빈도수를 계산한 후 벡터화 하는 객체 생성
    tfidf = TfidfVectorizer(lowercase=False, tokenizer=tokenizers)

    # 문장별 나오는 단어수 세서 수치화, 벡터화해서 학습을 시킨다.
    logistic = LogisticRegression(C=10.0, penalty='l2', random_state=0)

    pipe = Pipeline([('vect', tfidf), ('clf', logistic)])

    # 학습한다.
    pipe.fit(X_train, y_train)

    # 학습 정확도 측정
    y_pred = pipe.predict(X_test)
    print(accuracy_score(y_test, y_pred))

    # 학습된 모델을 저장한다.
    with open('pipe.dat', 'wb') as fp:
        pickle.dump(pipe, fp)

    print('저장완료')

def step3_using_model():
    # 객체를 복원한다.
    with open('pipe.dat', 'rb') as fp:
        pipe = pickle.load(fp)

    import numpy as np

    while True:
        text = input('리뷰를 작성해주세요 :')

        str = [text]
        # 예측 정확도
        r1 = np.max(pipe.predict_proba(str) * 100)
        # 예측 결과
        r2 = pipe.predict(str)[0]

        if r2 == '1':
            print('긍정적인 리뷰')
        else:
            print('부정적인 리뷰')

        print('정확도 : %.3f' % r1)


# 학습 함수
def learing(text_list,score_list):
    text_train, text_test, score_train, score_test = step1_data_preprocessing(text_list,score_list)
    step2_learning(text_train, score_train, text_test, score_test)

# 사용 함수
def using():
    step3_using_model()

if __name__=="__main__":
    Data = pd.read_excel("C:\\Users\\user\\Desktop\\MinHo\\Python\\concatData.xlsx", sheet_name= "Sheet1")

    Data['score'] = Data['score'].apply(star_preprocessing)
    text_list = Data['review'].tolist()
    score_list = Data['score'].tolist()

    # 컬럼 필터
    col_list = ['review']
    Data = Data[col_list]

    sentences = []
    text = []
    i =0

    okt = Okt()

    #learing(text_list,score_list)
    #using()
"""
    for review in Data['review']:
        if(i==1000):    # n개의 review 를 전처리 시킴
            break
        #text.append(get_noun(review))
        text += get_noun(review)     # 명사 추출

        #sentences += [t for t in generate_ngram(review)]  # ngram 추출
        #sentences += [t for t in bigram]   # bigram을 누적 저장
        i+=1

    
    #graph_words(text)
    #ngram_excel(sentences)
    #generate_cloud(sentences)
    #generate_cloud(text)
"""



