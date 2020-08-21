import pandas as pd
import tensorflow as tf


def print_info():
    print(lemon.shape)
    print(boston.shape)
    print(iris.shape)

    print(lemon.columns)
    print(boston.columns)
    print(iris.columns)

    # head함수는 상위 5개 데이터 출력
    print(lemon.head())
    print(boston.head())
    print(iris.head())


if __name__=="__main__":
    path = 'https://raw.githubusercontent.com/blackdew/tensorflow1/master/csv/lemonade.csv'
    lemon = pd.read_csv(path)

    path = 'https://raw.githubusercontent.com/blackdew/tensorflow1/master/csv/boston.csv'
    boston = pd.read_csv(path)

    path = 'https://raw.githubusercontent.com/blackdew/tensorflow1/master/csv/iris.csv'
    iris = pd.read_csv(path)

    """# Input(shape=[1])
    independent = lemon[['온도']]
    dependent = lemon[['판매량']]
    print(independent.shape, dependent.shape)
    """
    # Input(shape=[13])
    independent = boston[['crim', 'zn', 'indus', 'chas', 'nox', 'rm', 'age', 'dis', 'rad', 'tax','ptratio', 'b', 'lstat']]
    dependent = boston[['medv']]
    print(independent.shape, dependent.shape)
   
    """
    independent = iris[['꽃잎길이', '꽃잎폭', '꽃받침길이', '꽃받침폭']]
    dependent = iris[['품종']]
    print(independent.shape, dependent.shape)
    """

    # 레모네이드 학습 모델
    X = tf.keras.layers.Input(shape=[13])   # 독립변수가 하나라서 shpae = [1] 씀
    Y = tf.keras.layers.Dense(1)(X)  # 종속변수가 하나라서 shape = [1] 씀
    model = tf.keras.models.Model(X,Y)
    model.compile(loss='mse')

    # 모델 학습
    model.fit(independent,dependent, epochs=1000 , verbose = 0)  # 전체 데이터를 몇번 반복하여 학습할지 정하는 변수 verbos=0은 출력을 안함

    print(model.predict(independent[0:5]))  # 예측값
    print(dependent[0:5])                   # 실제 값(정답)

    print(model.get_weights())  # 모델 가중치 확인