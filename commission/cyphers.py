import discord
from discord.ext import commands  # 본격적인 봇 생성을  위한 모듈
import asyncio
import os
import requests

# 토큰 값이 노출방지를 위해 파일을 따로둬서 관리함   github에 올릴 때도 token.txt는 ignore처리 하면 토큰값이 노출될일이없음
token_path = os.path.dirname(os.path.abspath(__file__)) + "\\token.txt"
t = open(token_path, "r", encoding="utf-8")
token = t.read().split()[0]
t.close()

# 사이퍼즈 api 토큰값
api_path = os.path.dirname(os.path.abspath(__file__)) + "\\cyphers_token.txt"
f = open(api_path, "r", encoding="utf-8")
API_KEY = f.read().split()[0]

# 봇의 설정
# 생성된 토큰을 입력해준다.
game = discord.Game("!help")  # 상태 메시지
# commands_prefix는 해당 구문이 맨앞에 있을떄 명령어로 인식한다는 뜻 (!도움,!안녕 등) status 는 봇의값의 상태(온라인,자리비움 등) activity는 상태말 임
bot = commands.Bot(command_prefix='!', status=discord.Status.online, activity=game, help_command=None)

# 봇이 구동되었을 때 보여지는 코드
@bot.event
async def on_ready():
    print(f"{bot.user}에 로그인하였습니다!")

@bot.command()
async def 전적(ctx,*,content):
    msg = content.split(" ")
    nickname = msg[1]
    gametype = msg[0]

    if gametype == "공식":
        mode = "rating"
    elif gametype == "일반":
        mode = "normal"

    req = requests.get(f'https://api.neople.co.kr/cy/players?nickname={nickname}&wordType=<wordType>&apikey={API_KEY}')

    if req.status_code == 200:
        info = req.json()
        player_id = info['rows'][0]['playerId']
        print(player_id)

        req = requests.get(f'https://api.neople.co.kr/cy/players/{player_id}/matches?gameTypeId={mode}&apikey={API_KEY}')
        if req.status_code == 200:
            info = req.json()
            matches = info['matches']['rows']

            first_content = "```cs\n"
            second_content = "```\n"
            third_content = "```"
            total = 0
            win = 0
            lose = 0
            # 매치기록이 하나라도 있는경우
            if len(matches) >0 :
                for match in matches:
                    playinfo = match['playInfo']
                    result = playinfo['result']
                    if result == "win":
                        win += 1
                        result = "승리"
                        first_content += "'" + result + "' "
                    else:
                        lose += 1
                        result = "패배"
                        first_content += "#" + result + "  "

                    character = playinfo['characterName']
                    third_content += character + "\n"

                    kill = playinfo['killCount']
                    death = playinfo['deathCount']
                    assist = playinfo['assistCount']
                    first_content += str(kill) + "/" + str(death) + "/" + str(assist) + "\n"

                    if int(death) == 0:
                        kill_rate = int(kill) + int(assist)
                    else:
                        kill_rate = float((int(kill) + int(assist)) / int(death))
                        kill_rate = round(kill_rate,2)
                    if kill_rate > 7:
                        kill_rate = str(kill_rate)
                    second_content += str(kill_rate) + "\n"

                    #content += f"{result} {character} {kill}/{death}/{assist} {kill_rate} {gametype}\n"

                    total += 1
                    print(match)
                first_content += "```"
                second_content +="```"
                third_content += "```"
                embed = discord.Embed(title=f"[{gametype}] - 최근 {total}전 {win}승 {lose}패", color=discord.Color.blue())
                embed.set_author(name=f"{nickname}")
                embed.add_field(name="결과/KDA",value=first_content,inline=True)
                embed.add_field(name="KDA비율", value=second_content, inline=True)
                embed.add_field(name="캐릭터", value=third_content, inline=True)
                await ctx.send(embed= embed)
            else :
                await ctx.send("해당 기록이 존재하지 않습니다!")
        else :
            print("에러")
    else :
        print(nickname)
        print(API_KEY)
        print(req.status_code)

bot.run(token)  # 해당 토큰을 가진 봇을 실행
