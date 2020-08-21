from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd

Data = pd.read_excel("C:\\Users\\user\\Desktop\\MinHo\\Python\\wordData.xlsx", sheet_name= "Sheet1")
wordcloud = WordCloud(font_path='/Library/Fonts/NanumBarunGothic.ttf', background_color='white').generate(Data)

print(Data)

plt.figure(figsize=(22,22)) #이미지 사이즈 지정
plt.imshow(wordcloud, interpolation='lanczos') #이미지의 부드럽기 정도
plt.axis('off') #x y 축 숫자 제거
plt.show()
plt.savefig()
