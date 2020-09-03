import discord
from discord.ext import commands    # 본격적인 봇 생성을  위한 모듈
from discord import FFmpegPCMAudio
from discord.ext.commands import has_permissions, MissingPermissions
from youtube_search import YoutubeSearch
import asyncio
import os
import re
from youtube_dl import YoutubeDL
import youtube_dl
import requests
import random
import urllib
from urllib.request import Request, urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup

# 디스코드 1.0 이상에서는 bot을 이용한 방식이 보편적이고 유용하다.(문법적으로도 좀 바뀜)

# 토큰 값이 노출방지를 위해 파일을 따로둬서 관리함   github에 올릴 때도 token.txt는 ignore처리 하면 토큰값이 노출될일이없음
token_path = os.path.dirname(os.path.abspath(__file__))+"\\token.txt"
t = open(token_path,"r",encoding= "utf-8")
token = t.read().split()[0]
t.close()

# riot api_key 값과 헤더값 설정
api_path = os.path.dirname(os.path.abspath(__file__))+"\\riotAPI.txt"
f = open(api_path,"r",encoding="utf-8")
API_KEY = f.read().split()[0]
HEADER = {
    "Accept-Charset" : "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token" : API_KEY,
    "Accept-Language" : "ko-KR,ko; q=0.9, en-US; q=0.8,en; q=0.7"
}
main_url = "https://kr.api.riotgames.com"

# 봇의 설정
# 생성된 토큰을 입력해준다.
game = discord.Game("!help")  # 상태 메시지
# commands_prefix는 해당 구문이 맨앞에 있을떄 명령어로 인식한다는 뜻 (!도움,!안녕 등) status 는 봇의값의 상태(온라인,자리비움 등) activity는 상태말 임
bot = commands.Bot(command_prefix='!', status=discord.Status.online, activity=game, help_command=None)
bad_word = ["씨발","병신","개새끼" , "씨벌", "시발"]

# 노래 재생을 위한 변수들
que = {}    # 재생목록 대기열
showlist = []   # 노래 제목과 시간을 표시할 list
urllist = []    # url을 저장할 listz
message_id = [] # bot이 메세지의 id 정보를 가지고있음
volume = 0.4

# 추천 변수들
users_list = []

def search_youtube(msg):
    search = YoutubeSearch(msg , max_results=5).to_dict()   # youtube 검색 api
    
    # list에 알맞은 정보를 저장함
    for i in range(0,5):
        text = search[i]['title']
        text += " (" + str(search[i]['duration']) + ")"
        showlist.append(text)
        url = "https://www.youtube.com/" + search[i]['url_suffix']
        urllist.append(url)

def get_SummonerId(summonerName):
    url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}"
    req = requests.get(url=url, headers= HEADER)
    print(req.status_code)
    if req.status_code == 200:
        return req.json()
    else:
        print(req.status_code)

def get_RankInfo(summonerID):
    url = f"{main_url}/lol/league/v4/entries/by-summoner/{summonerID}"
    req = requests.get(url=url, headers=HEADER)
    if req.status_code == 200:
        leagues = req.json()
        if len(leagues) == 0:   # 데이터를 못읽으면 None 반환
            return None
        for league in leagues:
            if league['queueType'] == "RANKED_SOLO_5x5":
                return league
        return None
    else:
        print(req.status_code)

# !quit 명령어를 실행 하면 오류뜸
def queue(id,voice_client,options):  #음악 재생용 큐
    print("queue 함수 들어옴")
    try :
        if que[id] != []:
            print("봇 대기열 재생목록 재생중")
            player = que[id].pop(0)
            voice_client.play(FFmpegPCMAudio(player['formats'][0]['url'], **options),after=lambda e : queue(id,voice_client,options))   # 노래 재생
            voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
            voice_client.source.volume = volume
        else:
            print("다음 재생 목록 없음")
    except Exception as e : # 에러 발생시
        print(e)

# 봇이 구동되었을 때 보여지는 코드
@bot.event
async def on_ready():
    print(f"{bot.user}에 로그인하였습니다!")

"""
@bot.event
async def on_message(message):      # 메세지가 채널에 올라왔을떄
    message_content = message.content
    #bad = message_content.find("씨발")    # 해당 단어가 있으면 0 이상을 반환
    for word in bad_word:   # bad_word 개수가 늘어날수록 처리속도가 늘어나는지 확인 아직 안함
        bad = message.content.find(word)
        print(bad)
        if bad >= 0:
            await message.channel.send(f"욕하지마세요 {message.author} 걸레년아")   # 욕이 올라온 채널에 해당 메세지를 전송
            await message.delete()  # 욕설이 담긴 메세지 삭제   단 봇이 메시지 관리를 할수 있는 권한을 줘야함
    await bot.process_commands(message) # 메세지중 명령어가 있을 경우 처리해주는 코드
"""

@bot.event
async def on_member_join(member):
    # 유저가 서버에 처음 접속시 발생하는 이벤트
    channel = bot.get_channel(297698515415728128)
    await channel.send("어서오세요! {}님이 민초단이 되신걸 환영합니다!".format(member))
    # member 매개변수로 처음 들어온 유저의 정보를 받아와 member.send로 해당 유저에게 메세지를 보냅니다.

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(297698515415728128)
    await channel.send(f"{member}님이 민초단을 배신하였습니다.")

"""
@bot.command()
async def kick(ctx,member : discord.Member,*,reason = None):
    await member.kick(reason=reason)
    await ctx.send("{}님이 강퇴당하였습니다.".format(member))
@bot.command()
async def ban(ctx,member : discord.Member,*,reason = None):
    await member.ban(reason = reason)
    await ctx.send("{}님이 밴당하였습니다.".format(member.mention))

@bot.command()
async def unban(ctx,*,member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name,user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"Unbanned {user.mention}")
            return
"""
@bot.command()
async def help(ctx):
    msg = "!help\n노래 : !play (검색어) !skip !quit\n!코로나\n!상영영화\n!날씨\n당첨 : !참가 !추첨 (추첨개수)\n확률 : !주사위\n도박 : !러시안룰렛\n!실검\n\n----보류 중----\n!lol"

    # embed를 이용해 썸네일,이미지,영상도 추가 가능!
    embed = discord.Embed(title=f"{ctx.author}님 무엇을 도와드릴까요?", color=discord.Color.blue())
    embed.add_field(name=f"----명령어----", value=msg, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def lol(ctx,*,content):
    temp = content.split(" ")
    name = ""
    for t in temp:
        name += t
    print(name)

    print(name)
    info = get_SummonerId(name)
    rank_info = get_RankInfo(info['id'])
    print(rank_info)
    embed = discord.Embed(title=f"{name} 랭크 정보", color=discord.Color.blue())
    embed.add_field(name=f"랭크", value=f"{rank_info['tier']} {rank_info['rank']}", inline=False)
    embed.add_field(name=f"점수", value=f"{rank_info['leaguePoints']}", inline=False)
    embed.add_field(name=f"승/패", value=f"{rank_info['wins']} / {rank_info['losses']}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def 참가(ctx):
    user = ctx.message.author
    if user in users_list:
        msg = str(user) + " 님은 이미 참가하였습니다."
    else:
        msg = str(user) + " 님이 참가했습니다."
        users_list.append(ctx.message.author)

    # message를 쓴적이 있다면 id 값으로 message 객체 생성
    if len(message_id) > 0:
        message = await ctx.fetch_message(message_id[0])
        await message.delete()
        message_id.clear()
    message = await ctx.send(msg)
    message_id.append(message.id)

@bot.command()
async def 참가목록(ctx):
    msg = ""
    i = 1
    for user in users_list:
        msg += f"{i}. {user}\n"
        i += 1
    await ctx.send(msg)

@bot.command()
async def 추첨(ctx,content):
    if users_list != []:
        pick = content.split(" ")[0]
        if int(pick) > len(users_list):
            await ctx.send("추첨할 개수가 참가한 사람들보다 많습니다.")
            return
        msg = ""
        users = random.sample(users_list,int(pick))
        for user in users:
            msg += f"{user}\n"
        msg += "당첨되셨습니다."
        users_list.clear()
        await ctx.send(msg)
    else:
        await ctx.send("참가한 사람들이 없습니다!")

@bot.command()
async def 주사위(ctx):
    msg = "-- " + str(random.randrange(1,100)) + " --"
    await ctx.send(msg)

@bot.command()
async def 실검(ctx):
    # 방법 1
    # 헤더는 유저정보를 담긴 user-agent 값을 넘겨서 유저인걸 인식시킨다. 그리고 각종 설정값이 담긴 cookie 값도 설정해줌
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
              'cookie' : 'NNB=JOG5SUQPOJSF4; ASID=74229d3b00000170c9505c160000005a; _ga_4BKHBFKFK0=GS1.1.1595757924.2.1.1595757924.60; nx_ssl=2; _ga=GA1.1.1866649330.1587454866; _ga_7VKFYR6RV1=GS1.1.1597243589.7.0.1597243589.60; nid_inf=-1485735036; NID_AUT=/lVwqT4qcuHVOSWEPWjo4BDksW8AXy8mrNhXRbV44Ysu0lhiSKEbTWW/FLrYlJTv; NID_JKL=3iDdkoMQdNOR/YSukSs3orqY6KbRlaysKaHkHRuj/yE=; BMR=; _datalab_cid=50000000; page_uid=U1t1hlprvN8ss7vDnBlssssssb0-291485; NRTK=ag#20s_gr#4_ma#2_si#2_en#2_sp#2; NID_SES=AAABnGxfgi0AVs0bAmkvQ6pZOv5rH8EO9dUcNLT1USM1hG2UYzYXCkS2PWZTtf/n9D82Y0igcRr4yf2248/s0/oF7supMd18PsCuRH3EaPJnSiLflYApfsOdZWbI89miVLmyy3GITgGA8vwYh/UPczJXYWB08inDwMiwQ+8M4StzS+qhvwp6CsbcoydkXsZzahJbnQSvSlhYJMcOHUKWNKwtK5g501p+sb/qjEQda9ktIuy1zAc8Ms8FtAVTWTJavFQoiIx6WnvcV2cbtDeAYdl//tEnFokI9TwTBZvD6suoi1jU98aBoFfVZD4zTX1x2g+tw4ZtgIzhfONHJLyb4EQPIGh487KYDc/sazmKEn8OxftqgW0HD5yx13WK3MG3G2ocyCkc/bDa6Rss1QqJYo/yc4aCBlmmpko5KnbZb/mjE0BQb2Q8/hZVRIwCOZLi8GF+nxFGstCQVlphmfVv586MdzoI/IZC1snj4fEOoNokTvhQmNpndYaOieHJiOSsgi1e1vwpOwWI7N+6rUBkFgEYJDLU2qRUaJmLAkhOMO2iswFj'}
    site = "https://datalab.naver.com/keyword/realtimeList.naver?age=20s"
    html = requests.get(site,headers=header)
    bs = BeautifulSoup(html.content, 'html.parser')
    real_time = bs.select('span.item_title')

    msg = ""
    i = 1
    for item in real_time:
        msg += "**" + str(i) + "**." + item.text + "\n"
        i += 1

    # 방법 2
    # json 주소 구하는법은 브라우저 개발자도구에서 network 탭에서 필터링으로 원하는 부분 필터하고 나온 부분에 header에서 Request URL 값을 본다.
    """
    # 아래 주소가 메인페이지 내부에서 호출되는 실시간 검색어 데이터를 넘겨주는 주소
    # requests.get("주소").json() 을 하면 데이터를 json 형태로 받아올 수 있습니다.
    # 아래 주소를 직접 브라우저에서 접속해보시기 바랍니다.
    json = requests.get('https://www.naver.com/srchrank?frm=main').json()
    # json 데이터에서 "data" 항목의 값을 추출
    ranks = json.get("data")
    print(ranks)
    """

    # 메시지 보내기
    embed = discord.Embed(title="실시간 검색어", description="", color=0x5CD1E5)
    embed.add_field(name="조건 : 20대, 모든분야", value=msg, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def 상영영화(ctx):
    site = "https://movie.naver.com/movie/running/current.nhn?view=list&tab=normal&order=likeCount"
    html = urlopen(site)  # html 얻기
    bs = BeautifulSoup(html, 'html.parser')

    title_list = bs.select('dt.tit > a')    # 제목
    rate_list = bs.select('span.num')   # 평점
    
    # 문자열 처리
    msg = ""
    for num in range(20):
        msg += "**" + str(num+1) + "**." + title_list[num].text + " " + rate_list[num].text + "\n"
    # 메시지 보내기
    embed = discord.Embed(title="상영영화", description="", color=0x5CD1E5)
    embed.add_field(name="좋아요순", value=msg, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def 코로나(ctx):
    # 코로나 사이트
    covid_site = "http://ncov.mohw.go.kr/index.jsp"
    covid_notice = "http://ncov.mohw.go.kr"
    html = urlopen(covid_site)  # html 얻기
    bs = BeautifulSoup(html,'html.parser')
    latest_update_time = bs.find('span',{'class' : "livedate"}).text.split(',')[0][1:].split('.')    # span class = livedata 인걸 찾아서 문자열을 분리함
    statistical_numbers = bs.findAll('span', {'class': 'num'})  # 수치 통계들
    beforeday_numbers = bs.findAll('span', {'class': 'before'}) # 지난 데이터

    # 주요 브리핑 및 뉴스링크
    brief_tasks = []
    main_brief = bs.findAll('a',{'href' : re.compile('\/tcmBoardView\.do\?contSeq=[0-9]*')})
    for brf in main_brief:
        container = []
        container.append(brf.text)
        container.append(covid_notice + brf['href'])
        brief_tasks.append(container)
    print(brief_tasks)

    # 통계수치
    statNum = []
    # 전일대비 수치
    beforeNum = []
    for num in range(7):
        statNum.append(statistical_numbers[num].text)
    for num in range(4):
        beforeNum.append(beforeday_numbers[num].text.split('(')[-1].split(')')[0])

    total_people_int = statNum[0].split(')')[-1].split(',')
    tpInt = ''.join(total_people_int)
    lethatRate = round((int(statNum[3]) / int(tpInt)) * 100, 2)
    embed = discord.Embed(title="Covid-19 Virus Korea Status", description="", color=0x5CD1E5)
    embed.add_field(name="Data source : Ministry of Health and Welfare of Korea",
                    value="http://ncov.mohw.go.kr/index.jsp", inline=False)
    embed.add_field(name="Latest data refred time",
                    value="해당 자료는 " + latest_update_time[0] + "월 " + latest_update_time[1] + "일 " + latest_update_time[2] + " 자료입니다.", inline=False)
    embed.add_field(name="확진환자(누적)", value=statNum[0].split(')')[-1] + "(" + beforeNum[0] + ")", inline=True)
    embed.add_field(name="완치환자(격리해제)", value=statNum[1] + "(" + beforeNum[1] + ")", inline=True)
    embed.add_field(name="치료중(격리 중)", value=statNum[2] + "(" + beforeNum[2] + ")", inline=True)
    embed.add_field(name="사망", value=statNum[3] + "(" + beforeNum[3] + ")", inline=True)
    embed.add_field(name="누적확진률", value=statNum[6], inline=True)
    embed.add_field(name="치사율", value=str(lethatRate) + " %", inline=True)
    embed.add_field(name="- 최신 브리핑 1 : " + brief_tasks[0][0], value="Link : " + brief_tasks[0][1], inline=False)
    embed.add_field(name="- 최신 브리핑 2 : " + brief_tasks[1][0], value="Link : " + brief_tasks[1][1], inline=False)
    embed.set_thumbnail(url="https://wikis.krsocsci.org/images/7/79/%EB%8C%80%ED%95%9C%EC%99%95%EA%B5%AD_%ED%83%9C%EA%B7%B9%EA%B8%B0.jpg")
    embed.set_footer(text='Service provided by Hoplin.',
                     icon_url='https://avatars2.githubusercontent.com/u/45956041?s=460&u=1caf3b112111cbd9849a2b95a88c3a8f3a15ecfa&v=4')
    await ctx.send("Covid-19 Virus Korea Status", embed=embed)

@bot.command()
async def 날씨(ctx):
    site = "https://search.naver.com/search.naver?sm=top_hty&fbm=0&ie=utf8&query=%EB%82%A0%EC%94%A8"
    html = urlopen(site)  # html 얻기
    bs = BeautifulSoup(html, 'html.parser')
    # 하루 총 날씨정보
    temperature_list = bs.findAll('span',{'class' : 'todaytemp'})
    #print(temperature_list)
    weather_list = bs.findAll('p',{'class' : 'cast_txt'})
    #print(weather_list)
    hour_rain = bs.find('span',{'class' : 'rainfall'})
    #print(hour_rain.text)

    #시간대별 날씨
    hour_temperature_list = bs.select('ul > li > dl > dd.weather_item > span')  # 온도
    hour_weather_list = bs.select('ul > li > dl > dd > span.ico_state2')    # 날씨
    hour_time_list = bs.select('ul > li > dl > dd.item_time > span')    # 시간
    #print(hour_temperature_list)
    #print(hour_weather_list)
    #print(hour_time_list)
    
    # 온도 텍스트만 추출
    hour_temperature_show = []
    for num in range(8):
        hour_temperature_show.append(hour_temperature_list[num * 3].text)
    #print(hour_temperature_show)

    # 문자열 가공
    hour_first = ""
    hour_second = " "
    hour_third = ""
    for num in range(8):
        if num==7:
            hour_first += hour_temperature_show[num]
            hour_second += hour_weather_list[num].text
            hour_third += hour_time_list[num].text.replace(" ", "")
        else:
            hour_first += hour_temperature_show[num] + "   "
            hour_second += hour_weather_list[num].text + "   "
            hour_third += hour_time_list[num].text.replace(" ","") + " "

    hour_info = "```css\n" + hour_third + "\n" + "[" + hour_first + "]\n" + hour_second + "```"
    #print(hour_info)

    # 메세지 레이아웃 설정 및 보내기
    embed = discord.Embed(title="날씨", description="", color=0x5CD1E5)
    embed.add_field(name="현재 날씨", value=temperature_list[0].text + "℃ \n" + weather_list[0].text + "\n" + hour_rain.text, inline=False)
    embed.add_field(name="시간대별 날씨", value=hour_info,inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def 러시안룰렛(ctx):
    if users_list != []:

      if len(users_list) < 2:
          await ctx.send("러시안 룰렛을 하기에 사람이 부족합니다.")
          return
      else:
          # 러시안 룰렛에 당첨된 유저 선택
          user = random.sample(users_list,1)
          users_list.clear()
          #await ctx.guild.kick(user[0])
          await user[0].kick(reason="러시안 룰렛에 죽었습니다!")
          await ctx.send(user + "님이 죽었습니다!")
    else:
        await ctx.send("참가한 사람들이 없습니다!")

@bot.command()
async def play(ctx,*,content):
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
        else :
            text += t
    print(text)

    # message를 쓴적이 있다면 id 값으로 message 객체 생성
    if len(message_id) > 0:
        message = await ctx.fetch_message(message_id[0])

    # url 값이 정상적인 값인지 확인
    try:
        url = text
        url1 = re.match('(https?://)?(www\.)?((youtube\.(com))/watch\?v=([-\w]+)|youtu\.be/([-\w]+))', text)  # 정규 표현식을 사용해 url 검사

        if url1 == None:
            if text in ['1', '2', '3', '4', '5']:  # 입력값이 숫자고 선택목록이 있을경우만 선택할수있음
                if len(showlist) > 0:
                    url = urllist[int(text) - 1]
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
                if len(message_id) > 0: # 이전에 showlist를 메세지를 띄운경우 그 메세지를 삭제
                    await message.delete()
                    message_id.clear()
                message = await ctx.send("로딩중")
                message_id.append(message.id)   # 메세지 id정보 저장
                playlist = "**트랙을 선택해주세요.** ``!play 1-5``\n"
                for i in range(5):
                    playlist += "**" + str(i+1) + "**:" + showlist[i] + "\n"
                await message.edit(content = playlist)
                return
        else:
            message = await ctx.send("로딩중")
    except IndexError:
        await ctx.send(embed=discord.Embed(title=":no_entry_sign: url을 입력해주세요.", colour=0x2EFEF7))
        return

    # 정보 설정
    channel = ctx.message.author.voice.channel
    server = ctx.guild  # 서버 정보 는 guild 에 들어있음 
    voice_client = ctx.guild.voice_client   # 현재 채널의 봇정보를 가져옴
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
                player = ydl.extract_info(url,download=False)
        except youtube_dl.utils.DownloadError:  # 유저가 제대로 된 유튜브 경로를 입력하지 않았을 때
            await ctx.send(embed=discord.Embed(title=":no_entry_sign: 존재하지 않는 경로입니다.", colour=0x2EFEF7))
            await voice_client.disconnect()
            return
        if server.id in que:  # 큐에 값이 들어있을 때 ( 재생목록에 노래가 있을때)
            que[server.id].append(player)   # 노래 추가
        else:  # 큐에 값이 없을 때 (재생목록에 노래가 없을때)
            que[server.id] = [player]   # 대기열에 노래를 리스트 형태로 추가함
        await message.edit(content = f"{player['title']} 추가 완료!")
        message_id.clear()
        return

    # 최초로 노래 재생을 할때
    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            player = ydl.extract_info(url,download=False)
        await message.edit(content = f"{player['title']} 재생")
        message_id.clear()
    except youtube_dl.utils.DownloadError:  # 유저가 제대로 된 유튜브 경로를 입력하지 않았을 때
        await ctx.send(embed=discord.Embed(title=":no_entry_sign: 존재하지 않는 경로입니다.", colour=0x2EFEF7))
        await voice_client.disconnect()
        return

    print(player)
    voice_client.play(FFmpegPCMAudio(player['formats'][0]['url'], **FFMPEG_OPTIONS),after=lambda e : queue(server.id,voice_client,FFMPEG_OPTIONS))   # 노래 재생
    # 볼륨설정 voice_client.source는 play이후에 생성되기때문에 play이후에 설정해줌
    voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
    voice_client.source.volume = volume

# 스킵
@bot.command()
async def skip(ctx):
    channel = ctx.message.author.voice.channel
    server = ctx.guild
    voice_client = ctx.guild.voice_client
    
    if voice_client.is_playing():
        voice_client.stop()
# 봇 종료
@bot.command()
async def quit(ctx):
    voice_client = ctx.guild.voice_client

    if voice_client == None:  # 봇이 음성채널에 접속해있지 않았을 때
        await ctx.send(embed=discord.Embed(title=":no_entry_sign: 봇이 음성채널에 없어요.", colour=0x2EFEF7))
        return
    que = {}    # 퇴장하면서 입장했을떄 설정한 정보 초기화
    message_id.clear()
    await ctx.send(embed=discord.Embed(title=":mute: 채널에서 나갑니다.", colour=0x2EFEF7))  # 봇이 음성채널에 접속해있을 때
    await voice_client.disconnect()

@추첨.error
async def 추첨_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send("추첨 할 개수가 없습니다.")
# run함수는 on_ready 랑 bot.command 이후에 실행이 되어야함
bot.run(token)  # 해당 토큰을 가진 봇을 실행
