import discord
from discord.ext import commands  # 본격적인 봇 생성을  위한 모듈
from discord import FFmpegPCMAudio
from youtube_search import YoutubeSearch
import asyncio
import os
import re
from youtube_dl import YoutubeDL
import youtube_dl
import random
from random import choice
import ffmpeg

# 디스코드 1.0 이상에서는 bot을 이용한 방식이 보편적이고 유용하다.(문법적으로도 좀 바뀜)

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

# 추천 변수들
users_list = []


def search_youtube(msg):
    search = YoutubeSearch(msg, max_results=10).to_dict()  # youtube 검색 api
    count = 1
    i = 0
    # 생방송이거나 그런건 거름
    while(True):
        if count == 6:
            break
        if search[i]['duration'] == 0:
            i += 1
            continue
        text = search[i]['title']
        text += " (" + str(search[i]['duration']) + ")"
        showlist.append(text)
        url = "https://www.youtube.com/" + search[i]['url_suffix']
        urllist.append(url)

        count += 1
        i += 1

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

# 봇이 구동되었을 때 보여지는 코드
@bot.event
async def on_ready():
    print(f"{bot.user}에 로그인하였습니다!")

@bot.command()
async def 골라(ctx,*,content):
    item_list = content.split(" ")
    pick = choice(item_list)
    await ctx.send(pick)

@bot.command()
async def 참가(ctx,*,content):
    attend_list = content.split(" ")
    for member in attend_list:
        users_list.append(member)

    await ctx.send("등록되었습니다!")

@bot.command()
async def 참가목록(ctx):
    msg = ""
    i = 1
    for user in users_list:
        msg += f"{i}. {user}\n"
        i += 1
    await ctx.send(msg)

@bot.command()
async def 나누기(ctx, content):
    if users_list != []:
        group_num = int(content.split(" ")[0])
        pick = int(len(users_list) / group_num)
        group_list = []
        rest_list = []

        while len(users_list) > 0:
            temp = []
            if len(group_list) < group_num :
                for _ in range(pick):
                    player = choice(users_list)
                    temp.append(player)
                    users_list.remove(player)
                group_list.append(temp)
            else:
                player = choice(users_list)
                rest_list.append(player)
                users_list.remove(player)

        users_list.clear()
        embed = discord.Embed(title=f"그룹", color=discord.Color.blue())
        i = 1
        for _ in range(group_num):
            msg = ""
            for member in group_list[i-1]:
                msg += member + "\n"
            embed.add_field(name=f"Team{i}", value=msg, inline=False)
            i += 1

        if len(rest_list) > 0:
            msg = ""
            for rest in rest_list:
                msg += rest + "\n"
            embed.add_field(name="잔류인원", value=msg, inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("참가한 사람들이 없습니다!")

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
        url1 = re.match('(https?://)?(www\.)?((youtube\.(com))/watch\?v=([-\w]+)|youtu\.be/([-\w]+))',
                        text)  # 정규 표현식을 사용해 url 검사
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

# run함수는 on_ready 랑 bot.command 이후에 실행이 되어야함
bot.run(token)  # 해당 토큰을 가진 봇을 실행
