import pandas as pd

Data1 = pd.read_excel("C:\\Users\\user\\Desktop\\MinHo\\Python\\pythoncide.xlsx", sheet_name= "Sheet1")
Data2 = pd.read_excel("C:\\Users\\user\\Desktop\\MinHo\\크롤링 및 텍스트 마이닝\\테스트용 데이터셋\\순수백과 피톤치드.xlsx", sheet_name= "review")
Data3 = pd.read_excel("C:\\Users\\user\\Desktop\\MinHo\\크롤링 및 텍스트 마이닝\\테스트용 데이터셋\\피톤치드 원액.xlsx", sheet_name= "review")

# 컬럼 필터
col_list = [ 'userid',   'date' ,  'option',  'review', 'score']

# 불필요한 인덱스 제거
Data2 = Data2[col_list]
Data3 = Data3[col_list]

concat_data = pd.concat([Data1,Data2])    # concat 함수는 데이터를 위아래로 연결함
final_data = pd.concat([concat_data,Data3])

final_data.to_excel("concatData.xlsx",index=False)