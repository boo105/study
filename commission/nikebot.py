import discord
from discord.ext import commands  # 본격적인 봇 생성을  위한 모듈
import asyncio
import os
import urllib
import requests
from urllib.request import Request, urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import pandas as pd
import time
import webbrowser

channel_id = 297698515415728128

# 토큰 값이 노출방지를 위해 파일을 따로둬서 관리함   github에 올릴 때도 token.txt는 ignore처리 하면 토큰값이 노출될일이없음
token_path = os.path.dirname(os.path.abspath(__file__)) + "\\token.txt"
t = open(token_path, "r", encoding="utf-8")
token = t.read().split()[0]
t.close()

# 봇의 설정
# 생성된 토큰을 입력해준다.
game = discord.Game("!help")  # 상태 메시지
# commands_prefix는 해당 구문이 맨앞에 있을떄 명령어로 인식한다는 뜻 (!도움,!안녕 등) status 는 봇의값의 상태(온라인,자리비움 등) activity는 상태말 임
bot = commands.Bot(command_prefix='!', status=discord.Status.online, activity=game, help_command=None)

# 유저인척 하는 헤더 정보 및 크롬드라이버 설정
header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
          'accept-encoding': 'gzip, deflate, br',
          'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
          'cache-control': 'max-age=0',
          }

# driver 세팅
options = webdriver.ChromeOptions()
options.add_argument('headless')  # 크롤링 동안 크롬창 없이 크롤링
options.add_argument("--log-level=3")  # 콘솔로그 제거
options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36')
driver = webdriver.Chrome("C:\\Users\\user\\Desktop\\MinHo\\GitHub\\study\\chromedriver.exe", options=options)

# 원하는 타겟 상품 리스트
shoes_list = []

# 크롬창에 띄어줄 사이트 목록
quicktask_list = []

async def nike_product():
    while True:
        # 타겟 상품이 하나라도 있을때
        if (len(shoes_list) > 0):
            print("크롤링 시작")
            for product in shoes_list:
                #driver = get_driver()
                #  html 긁어오기
                #print(product)
                driver = webdriver.Chrome("C:\\Users\\user\\Desktop\\MinHo\\GitHub\\study\\chromedriver.exe",options=options)
                driver.get(product['url'])  # url 접속
                time.sleep(1)   # 1초 지연  페이지로드 할때나 이동할때 (변화가 있을때) 넣는다
                html = driver.page_source
                
                # 원하는 부분 긁어오기
                soup = bs(html, 'html.parser')
                element = soup.select_one(f'span[typename={product["size"]}]')  # select가 find보다 속도도 빠르고 메모리도 적게 먹음
                #print(element)
                
                # 품절인지 아닌지 판정
                try:
                    if element.attrs['disabled'] != None:
                        print("품절")
                except:
                    # 채널 정보
                    channel = bot.get_channel(channel_id)
                    # embed 정보
                    msg = "Price :" + product['price'] + "\n" + product['url']
                    embed = discord.Embed(title="나이키 재고 정보", color=discord.Color.blue())
                    embed.add_field(name=f"{product['name']}", value=msg, inline=False)
                    await channel.send(embed=embed)
                driver.close()
        await asyncio.sleep(10)

# 봇이 구동되었을 때 보여지는 코드
@bot.event
async def on_ready():
    print(f"{bot.user}에 로그인하였습니다!")
    # 주기적으로 nike 타겟 사이트 모니터링
    bot.loop.create_task(nike_product())

@bot.command()
async def 도움(ctx,*,content):
    print("도움")

@bot.command()
async def 추가(ctx,*,content):
    # 매개변수는 신발이름 사이즈 로 들어옴
    message = content.split(" ")
    size = message[0]
    url = message[1]
    
    # 드라이버 설정
    #driver = get_driver()
    driver = webdriver.Chrome("C:\\Users\\user\\Desktop\\MinHo\\GitHub\\study\\chromedriver.exe", options=options)
    driver.get(url)
    
    # html 긁어오기
    html = driver.page_source
    soup = bs(html,'html.parser')
    element = soup.select_one(f'span[typename={size}]')
    print(element.attrs)
    # 품절인지 아닌지 판정
    try:
        if(element.attrs['disabled'] != None):
            # 품절된 상태
            name = soup.select('.info-wrap_product_n > h1 > span.tit')  # 신발 이름
            name = name[0]['data-name']
            price = soup.select_one('span.price > strong').text
            shoes_list.append({'name': name, 'size': size, 'price' : price ,'url': url})
            print(name + " 추가 완료\n")
            driver.close()
            await ctx.send("추가가 완료되었습니다!")
    except:
        print("이미 재고가 있습니다!")
        driver.close()
        await ctx.send("이미 재고가 있습니다!")

@bot.command()
async def 확인(ctx):
    i = 1
    message = ""
    for element in shoes_list:
        message += "**" + str(i) + "**. "
        message += "**이름** : " + element['name'] + " **\n    사이즈** : " + element['size'] + "\n"  # + element['url'] +"\n"
        i += 1
    await ctx.send(message)

@bot.command()
async def quicktask(ctx,content):
    url = content.split(" ")[0]
    quicktask_list.append(url)
    ctx.send("추가가 완료되었습니다.")

@bot.command()
async def 목록(ctx):
    i = 1
    msg = ""
    for e in quicktask_list:
        msg += "**" + str(i) + "**. "
        msg += e + "\n"
        i += 1

    for e in quicktask_list:
        webbrowser.open_new(e)

    embed = discord.Embed(title="나이키", color=discord.Color.blue())
    embed.add_field(name="QuickTask",value=msg,inline=False)
    #embed.add_field(name=f"quicktask", url= "https://www.naver.com/", inline=False)
    await ctx.send(embed=embed)

# run함수는 on_ready 랑 bot.command 이후에 실행이 되어야함
bot.run(token)  # 해당 토큰을 가진 봇을 실행
