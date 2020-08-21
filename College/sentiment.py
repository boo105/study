import codecs
import pandas as pd
import re
from konlpy.tag import Okt
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Embedding,Dense, LSTM
from keras_preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
import matplotlib.pyplot as plt
import numpy as np

def create_dictionary():
    pos = codecs.open("./pos_pol_word.txt", 'rb', encoding='UTF-8')
    while True:
        line = pos.readline()       # line 마다 읽어들임
        line = line.replace('\n', '')   # 끝부분을 \n으로 끝나게 해서 구분 할수 있게함
        positive.append(line)
        posneg.append(line)
        if not line: break
    pos.close()

    neg = codecs.open("./neg_pol_word.txt", 'rb', encoding='UTF-8')
    while True:
        line = neg.readline()       # line 마다 읽어들임
        line = line.replace('\n', '')   # 끝부분을 \n으로 끝나게 해서 구분 할수 있게함
        negative.append(line)
        posneg.append(line)
        if not line: break
    neg.close()

def create_label(reviews):
    j=0

    for review in reviews:
        re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…\"\“》]', '', review)    # 특수 기호 제거
        my_review_dic['review'].append(review)      # 딕셔너리에 review 추가

        for i in range(len(posneg)):
            posflag = False
            negflag = False
         #   if i < (len(positive)-1):
            if review.find(posneg[i]) != -1:    # 긍정어를 찾으면
                posflag = True
              #  print(i, "positive?", "테스트 : ", review.find(posneg[i]), "비교단어 : ", posneg[i], "인덱스 : ", i, review)
                break
     #       if i > (len(positive)-2):
            if review.find(posneg[i]) != -1:    # 부정어를 찾으면
                negflag = True
           #     print(i, "negative?", "테스트 : ", review.find(posneg[i]), "비교단어 : ", posneg[i], "인덱스 : ", i, review)
                break

        if posflag == True:
            label[j] = 1
        elif negflag == True:
            label[j] = -1
        else:
            label[j] = 0

        j += 1

    my_review_dic['label'] = label
    return pd.DataFrame(my_review_dic)

def show_plot():
    plt.hist([len(s) for s in X_train], bins=50)
    plt.title("X_train")
    plt.xlabel("length of Data")
    plt.ylabel("number of Data")
    plt.show()

    plt.hist([len(s) for s in X_test], bins=50)
    plt.title("X_test")
    plt.xlabel("length of Data")
    plt.ylabel("number of Data")
    plt.show()


if __name__ == "__main__":

    positive = []  # 긍정 텍스트
    negative = []  # 부정 텍스트
    posneg = []  # 긍부정 텍스트

    Data = pd.read_excel("C:\\Users\\user\\Desktop\\MinHo\\Python\\concatData.xlsx", sheet_name="Sheet1")   # reviews 읽어들이기

    col_list = ['review']
    Data = Data[col_list]

    label = [0] * 6000
    my_review_dic = {"review" : [], "label" : label}    # train data

    create_dictionary() # 긍정 부정 텍스트 읽은 후 생성
    my_review_df = create_label(Data['review'])  #  긍정 부정 라벨 생성(분류)
    
    stopwords = ['의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '도', '를', '으로', '자', '에', '와', '한', '하다']
    okt = Okt()     # 토큰화는 Okt형태소 분석기를 사용함

    X= []

    for review in my_review_df['review']:
        temp_X = []
        temp_X = okt.morphs(review, stem=True)  # 토큰화
        temp_X = [word for word in temp_X if not word in stopwords]     # 불용어 제거
        X.append(temp_X)

    X_train , X_test = train_test_split(X,test_size=0.2, random_state=123)

    # 정수인코딩 (토큰화 된 단어를 컴퓨터가 인식할 수 있도록)
    max_words = 35000
    tokenizer = Tokenizer(num_words= max_words)
    tokenizer.fit_on_texts(X_train)
    X_train = tokenizer.texts_to_sequences(X_train)
    X_test = tokenizer.texts_to_sequences(X_test)

    Y = []

    # 원핫인코딩 (컴퓨터가 보고 알수 있도록)
    for i in range(len(my_review_df['label'])):
        if my_review_df['label'].iloc[i] == 1:
            Y.append([0,0,1])     # 긍정 중립 부정
        elif my_review_df['label'].iloc[i] == 0:
            Y.append([0, 1, 0])
        elif my_review_df['label'].iloc[i] == -1:
            Y.append([1, 0, 0])

    Y_train , Y_test = train_test_split(Y, test_size=0.2, random_state=123)

    Y_train = np.array(Y_train)
    Y_test = np.array(Y_test)


    # 전체 데이터 길이를 max_len 으로 맞춰줌
    max_len = 100
    X_train = pad_sequences(X_train, maxlen= max_len)
    X_test = pad_sequences(X_test, maxlen=max_len)

    # 긍정, 부정, 중립 3가지로 분류해야하니 LSTM, softmax, categorical_crossentropy를 사용하였습니다.
    model = Sequential()
    model.add(Embedding(max_words,100))
    model.add(LSTM(128))
    model.add(Dense(3,activation="softmax"))

    model.compile(optimizer="rmsprop", loss= "categorical_crossentropy", metrics=['accuracy'])
    history = model.fit(X_train,Y_train, epochs=5, batch_size=10, validation_split=0.2, verbose=0)

   # print("테스트 정확도 : {:.2f}%".format(model.evaluate(X_test,Y_test)[1]*100))

    test_review = "완전 향이 안좋고 되게 별로였어요 돈만 날린듯..."
    test_X = []
    test_X = okt.morphs(test_review, stem=True)
    test_X = [word for word in test_X if not word in stopwords]
    test_X = tokenizer.texts_to_sequences(test_X)
    test_X = pad_sequences(test_X, maxlen=max_len)

    predict = model.predict(test_X)
    predict_labels = np.argmax(predict,axis =1)

    print("리뷰 : ",test_review,"/\t 예측한 라벨 : ",predict_labels)


"""
    # 예측
    predict = model.predict(X_test)

    predict_labels = np.argmax(predict, axis=1)
    original_labels = np.argmax(Y_test, axis=1)

    for i in range(30):
        print("리뷰 : ", my_review_df['review'].iloc[i], "/\t 원래 라벨 : ", original_labels[i], "/\t예측한 라벨 : ", predict_labels[i])
"""


