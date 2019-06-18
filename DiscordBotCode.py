# # Work with Python 3.6
# import discord
#
# TOKEN = 'XXXXXXXXXX'
#
# client = discord.Client()
#
# @client.event
# async def on_message(message):
#     # we do not want the bot to reply to itself
#     if message.author == client.user:
#         return
#
#     if message.content.startswith('!hello'):
#         msg = 'Hello {0.author.mention}'.format(message)
#         await client.send_message(message.channel, msg)
#woah


# Work with Python 3.6
import random
import asyncio
import aiohttp
import json
from random import randint
from discord.ext import commands
from discord import Game,User
from discord.ext.commands import Bot
import time

CHESSHELP = ["!c XN>YM: X for column N for row, to column Y row M",
             "!c newgame: start a new game for 2 player",
             "!c ai: start a new game against AI",
             ]


CHESSDEFAULT = [["BR","BK","BB","BQ","BG","BB","BK","BR"],
                ["BP","BP","BP","BP","BP","BP","BP","BP"],
                ["  ","  ","  ","  ","  ","  ","  ","  "],
                ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
                ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
                ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
                ["WP","WP","WP","WP","WP","WP","WP","WP"],
                ["WR","WK","WB","WQ","WG","WB","WK","WR"],
                ]

CHESSCODE = {"BR":"♜","BK":"♞","BB":"♝","BQ":"♛","BG":"♚","BP":"♟",
             "WR": "♖", "WK": "♘", "WB": "♗", "WQ": "♕", "WG": "♔", "WP": "♙",'  ':'  □'}

def toUpper(arg):
    return arg.upper()

def updateChessBoard():
    pass

def readNum(a):
    return Read(str(a))

def Read(a):
    if a == "1":
        return("||:one:||")
    elif a == "2":
        return("||:two:||")
    elif a == "3":
        return("||:three:||")
    elif a == "4":
        return("||:four:||")
    elif a == "5":
        return("||:five:||")
    elif a == "6":
        return("||:six:||")
    elif a == "7":
        return("||:seven:||")
    elif a == "8":
        return("||:eight:||")
    elif a== "B":
        return "||:bomb:||"
    elif a == "0":
        return("||:black_medium_small_square:||")

def userInputMatrix(M,n):
    for i in range (0,n):
        M.append([])
        for j in range(0,n):
            item = input("Enter item for "+"column "+str(j+1)+" row "+str(i+1)+", with 'b' for bomb or a number for a number.")
            M[i].append(item)
        print(M[i])
    Print = ""
    return M

def randomMatrix(n,M):
    for i in range(n):
        rand = [randint(0,n-1),randint(0,n-1)]
        while M[rand[0]][rand[1]]=="B":
            rand = [randint(0, n - 1), randint(0, n - 1)]
        M[rand[0]][rand[1]] = "B"
    return M

def putNumbers(n,M):
    for i in range(n):
        for j in range(n):
            if M[i][j]!="B":
                count = 0
                for c in range(9):
                    if c!=4:
                        x = j + (c%3)-1
                        y = i + (c//3)-1
                        if x<n and x >= 0 and y<n and y>= 0:
                            if M[y][x]=="B":
                                count += 1
                M[i][j] = str(count)
    return M




BOT_PREFIX = ("?", "!")

client = Bot(command_prefix=BOT_PREFIX)




class RandomSlapper(commands.Converter):
    async def convert(self, ctx, argument):
        to_slap = random.choice(ctx.guild.members)
        return '@{0.author} slapped @{1} because *{2}*'.format(ctx, to_slap, argument)


@client.command()
async def slap(ctx, *, reason: RandomSlapper):
    await ctx.send(reason)



@client.command(pass_context=True)
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: User):
    """ Simple kick command """
    await client.kick(member)
    print("kicked" + " " + str(member))


@client.command(name='8ball',
                description="Answers a yes/no question.",
                brief="Answers from the beyond.",
                aliases=['eight_ball', 'eightball', '8-ball'],
                pass_context=True)
async def eight_ball(context):
    possible_responses = [
        'That is a resounding no',
        'It is not looking likely',
        'Too hard to tell',
        'It is quite possible',
        'Definitely',
    ]
    await context.send(random.choice(possible_responses) + ", " + context.message.author.mention)


@client.command()
async def square(context,number: int):
    squared_value = number * number
    await context.send(str(number) + " squared is " + str(squared_value))

@client.command(name="minesweeper",
                description="produces a minesweeper puzzle of nxn with n bombs",
                aliases=["mine_sweeper","msweep"])
async def mineSweeper(context,num: int):
    n = int(num)
    M = [["0" for j in range(n)] for i in range(n)]  # board matrix
    M = randomMatrix(n, M)
    M = putNumbers(n, M)
    for i in range(n):
        line = ""
        for j in range(n):
            line += readNum(M[i][j]) + " "
        await context.send(line)

@client.command(name="chess",
                description="play chess",
                aliases=["c"])
async def chess(context,arg: toUpper):
    if '>' in arg:
        updateChessBoard(arg)
    elif arg=="newgame":
        pass
    elif arg=="ai":
        pass
    elif arg=='p':
        for i in range(8):
            line = ''
            for j in range(8):
                line += CHESSCODE[CHESSDEFAULT[i][j]]
            await context.send(line)
            time.sleep(0.01)
    else:
        for i in range(len(CHESSHELP)):
            await context.send(CHESSHELP[i])

@client.command(name="regional_indicator",
                description="Prints out words",
                aliases=["emojiWrite","regIn","emw"])
async def emojiWrite(context,word):
    word = word.lower().replace("_"," ")
    output = ""
    for letter in word:
        if letter==" ":
            output +=":black_medium_small_square:"
        else:
            output += ":regional_indicator_" + letter + ": "
    await context.send(output)


@client.event
async def on_ready():
    await client.change_presence(activity=Game(name="Ninoh's Tasks"))
    print("Logged in as " + client.user.name)
    print(client.user.id)
    print('------')


@client.command()
async def bitcoin(context):
    url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
    async with aiohttp.ClientSession() as session:  # Async HTTP request
        raw_response = await session.get(url)
        response = await raw_response.text()
        response = json.loads(response)
        await context.send("Bitcoin price is: $" + response['bpi']['USD']['rate'])

@client.command(name="Echo",
                description="Print what you said",
                aliases=["e","E","echo"])
async def echo(context,*,arg):
    await context.send(arg)


@client.command(name="Version",
                description="Prints version of code",
                aliases=["v","ver","version"])
async def version(context):
    await context.send("Version Number: v.1.0.1")

@client.command(name="Eito",
                description="Prints version of code",
                aliases=["eito","ninoh"])
async def eito(context):
    print(context.author.id,"Eito's Id: 270972813739819009")
    if context.author.id=="270972813739819009":
        await context.send("You are my owner")
    else:
        await context.send("You are not Eito")

async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)

print("hello")

client.loop.create_task(list_servers())

f = open("token.txt","r")
token = f.read()
f.close()
client.run(token)
