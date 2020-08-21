import requests

stdNo = "20161253" #아이디
passwd = "rkdalsgh9546!" #비밀번호
string = ""

Class_Header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Length': '79',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'dreams2.daejin.ac.kr',
    'Origin': 'http://dreams2.daejin.ac.kr',
    'Referer': 'http://dreams2.daejin.ac.kr/sugang/nsugang_direct2_new.jsp',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
}

data = {
    'dir': '1',
    'cmd': 'aply',
    'ic_sbjcd': '92700912', # 과목코드 + 분반
    'urltype': 'direct',
    'getsbjt_no': '927009', # 과목코드
    'getclss_no': '12' # 분반
}

with requests.Session() as s:
    login_req = s.post("http://dreams2.daejin.ac.kr/sugang/LoginB?user_flag=1&stdNo={}&passwd={}".format(stdNo,passwd))
    cookies = login_req.cookies.get_dict()
    for key,value in cookies.items():
        string = string + "{}={}; ".format(key,value)
    string = string + "viewCount=WSL_BBSDATA18275;"
    Class_Header['Cookie'] = string
    sugang = s.get('http://dreams2.daejin.ac.kr/enroll.html')
    test = s.post("http://dreams2.daejin.ac.kr/sugang/SugangWlsn0410",headers = Class_Header,data = data)