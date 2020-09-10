from bs4 import BeautifulSoup as bs
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import requests
import sys
import os
from urllib.request import urlopen

class NaverTop20Crawler(QWidget):   # QWidget 상속
    def __init__(self):
        super().__init__()
        self.initializeScreen()

    def initializeScreen(self):
        # 위젯들을 그리드 layout에 집어넣을 예정
        grid = QGridLayout()
        self.setLayout(grid)

        # 타이틀 텍스트 선언
        self.titleLabel = QLabel("Pyqt를 이용한 크롤링 연습")
        self.titleLabel.setAlignment(Qt.AlignCenter)    # 중앙으로 설정
        self.titleLabel.setFixedHeight(50)
        self.titleLabel.setFont(QFont("Ubuntu",pointSize=15,weight=QFont.Bold))

        self.startCrawlingBtn = QPushButton("크롤링 시작")
        self.startCrawlingBtn.clicked.connect(self.getTop20Keyword)     # 클릭시 getTop20keyword 함수와 연동

        # 데이터를 뿌려줄 ListView
        self.rankListView = NaverTop20RankListView()

        # 타이틀 및 화면 왼쪽에 있는 위젯들을 등록합니다.
        grid.addWidget(self.titleLabel,0,0)
        grid.addWidget(self.startCrawlingBtn,1,0)
        grid.addWidget(self.rankListView,2,0)

        self.setWindowTitle("네이버 실검 20위 크롤러")
        self.setFixedWidth(500)
        self.setFixedHeight(850)

        self.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.show()

    def getTop20Keyword(self):
        keywords = []
        res = requests.get("https://www.naver.com/srchrank?frm=main")

        if res.status_code == 200:  # response code 가 200 이면 정상이므로 데이터 세팅함
            json = res.json()
            ranks = json.get('data')
            print(ranks)
            for rank in ranks:
                keyword = rank['keyword']
                print(keyword)
                keywords.append(keyword)

            self.rankListView.setData(keywords)
        else:
            self.rankListView.setData(["데이터를 가져오는데 실패하였습니다."])
class NaverTop20RankListView(QWidget):
    def __init__(self):
        QWidget.__init__(self,flags=Qt.Widget)
        self.setFixedHeight(650)
        self.tableWidget = QTableWidget(self)

        # 대강 꽉차게 사이즈 맞춤
        self.tableWidget.resize(500,850)
        # 실검이 20위까지니까 가로 줄 20개 세팅
        self.tableWidget.setRowCount(20)
        self.tableWidget.setColumnCount(1)
        # 이걸 써야 한 셀이 한 행에 꽉참
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

    def setData(self,keywords):
        self.keywords = keywords

        for idx in range(20):
            # 테이블 위젯에 값을 세팅
            item = QTableWidgetItem()
            item.setText(keywords[idx])
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(idx,0,item)

        self.tableWidget.cellClicked.connect(self.onCellClicked)

    def onCellClicked(self,row,col):
        print("Selected Keyword : ",self.keywords[row])

class NaverImageCrawler(QWidget):
    def __init__(self):
        super().__init__()
        self.initializeScreen()

    def initializeScreen(self):
        # 위젯들을 그리드 layout에 집어넣을 예정
        grid = QGridLayout()
        self.setLayout(grid)

        # 타이틀 텍스트 선언
        self.titleLabel = QLabel("Pyqt를 이용한 크롤링 연습2")
        self.titleLabel.setAlignment(Qt.AlignCenter)  # 중앙으로 설정
        self.titleLabel.setFixedHeight(40)
        self.titleLabel.setFont(QFont("Ubuntu", pointSize=15, weight=QFont.Bold))

        # 검색어를 입력받을 LindEdit
        self.search_word = QLineEdit("",self)

        self.startCrawlingBtn = QPushButton("크롤링 시작")
        self.startCrawlingBtn.clicked.connect(self.getImages)  # 클릭시 getTop20keyword 함수와 연동

        # 데이터를 뿌려줄 ListView
        self.imageListView = ImageListView()

        # 타이틀 및 화면 왼쪽에 있는 위젯들을 등록합니다.
        grid.addWidget(self.titleLabel, 0, 0)
        grid.addWidget(self.search_word,1,0)
        grid.addWidget(self.startCrawlingBtn, 2, 0)
        grid.addWidget(self.imageListView, 3, 0)

        self.setWindowTitle("네이버 이미지 크롤러")
        self.setFixedWidth(580)
        self.setFixedHeight(600)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.show()

    def getImages(self):
        url = f"https://www.google.co.kr/search?q={self.search_word.text()}&newwindow=1&authuser=0&hl=ko&sxsrf=ALeKk01jmXwyM-wKk5oIFOkzcehtOVUUYA:1599720186027&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjm_bWL_t3rAhXJGaYKHcmMAdUQ_AUoAXoECBAQAw&biw=1765&bih=927"
        res = requests.get(url)

        if res.status_code == 200:
            soup = bs(res.text,'html.parser')
            elements = soup.select('img.t0fcAb')
            images = []
            n = 1
            print(elements)
            for element in elements:
                if n > 9:
                    break
                imageUrl = element['src']
                #images.append(imageUrl)

                # 경로가 없으면 경로생성
                if os.path.isdir('./images') == False:
                    os.makedirs('./images')

                with urlopen(imageUrl) as f:
                    with open('./images/img' + str(n) + '.jpg','wb') as h:
                        image = f.read()
                        images.append(image)
                        h.write(image)
                n += 1
            self.imageListView.setImage(images)
        else:
            self.imageListView.error("데이터를 가져오는데 실패하였습니다.")
class ImageListView(QWidget):
    def __init__(self):
        QWidget.__init__(self,flags=Qt.Widget)
        self.setFixedHeight(650)
        self.tableWidget = QTableWidget(self)
        # 대강 꽉차게 사이즈 맞춤
        self.tableWidget.resize(580,600)
        # 테이블 행 열 개수 설정
        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(3)
        # cell 크기 설정
        self.tableWidget.horizontalHeader().setDefaultSectionSize(180)
        self.tableWidget.verticalHeader().setDefaultSectionSize(140)

    def setImage(self,images):
        row = 0
        col = 0
        for image in images:
            item = self.getImageLabel(image)
            item.setAlignment(Qt.AlignCenter)
            self.tableWidget.setCellWidget(row,col,item)
            col += 1
            if col > 2 :
                col = 0
                row += 1

    def getImageLabel(self,image):
        imageLabel = QLabel()
        imageLabel.setText("")
        imageLabel.setScaledContents(False)
        pixMap = QPixmap()
        pixMap.loadFromData(image,'jpg')
        imageLabel.setPixmap(pixMap)
        return imageLabel

    def error(self,message):
        item = QTableWidgetItem()
        item.setText(message)
        item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(0,0,item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = NaverImageCrawler()
    #ex = NaverTop20Crawler()
    sys.exit(app.exec_())