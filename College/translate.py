import pandas as pd
from googletrans import Translator


def extration_english():
    translator = Translator()

    X = {
        'review': [],
        'score': []
    }

    i = 0
    j = 1
    for review in Data['review']:
        if translator.detect(review).lang == 'en':
            print(j," 번쨰 추출")
            X['review'].append(review)
            X['score'].append(Data['score'][i])
            j += 1

        i += 1

    X = pd.DataFrame(X)
    X.to_excel('review_english.xlsx', index=False)

def translate(Review):
    translator = Translator()

    i = 1
    # 번역한 review 기록
    for review in Data['review']:
        # 해당 review가 번역되지 않았으면 번역함
        if translator.detect(review).lang == 'ko':
            print(i, " 번째 번역")
            trans_review = translator.translate(review, dest="en").text
            Review['review'].append(trans_review)
            i += 1
        else:  # 번역이 되있는 상태면 그냥 추가해줌
            Review['review'].append(review)

    Review['score'] = Data['score']

    # 엑셀로 저장
    Review = pd.DataFrame(Review)
    Review.to_excel('trans_review2.xlsx', index=False)


if __name__ == "__main__":

    Review = {
        'review' : [],
        'score' : []
    }

    # 번역할 데이터 읽어오기
    Data = pd.read_excel("C:\\Users\\user\\Desktop\\MinHo\\Python\\College\\trans_review2.xlsx", sheet_name= "Sheet1")
    """""
    col_list = ['review','score']
    Data = Data[col_list]
    """

    extration_english()

    """
    i=1
    # 번역한 review 기록
    for review in Data['review']:
        print(i," 번째 번역")
        trans_review = translator.translate(review, dest = "en").text
        Review['review'].append(trans_review)
        i += 1
    
    # score 기록
    for score in Data['score']:
        Review['score'].append(score)
    
    # 엑셀로 저장
    Review = pd.DataFrame(Review)
    Review.to_excel('trans_review.xlsx',index= False)
    """