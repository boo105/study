import discord
from discord.ext import commands
import asyncio
import os
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import pandas as pd
import time
import webbrowser
from threading import Thread

# 채널 ID
channel_path = os.path.dirname(os.path.abspath(__file__)) + "\\channel_id.txt"
f = open(channel_path,"r",encoding="utf-8")
channel_id = int(f.read().split()[0])
f.close()

# 토큰 값이 노출방지를 위해 파일을 따로둬서 관리함   github에 올릴 때도 token.txt는 ignore처리 하면 토큰값이 노출될일이없음
token_path = os.path.dirname(os.path.abspath(__file__)) + "\\token.txt"
t = open(token_path, "r", encoding="utf-8")
token = t.read().split()[0]
t.close()

# 봇의 설정
game = discord.Game("!도움")  # 상태 메시지
# commands_prefix는 해당 구문이 맨앞에 있을떄 명령어로 인식한다는 뜻 (!도움,!안녕 등) status 는 봇의값의 상태(온라인,자리비움 등) activity는 상태말 임
bot = commands.Bot(command_prefix='!', status=discord.Status.online, activity=game, help_command=None)

# 유저인척 하는 헤더 정보 및 크롬드라이버 설정
header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    }

# driver 세팅
options = webdriver.ChromeOptions()
options.add_argument('headless')  # 크롤링 동안 크롬창 없이 크롤링
options.add_argument("--log-level=3")  # 콘솔로그 제거
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36')

# 원하는 타겟 상품 리스트
shoes_list = []

# 크롬창에 띄어줄 사이트 목록
quicktask_list = []

message_alarm_id = []   # 재고 알람 메세지

message_view_id = []    # 목록 확인 메세지

message_id = []     # 일반 알림 메세지

test_path = 'C:/Program Files (x86)/Naver/Naver Whale/Application/whale.exe --new-window %s'

async def nike_product():
    while True:
        # 타겟 상품이 하나라도 있을때
        if (len(shoes_list) > 0):
            print("크롤링 시작")
            i = 0
            for product in shoes_list:
                # html 긁어오기
                # print(product)
                driver = webdriver.Chrome("./chromedriver.exe", options=options)
                driver.get(product['url'])  # url 접속

                time.sleep(2)  # 1초 지연  페이지로드 할때나 이동할때 (변화가 있을때) 넣는다
                html = driver.page_source

                # 원하는 부분 긁어오기
                soup = bs(html, 'html.parser')
                element = soup.select_one(f'span[typename={product["size"]}]')  # select가 find보다 속도도 빠르고 메모리도 적게 먹음
                #print(element.attrs)
                # 품절인지 아닌지 판정
                try:
                    if element.attrs['disabled'] != None:
                        print(product['name'] + " 품절")
                except:
                    print(product['name'] + " 재고가 들어왔습니다.")
                    shoes_list[i]['status'] = 'stock'
                    # 채널 정보
                    channel = bot.get_channel(channel_id)
                    # embed 정보
                    msg = "Price :" + product['price'] + "\n" + product['url']
                    embed = discord.Embed(title="나이키 재고가 들어왔습니다!", color=discord.Color.blue())
                    embed.add_field(name=f"{product['name']}", value=msg, inline=False)

                    if len(message_alarm_id) > 0:  # 이전에 showlist를 메세지를 띄운경우 그 메세지를 삭제
                        message = await channel.fetch_message(message_alarm_id[0])
                        await message.delete()
                        message_alarm_id.clear()
                    message = await channel.send(embed=embed)
                    message_alarm_id.append(message.id)  # 메세지 id정보 저장
                i += 1
                driver.close()
        await asyncio.sleep(5)

# 봇이 구동되었을 때 보여지는 코드
@bot.event
async def on_ready():
    print(f"{bot.user}에 로그인하였습니다!")

    if os.path.isfile("./shoes_list.xlsx") == False:
        Data = {'name': [], 'size': [], 'price': [], 'url' :[], 'status' : []}
        Data = pd.DataFrame(Data)
        Data.to_excel("shoes_list.xlsx")
    else:
        file = pd.read_excel("./shoes_list.xlsx")
        for shoes in file.to_dict('records'):
            shoes_list.append(shoes)
        print("shoes_list 불러오기 완료")

    if os.path.isfile("./quicktask_list.xlsx") == False:
        Data = {'name': [], 'url' :[]}
        Data = pd.DataFrame(Data)
        Data.to_excel("quicktask_list.xlsx")
    else:
        file = pd.read_excel("./quicktask_list.xlsx")
        for task in file.to_dict('records'):
            quicktask_list.append(task)
        print("quicktask_list 불러오기 완료")

    # 주기적으로 nike 타겟 사이트 모니터링
    bot.loop.create_task(nike_product())

@bot.command()
async def 도움(ctx):
    msg = "!추가 (주소)\n!상품확인\n!상품제거 (원하시는상품번호)\n!알람확인 (창개수)\n!quicktask (주소)\n!사이트목록\n!제거 (원하시는사이트번호)\n!열기 all  또는 !열기 (원하시는사이트번호) (창개수)"
    # embed를 이용해 썸네일,이미지,영상도 추가 가능!
    embed = discord.Embed(title=f"명령어 양식", color=discord.Color.blue())
    embed.add_field(name=f"----명령어----", value=msg, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def 추가(ctx, *, content):
    # 매개변수는 신발이름 사이즈 로 들어옴
    try:
        message = content.split(" ")
        size = message[0]
        url = message[1]
    except IndexError:
        await ctx.send("입력양식을 확인해 다시 입력해주세요!")
        return

    msg = await ctx.send("--- 추가중 ---")

    # 드라이버 설정
    driver = webdriver.Chrome("./chromedriver.exe", options=options)
    driver.get(url)
    time.sleep(2)

    # html 긁어오기
    html = driver.page_source
    soup = bs(html, 'html.parser')
    element = soup.select_one(f'span[typename={size}]')
    #print(element.attrs)

    # 품절인지 아닌지 판정
    try:
        if (element.attrs['disabled'] != None):
            # 품절된 상태
            name = soup.select('.info-wrap_product_n > h1 > span.tit')  # 신발 이름
            name = name[0]['data-name']
            price = soup.select_one('span.price > strong').text
            shoes_list.append({'name': name, 'size': size, 'price': price, 'url': url,'status': 'out'})
            print(name + " 추가 완료\n")
            driver.close()
            # 파일 저장
            Data = pd.DataFrame(shoes_list)
            Data.to_excel("shoes_list.xlsx",index=False)

            if len(message_id) > 0:  # 이전에 showlist를 메세지를 띄운경우 그 메세지를 삭제
                message = await ctx.fetch_message(message_id[0])
                await message.delete()
                message_id.clear()

            message_id.append(msg.id)
            content = "추가가 완료되었습니다!"
            await msg.edit(content=content)

    except:
        driver.close()
        if len(message_id) > 0:  # 이전에 showlist를 메세지를 띄운경우 그 메세지를 삭제
            message = await ctx.fetch_message(message_id[0])
            await message.delete()
            message_id.clear()

        message_id.append(msg.id)
        content = "이미 재고가 있습니다!"
        await msg.edit(content=content)

@bot.command()
async def 상품확인(ctx):
    i = 1
    message = ""

    if len(message_view_id) > 0:  # 이전에 showlist를 메세지를 띄운경우 그 메세지를 삭제
        msg = await ctx.fetch_message(message_view_id[0])
        await msg.delete()
        message_view_id.clear()

    if len(shoes_list) > 0 :
        for element in shoes_list:
            message += "**" + str(i) + "**. "
            message += "**이름** : " + element['name'] + " **\n    사이즈** : " + str(element['size']) + "\n"  # + element['url'] +"\n"
            i += 1

        msg = await ctx.send(message)
        message_view_id.append(msg.id)
    else:
        msg = await ctx.send("상품이 없습니다.")
        message_view_id.append(msg.id)

@bot.command()
async def 상품제거(ctx, content):
    pick = content.split(" ")[0]
    try:
        del shoes_list[int(pick) - 1]
        # 파일 저장
        Data = pd.DataFrame(shoes_list)
        Data.to_excel("shoes_list.xlsx", index=False)
        await ctx.send("선택한 상품이 제거가 되었습니다.")
    except:
        await ctx.send("선택한 상품이 없습니다. 다시 입력해주세요!")

@bot.command()
async def 알람확인(ctx,content):
    count = content.split(" ")[0]

    i = 0
    for product in shoes_list:
        if product['status'] == 'stock':
            for _ in range(int(count)):
                #wb = webbrowser.get('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe --new-window %s')
                wb = webbrowser.get(test_path)
                wb.open(product['url'], 2)
            del shoes_list[i]
            Data = pd.DataFrame(shoes_list)
            Data.to_excel("shoes_list.xlsx", index=False)
            print("알람 중지")
        i += 1

@bot.command()
async def quicktask(ctx, content):
    url = content.split(" ")[0]

    msg = await ctx.send("--- 추가중 ---")

    # 이름 설정
    req = requests.get(url, headers=header)
    soup = bs(req.content, 'html.parser')
    name = soup.select('.info-wrap_product_n > h1 > span.tit')  # 신발 이름
    name = name[0]['data-name']
    quicktask_list.append({'name': name, 'url': url})

    # 파일 저장
    Data = pd.DataFrame(quicktask_list)
    Data.to_excel("quicktask_list.xlsx", index=False)

    if len(message_id) > 0:  # 이전에 showlist를 메세지를 띄운경우 그 메세지를 삭제
        message = await ctx.fetch_message(message_id[0])
        await message.delete()
        message_id.clear()

    message_id.append(msg.id)  # 메세지 id정보 저장
    content = "추가가 완료되었습니다!"
    await msg.edit(content=content)

@bot.command()
async def 사이트목록(ctx):
    i = 1
    msg = ""

    if len(message_view_id) > 0:  # 이전에 showlist를 메세지를 띄운경우 그 메세지를 삭제
        message = await ctx.fetch_message(message_view_id[0])
        await message.delete()
        message_view_id.clear()

    if (len(quicktask_list) > 0):
        for e in quicktask_list:
            msg += "**" + str(i) + "**. "
            msg += e['name'] + "\n"
            i += 1
        embed = discord.Embed(title="나이키", color=discord.Color.blue())
        embed.add_field(name="QuickTask", value=msg, inline=False)

        message = await ctx.send(embed=embed)
        message_view_id.append(message.id)
    else:
        message = await ctx.send("quicktask가 없습니다.")
        message_view_id.append(message.id)

@bot.command()
async def 제거(ctx, content):
    pick = content.split(" ")[0]
    try:
        del quicktask_list[int(pick) - 1]
        # 파일 저장
        Data = pd.DataFrame(quicktask_list)
        Data.to_excel("quicktask_list.xlsx", index=False)
        await ctx.send("선택한 사이트가 제거가 되었습니다.")
    except:
        await ctx.send("선택한 상품이 없습니다. 다시 입력해주세요!")

@bot.command()
async def 열기(ctx,*,content):
    msg = content.split(" ")
    if len(msg) > 1:
        pick = msg[0]
        count = msg[1]
        try:
            for _ in range(0, int(count)):
                wb = webbrowser.get('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe --new-window %s')
                wb.open(quicktask_list[int(pick) - 1]['url'], 1)
        except IndexError:
            await ctx.send("선택한 사이트가 없습니다!")
    else:
        for e in quicktask_list:
            wb = webbrowser.get('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe --new-window %s')
            wb.open(e['url'], 2)

# run함수는 on_ready 랑 bot.command 이후에 실행이 되어야함
bot.run(token)  # 해당 토큰을 가진 봇을 실행