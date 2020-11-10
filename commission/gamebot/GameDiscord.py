import discord
from discord.ext import commands  # 본격적인 봇 생성을  위한 모듈
from discord import FFmpegPCMAudio
from youtube_search import YoutubeSearch
import asyncio
import os
import re
from youtube_dl import YoutubeDL
import youtube_dl
import ffmpeg
import pandas as pd
import datetime
from random import *

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

# 노래 재생을 위한 변수들
que = {}  # 재생목록 대기열
showlist = []  # 노래 제목과 시간을 표시할 list
urllist = []  # url을 저장할 listz
que_list = []   # 재생목록
message_id = []  # bot이 메세지의 id 정보를 가지고있음
volume = 0.4

# 쿨타임 리스트
cooltime_list = []
market_cooltime = None

def check_db(ctx):
    if os.path.isfile(str(ctx.message.guild) + " user.xlsx") == False:
        print(os.path.abspath(__file__))
        Data = {'id': [], 'money': []}
        Data = pd.DataFrame(Data)
        Data.to_excel(str(ctx.message.guild) + " user.xlsx")

def save_file(id,money,file_name):
    total_data = {}
    total_data['id'] = id
    total_data['money'] = money
    total_data = pd.DataFrame(total_data)
    #print(total_data)
    total_data.to_excel(file_name, index=False)

def cooltime(ctx):
    for cooltime in cooltime_list:
        if cooltime['id'] == ctx.message.author.id:
            # 쿨타임 계산
            cost_time = datetime.datetime.now() - cooltime['start_time']
            left_time = 60 - (cost_time.seconds // 60)
            # 쿨타임이 다 되면
            if left_time <= 0:
                cooltime_list.remove(cooltime)
                print(cooltime_list)
                return ""
            msg = str(ctx.message.author.mention) + f", 쿨타임중입니다.\n`{left_time}`분 후에 사용가능합니다."
            return msg
    return ""

def change_market():
    # 아이템 DB 읽기
    file = pd.read_excel("아이템.xlsx")
    name_list = file['name'].tolist()
    price_list = file['price'].tolist()
    fluctuation_list = file['fluctuation'].tolist()
    status_list = file['status'].tolist()

    i=0
    for name in name_list:

        # 아이템 가격이 0이하면 1이상이 될떄까지 다시 돌림
        while True:
            change = randrange(-20, 20)
            preview_price = price_list[i] + change
            if preview_price > 0:
                break
        # 상태 저장
        if change >0:
            status_list[i] = "+"
            fluctuation_list[i] = "▲ " + str(change)
        elif change <0:
            status_list[i] = "-"
            fluctuation_list[i] = "▼ " + str(abs(change))
        else:
            status_list[i] = "~"
            fluctuation_list[i] = "~ 0"
        # 가격 변경
        price_list[i] = preview_price
        i += 1
    # 저장
    total_data = {}
    total_data['name'] = name_list
    total_data['price'] = price_list
    total_data['fluctuation'] = fluctuation_list
    total_data['status'] = status_list
    total_data = pd.DataFrame(total_data)
    total_data.to_excel("아이템.xlsx", index=False)

def test_create():
    Data = {'name': [], 'price': [],'fluctuation' : [] ,'status': []}
    Data['name'].append("대리코인")
    Data['name'].append("소주")
    Data['name'].append("후드티")
    Data['name'].append("침대")
    Data['name'].append("호두")
    Data['name'].append("도라에몽")

    Data['price'].append(30)
    Data['price'].append(30)
    Data['price'].append(30)
    Data['price'].append(30)
    Data['price'].append(30)
    Data['price'].append(30)

    Data['fluctuation'].append("~ 0")
    Data['fluctuation'].append("~ 0")
    Data['fluctuation'].append("~ 0")
    Data['fluctuation'].append("~ 0")
    Data['fluctuation'].append("~ 0")
    Data['fluctuation'].append("~ 0")

    Data['status'].append("~")
    Data['status'].append("~")
    Data['status'].append("~")
    Data['status'].append("~")
    Data['status'].append("~")
    Data['status'].append("~")

    Data = pd.DataFrame(Data)
    Data.to_excel("아이템.xlsx",index=False)

def search_youtube(msg):
    print("search 시작!")
    search = YoutubeSearch(msg, max_results=10).to_dict()  # youtube 검색 api
    count = 1
    i = 0
    # 생방송이거나 그런건 거름
    while(True):
        if count == 6:
            break
        if search[i]['duration'] == 0:
            print("wtf..")
            i += 1
            continue
        text = search[i]['title']
        text += " (" + str(search[i]['duration']) + ")"
        showlist.append(text)
        url = "https://www.youtube.com/" + search[i]['url_suffix']
        urllist.append(url)

        count += 1
        i += 1

    print("search 종료!")

# !quit 명령어를 실행 하면 오류뜸
def queue(id, voice_client, options):  # 음악 재생용 큐
    if len(que_list) > 0:
        que_list.pop(0)
    print("queue 함수 들어옴")
    try:
        if que[id] != []:
            print("봇 대기열 재생목록 재생중")
            player = que[id].pop(0)
            voice_client.play(FFmpegPCMAudio(player['formats'][0]['url'], **options),after=lambda e: queue(id, voice_client, options))  # 노래 재생
            voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
            voice_client.source.volume = volume
        else:
            print("다음 재생 목록 없음")
    except Exception as e:  # 에러 발생시
        print(e)

@bot.command()
async def kick(ctx,member : discord.Member,*,reason = None):
    await member.kick(reason=reason)
    await ctx.send("{}님이 강퇴당하였습니다.".format(member))
@bot.command()
async def ban(ctx,member : discord.Member,*,reason = None):
    await member.ban(reason = reason)
    await ctx.send("{}님이 밴당하였습니다.".format(member.mention))

# 봇이 구동되었을 때 보여지는 코드
@bot.event
async def on_ready():
    global market_cooltime
    market_cooltime = datetime.datetime.now()
    if os.path.isfile("아이템.xlsx") == False:
        test_create()

    print(f"{bot.user}에 로그인하였습니다!")

@bot.command()
async def 돈받기(ctx):
    # 쿨타임 체크
    msg = cooltime(ctx)
    if msg != "" :
        await ctx.send(msg)
        return 0

    # DB 존재 유무 체크
    check_db(ctx)
    # DB 읽기
    file_name = str(ctx.message.guild) + " user.xlsx"
    file = pd.read_excel(file_name)
    id_list = file['id'].tolist()
    id_list = list(map(str, id_list))  # 저장할때 문자열로 해도 읽어올때 int 형으로 읽어와서 원소들을 문자열로 바꿔줘야함
    money_list = file['money'].tolist()

    # id_list 에 본인 id가 없으면 새로 생성함
    if (str(ctx.message.author.id) in id_list) == False:
        id_list.append(str(ctx.message.author.id))
        money_list.append(0)
        save_file(id_list, money_list,file_name)
    i = 0
    for id in id_list:
        if str(id) == str(ctx.message.author.id):
            money_list[i] += 100
            save_file(id_list,money_list,file_name)
            break
        i += 1
    msg = str(ctx.message.author.mention) + f", 당신의 잔고에 `{100}`원을 추가하였습니다!\n잔고:`{money_list[i]}`원"
    cooltime_list.append({"id" : ctx.message.author.id, "start_time" : datetime.datetime.now()})
    await ctx.send(msg)
    #print(cooltime_list)

@bot.command()
async def 시세(ctx):
    # 시간 초기화
    global market_cooltime
    cost_time = datetime.datetime.now() - market_cooltime
    set_time = 150

    # 명령어를 쳤을때 지난 시간이 set_time보다 같거나 클때 시세변동 및
    # market_cooltime 초기화 및 cost_time 초기화
    if cost_time.seconds >= set_time:
        change_market()
        second = (cost_time.seconds - set_time) % set_time
        market_cooltime = datetime.datetime.now() - datetime.timedelta(seconds=second)
        cost_time = datetime.datetime.now() - market_cooltime

    title = "```css\n[ 아이템 시세 ]```\n"

    # 아이템 DB 불러오기
    file = pd.read_excel("아이템.xlsx")

    # 메세지 내용 작성
    content ="```diff\n"
    i = 0
    for name in file['name']:
        content += f"{file['status'][i]} " + name + " : " + str(file['price'][i]) + "원 " + f"[{file['fluctuation'][i]}]\n"
        i += 1
    time_content = f"다음 변동: `{str(set_time - cost_time.seconds)}`초 남음"
    # 메세지 전송
    msg = title + content +"```" + time_content
    await ctx.send(msg)

@bot.command()
async def 구매(ctx,*,content):
    content = content.split(" ")
    if len(content) != 2:
        await ctx.send("입력을 잘못했습니다. 도움말을 참조해주세요!")
        return 0
    item = content[0]
    ea = content[1]

    if ea == "올인":
        # 아이템 DB 불러오기
        item_file = pd.read_excel("아이템.xlsx")
        user_file = pd.read_excel(str(ctx.message.guild) + " user.xlsx")
        id_list = user_file['id'].tolist()
        id_list = list(map(str, id_list))  # 저장할때 문자열로 해도 읽어올때 int 형으로 읽어와서 원소들을 문자열로 바꿔줘야함
        money_list = user_file['money'].tolist()

        # Item 정보 찾기
        i = 0
        for name in item_file['name']:
            if name == item:
                # 총 가격
                item_price = item_file['price'][i]
                break
            i += 1

        # user 찾기 및 결제
        i = 0
        for id in id_list:
            if id == str(ctx.message.author.id):
                ea = int(money_list[i] / item_price)
                total_cost = ea * item_price
                if ea == 0:
                    await ctx.send(str(ctx.message.author.mention) + ",지불하실 금액을 소지하고 있지 않습니다.")
                    return 0
                else:
                    money_list[i] -= total_cost
                break
            i += 1
    # 수량을 적었을때
    else:
        # 아이템 DB 불러오기
        item_file = pd.read_excel("아이템.xlsx")
        user_file = pd.read_excel(str(ctx.message.guild) + " user.xlsx")
        id_list = user_file['id'].tolist()
        id_list = list(map(str, id_list))  # 저장할때 문자열로 해도 읽어올때 int 형으로 읽어와서 원소들을 문자열로 바꿔줘야함
        money_list = user_file['money'].tolist()

        # Item 정보 찾기
        i = 0
        for name in item_file['name']:
            if name == item:
                # 총 가격
                total_cost = item_file['price'][i] * int(ea)
                break
            i += 1


        # user 찾기 및 결제
        i = 0
        for id in id_list:
            if id == str(ctx.message.author.id):
                if total_cost > money_list[i]:
                    await ctx.send(str(ctx.message.author.mention) + ",지불하실 금액을 소지하고 있지 않습니다.")
                    return 0
                else:
                    money_list[i] -= total_cost
                break
            i += 1

    # 처리후 정보 저장
    save_file(id_list,money_list,str(ctx.message.guild) + " user.xlsx")
    msg = "아이템 : " + item + "\n수량 : " + str(ea) + "\n지불한 금액 : " + str(total_cost) + "\n잔고 : " + str(money_list[i])
    embed = discord.Embed(color=discord.Color.blue())
    embed.add_field(name=f"결제완료", value=msg, inline=False)
    embed.set_footer(text= f"{ctx.message.author.nick}",icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed= embed)

@bot.command()
async def play(ctx, *, content):
    # 영상을 오디오 최적화 하는 옵션
    YDL_OPTIONS = {
        'format': 'bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song.%(ext)s',
    }
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    temp = content.split(" ")
    text = ""
    for t in temp:
        if len(temp) > 1:
            text += t + " "
        else:
            text += t
    print(text)

    # message를 쓴적이 있다면 id 값으로 message 객체 생성
    if len(message_id) > 0:
        message = await ctx.fetch_message(message_id[0])

    isFirst = False
    # url 값이 정상적인 값인지 확인
    try:
        url = text
        url1 = re.match('(https?://)?(www\.)?((youtube\.(com))/watch\?v=([-\w]+)|youtu\.be/([-\w]+))', text)  # 정규 표현식을 사용해 url 검사
        if url1 == None:
            if text in ['1', '2', '3', '4', '5']:  # 입력값이 숫자고 선택목록이 있을경우만 선택할수있음
                if len(showlist) > 0:
                    url = urllist[int(text) - 1]
                    title = showlist[int(text) - 1]
                    showlist.clear()
                    urllist.clear()
                else:
                    print("노래를 검색하지 않았습니다.")
                    return
                # 재생목록 보여준거 수정하면서 재생됬다고 수정해야함
            else:
                # 노래 목록을 선택하려고 할때마다 이전목록을 초기화시킴
                showlist.clear()
                urllist.clear()
                search_youtube(text)
                if len(message_id) > 0:  # 이전에 showlist를 메세지를 띄운경우 그 메세지를 삭제
                    await message.delete()
                    message_id.clear()
                message = await ctx.send("로딩중")
                message_id.append(message.id)  # 메세지 id정보 저장
                playlist = "**트랙을 선택해주세요.** ``!play 1-5``\n"
                for i in range(5):
                    playlist += "**" + str(i + 1) + "** : " + showlist[i] + "\n"
                await message.edit(content=playlist)
                return
        else:
            isFirst = True
            message = await ctx.send("로딩중")
    except IndexError:
        await ctx.send(embed=discord.Embed(title=":no_entry_sign: url을 입력해주세요.", colour=0x2EFEF7))
        return

    # 정보 설정
    channel = ctx.message.author.voice.channel
    server = ctx.guild  # 서버 정보 는 guild 에 들어있음
    voice_client = ctx.guild.voice_client  # 현재 채널의 봇정보를 가져옴
    # 명령어 친 유저가 해당 채널에 없으면 에러 발생 수정 바람
    # 봇이 없으면 채널에 입장시킴
    if voice_client == None:
        try:
            voice_client = await channel.connect()
        except discord.errors.InvalidArgument:  # 유저가 음성채널에 접속해있지 않을 때
            await ctx.send(embed=discord.Embed(title=":no_entry_sign: 음성채널에 접속하고 사용해주세요.", colour=0x2EFEF7))
            return

    # 봇이 음성채널에 접속해있고 음악을 재생할 때 재생목록에 노래를 추가함
    if voice_client.is_connected() and voice_client.is_playing():
        try:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                player = ydl.extract_info(url, download=False)
                if isFirst:
                    isFirst = False
                    title = player['title']
        except youtube_dl.utils.DownloadError:  # 유저가 제대로 된 유튜브 경로를 입력하지 않았을 때
            print(url)
            await ctx.send(embed=discord.Embed(title=":no_entry_sign: 존재하지 않는 경로입니다.", colour=0x2EFEF7))
            await voice_client.disconnect()
            return
        if server.id in que:  # 큐에 값이 들어있을 때 ( 재생목록에 노래가 있을때)
            que[server.id].append(player)  # 노래 추가
            que_list.append(title)
        else:  # 큐에 값이 없을 때 (재생목록에 노래가 없을때)
            que[server.id] = [player]  # 대기열에 노래를 리스트 형태로 추가함
            que_list.append(title)
        await message.edit(content=f"{player['title']} 추가 완료!")
        message_id.clear()
        return

    # 최초로 노래 재생을 할때
    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            player = ydl.extract_info(url, download=False)
        await message.edit(content=f"{player['title']} 재생")
        message_id.clear()
    except youtube_dl.utils.DownloadError:  # 유저가 제대로 된 유튜브 경로를 입력하지 않았을 때
        print(url)
        await ctx.send(embed=discord.Embed(title=":no_entry_sign: 존재하지 않는 경로입니다.", colour=0x2EFEF7))
        await voice_client.disconnect()
        return

    print(player)
    voice_client.play(FFmpegPCMAudio(player['formats'][0]['url'], **FFMPEG_OPTIONS),after=lambda e: queue(server.id, voice_client, FFMPEG_OPTIONS))  # 노래 재생
    # 볼륨설정 voice_client.source는 play이후에 생성되기때문에 play이후에 설정해줌
    voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
    voice_client.source.volume = volume

# 스킵
@bot.command()
async def 스킵(ctx):
    voice_client = ctx.guild.voice_client

    if voice_client.is_playing():
        voice_client.stop()

# 재생목록
@bot.command()
async def 재생목록(ctx):
    msg = ""
    i = 1
    if len(que_list) > 0 :
        for song in que_list:
            msg += "**" + str(i) + "** : " + song + "\n"
            i += 1
        await ctx.send(msg)
    else :
        await ctx.send("대기열이 없습니다!")

# 봇 퇴장
@bot.command()
async def 중지(ctx):
    voice_client = ctx.guild.voice_client

    if voice_client == None:  # 봇이 음성채널에 접속해있지 않았을 때
        await ctx.send(embed=discord.Embed(title=":no_entry_sign: 봇이 음성채널에 없어요.", colour=0x2EFEF7))
        return
    que = {}  # 퇴장하면서 입장했을떄 설정한 정보 초기화
    que_list = {}
    message_id.clear()
    await ctx.send(embed=discord.Embed(title=":mute: 채널에서 나갑니다.", colour=0x2EFEF7))  # 봇이 음성채널에 접속해있을 때
    await voice_client.disconnect()

# 에러 처리
@구매.error
async def 구매_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        title = "사용법:\n"
        content = "```diff\n!구매 [아이템] [수량]```"
        await ctx.send(title + content)

# run함수는 on_ready 랑 bot.command 이후에 실행이 되어야함
bot.run(token)  # 해당 토큰을 가진 봇을 실행