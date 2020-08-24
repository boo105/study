import discord
from discord.ext import commands    # 본격적인 봇 생성을  위한 모듈
from discord import FFmpegPCMAudio
from youtube_search import YoutubeSearch
import asyncio
import os
import re
from youtube_dl import YoutubeDL
import youtube_dl
import requests

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
urllist = []    # url을 저장할 list

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
        else:
            print("다음 재생 목록 없음")
    except Exception as e : # 에러 발생시
        print(e)

# 봇이 구동되었을 때 보여지는 코드
@bot.event
async def on_ready():
    print(f"{bot.user}에 로그인하였습니다!")

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

@bot.event
async def on_member_join(member):
    # 유저가 서버에 처음 접속시 발생하는 이벤트
    await member.send("어서오세요! {}님이 병신이 되신걸 환영합니다!".format(member))
    # member 매개변수로 처음 들어온 유저의 정보를 받아와 member.send로 해당 유저에게 메세지를 보냅니다.

@bot.event
async def on_member_remove(member):
    await member.send("{}님이 서버에서 나가셨습니다.".format(member))

"""
@bot.command()
async def kick(ctx,member : discord.Member,*,reason = None):
    await member.kick(reason = reason)
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
    # embed를 이용해 썸네일,이미지,영상도 추가 가능!
    embed = discord.Embed(title=f"{ctx.author}님 무엇을 도와드릴까요?", description="봇 소개", color=discord.Color.blue())
    embed.add_field(name=f"명령어", value=f"!help !welcome(임시) !play 검색어 !quit", inline=False)
    embed.add_field(name=f"욕설필터링", value=f"각종 욕설 및 노무현 고인드립 등 필터링을 합니다.(임시)", inline=False)
    await ctx.send(embed=embed)
    #await ctx.send(f"{ctx.author.mention}님 무엇을 도와드릴까요?")

@bot.command()
async def welcome(ctx):
    # embed를 이용해 썸네일,이미지,영상도 추가 가능!
    embed = discord.Embed(title = f"우리서버에 오신 것을 환영합니다.", description="방장님을 위한 서버!",color=discord.Color.blue())
    embed.add_field(name = f"우리서버는요?", value=f"질병걸린 사람들을 위한 치료센터에요!",inline=False)
    embed.add_field(name = f"재석이는?", value=f"전라도홍어라서 남 통수를 잘쳐요!", inline= False)
    await ctx.send(embed=embed)
@bot.command()
async def lol(ctx,content):
    name = content.split(" ")[0]
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
    msg = content.split(" ")

    # url 값이 정상적인 값인지 확인
    try:
        text = msg[0]
        url = text
        url1 = re.match('(https?://)?(www\.)?((youtube\.(com))/watch\?v=([-\w]+)|youtu\.be/([-\w]+))', text)  # 정규 표현식을 사용해 url 검사
        
        if text in ['1', '2', '3', '4', '5']:   # 입력값이 숫자고 선택목록이 있을경우만 선택할수있음
            if len(showlist) > 0 :
              url = urllist[int(text) - 1]
              showlist.clear()
              urllist.clear()
            else:
                print("노래를 검색하지 않았습니다.")
                return
            # 재생목록 보여준거 수정하면서 재생됬다고 수정해야함
        elif url1 == None:
            # 노래 목록을 선택하려고 할때마다 이전목록을 초기화시킴
            showlist.clear()
            urllist.clear()
            search_youtube(text)
            embed = discord.Embed(title=f"트랙을 선택해주세요. !play 1-5", color=discord.Color.blue())
            for i in range(5):
                embed.add_field(name=f"{i+1}.",value=f"{showlist[i]}" , inline=False)
            await ctx.send(embed=embed)
            return
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
        await ctx.send(embed=discord.Embed(title=":white_check_mark: {} 추가 완료!".format(player['title']), colour=0x2EFEF7))
        return

    # 최초로 노래 재생을 할때
    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            player = ydl.extract_info(url,download=False)
        await ctx.send(embed=discord.Embed(title=":white_check_mark: {} 재생".format(player['title']), colour=0x2EFEF7))
    except youtube_dl.utils.DownloadError:  # 유저가 제대로 된 유튜브 경로를 입력하지 않았을 때
        await ctx.send(embed=discord.Embed(title=":no_entry_sign: 존재하지 않는 경로입니다.", colour=0x2EFEF7))
        await voice_client.disconnect()
        return

    print(player)
    voice_client.play(FFmpegPCMAudio(player['formats'][0]['url'], **FFMPEG_OPTIONS),after=lambda e : queue(server.id,voice_client,FFMPEG_OPTIONS))   # 노래 재생

@bot.command()
async def quit(ctx):
    channel = ctx.message.author.voice.channel
    server = ctx.guild
    voice_client = ctx.guild.voice_client

    if voice_client == None:  # 봇이 음성채널에 접속해있지 않았을 때
        await ctx.send(embed=discord.Embed(title=":no_entry_sign: 봇이 음성채널에 없어요.", colour=0x2EFEF7))
        return
    que = {}    # 퇴장하면서 입장했을떄 설정한 정보 초기화
    await ctx.send(embed=discord.Embed(title=":mute: 채널에서 나갑니다.", colour=0x2EFEF7))  # 봇이 음성채널에 접속해있을 때
    await voice_client.disconnect()

# run함수는 on_ready 랑 bot.command 이후에 실행이 되어야함
bot.run(token)  # 해당 토큰을 가진 봇을 실행
