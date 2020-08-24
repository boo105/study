import pandas as pd
import matplotlib.pyplot as plt
from afinn import Afinn
import numpy as np
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier

def emolex(review):
    # NRC 사전은 긍정,부정 + 8가지 감성 총 10가지 척도에 대해 0또는 1로 라벨링 되어있다. 14,182개의 단어에 대해서 이므로 총 14만 1820개의 행으로 이루어져있음
    NRC = pd.read_csv("C:\\Users\\user\\Desktop\\MinHo\\Python\\College\\NRC-Emotion-Lexicon-Wordlevel-v0.92.txt",
                      engine="python", header=None, sep="\t")
    #NRC.head(20)

    # 필요한 단어들은 1로 라벨링 되어있는 것들이므로 DataFrame.all() 메서드를 통해 유의미한 라벨들만 추출한다. all() 파라미터로 0은 위아래로 탐색 1은 좌우로 탐색한다.
    NRC = NRC[(NRC != 0).all(1)]
    #NRC.head(10)

    # 추출 후 인덱스 번호 리셋(추출 하면 인덱스가 혼합되므로)
    NRC = NRC.reset_index(drop=True)
    #NRC.head(10)

    tokenizer = RegexpTokenizer('[\w]+')        # 정규표준화
    stop_words = stopwords.words('english')     # 영어에 대한 불용어
    p_stemmer = PorterStemmer()

    raw = review.lower()    # 소문자로 바꿈
    tokens = tokenizer.tokenize(raw)    # 토큰화
    stopped_tokens = [i for i in tokens if not i in stop_words]  # 불용어 제거
    match_words = [x for x in stopped_tokens if x in list(NRC[0])]  # 사전과 매칭

    emotion = []
    for i in match_words:
        temp = list(NRC.iloc[np.where(NRC[0] == i)[0], 1])       # 단어에 해당되는 감정들의 index들을 불러와 emotion들을 리스트형태로 저장
        for j in temp:
            emotion.append(j)

    sentiment_result1 = pd.Series(emotion).value_counts()   # emotion 값의 개수 반환

    plt.bar = sentiment_result1.plot.bar()
    plt.show()
    print(sentiment_result1, sentiment_result1.plot.bar())

def create_label():
    i= 0
    labels = []
    for review in Data['review']:
        print(i,"번째 라벨 생성")
        if Data['score'][i] <= 2: # 평점이 2점이하면 부정적
            labels.append("negative")
        elif afinn.score(review) > 2 :  # 평점이 3점일때 afinn.score 가 3점이상이면 긍정적
            labels.append("positive")
        else :
            labels.append("negative")
        i += 1

    Data['sentiment'] = labels
    Data.to_excel('review_english.xlsx', index=False)

if __name__ == "__main__":
    # 감성분석 순서
    # 1. 데이터 읽어오기(이미 전처리,가공 된 데이터 이어야함)
    # 2. afinn 사전 혹은 emolex 사전을 이용해 감성점수 를 계산함
    # 3. 모델 만들기 및 학습
    # 4. 예측
    # 주의사항 : 데이터 전처리 과정이 매우 중요하다는 사실을 깨달음 특히 라벨링 하는 부분

    Data = pd.read_excel("C:/Users/user/Desktop/MinHo/Python/College/review_english.xlsx", sheet_name= "Sheet1")
    afinn = Afinn()
#    emolex(Data['review'][3307])

    # 감성분석을 하기전 지도학습을 하기위한 라벨링을 추가해줘야함
    #create_label()

    # 모델 생성
    # x에는 feature(reivew)를 y에는 label을 설정하고 train_data와 test_data로 분류
    x = Data['review']
    y = Data['sentiment']
    x_train, x_test, y_train, y_test = train_test_split(x, y, stratify=y, test_size=0.2)

    print(x_train.shape, x_test.shape)  # 훈련세트, 테스트세트 비율 확인
    print(np.unique(y_train, return_counts=True)) # 훈련세트의 타깃(라벨) 확인

    stop_words = stopwords.words('english')
    # 불용어 제거후 TF-IDF 가중치를 이용해 리뷰에 해당하는 column을 문서-단어 매트릭스로 바꾼다.
    vect = TfidfVectorizer(stop_words=stop_words).fit(x_train)
    x_train_vectorized = vect.transform(x_train)

    #print(x_train_vectorized)

    # 로지스틱 회귀로 학습한 결과
    model = LogisticRegression()
    model.fit(x_train_vectorized, y_train)
    print(model.score(x_train_vectorized, y_train)) # 모델 정확도(train)
    print(model.score(vect.transform(x_test), y_test))  # 정확도(test)

    print(afinn.score("I can use this product everyday"))

    text = ["This smells is so bad", "I think this is not good", "1 month use fresh scent I thought...",
            "This is the best item for me", "So so", "I can use this product everyday"]
    predict = model.predict(vect.transform(text))
    print(predict)

    """
    from sklearn.tree import DecisionTreeClassifier
    # 의사결정나무로 학습
    clf = DecisionTreeClassifier()
    clf.fit(x_train_vectorized, y_train)
    print(clf.score(x_train_vectorized, y_train))
    print(clf.score(vect.transform(x_test), y_test))
    """