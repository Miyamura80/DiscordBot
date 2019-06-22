import random
import asyncio
import aiohttp
import json
from random import randint
from discord.ext import commands
from discord import Game,Member,Embed,Colour,errors
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

with open("chatFilterList.txt","r") as f:
    bannedWordsPrepro =f.readlines()
bannedWords = [word.lower() for word in bannedWordsPrepro]


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



@client.command(pass_context=True,category="Moderation")
async def kick(ctx, member: Member,reason="<None Specified>"):
    # if "454184393636839426" in [str(role.id) for role in ctx.author.roles]:
    if ctx.message.author.guild_permissions.administrator:
        await ctx.send("**Kicked**: "+str(member.name)+" for: "+reason)
        await member.kick(reason=reason)
    else:
        await ctx.send("Insufficient permissions")

@client.command(pass_context=True,category="Moderation")
async def ban(ctx, member: Member,reason="<None Specified>"):
    # if "454184393636839426" in [str(role.id) for role in ctx.author.roles]:
    if ctx.message.author.guild_permissions.administrator:
        await ctx.send("**Banned**: "+str(member.name)+" for: "+reason)
        await member.ban(reason=reason)
    else:
        await ctx.send("Insufficient permissions")

@client.command(name='banList',
                brief="Shows a list of banned users",
                aliases=['bl', 'banlist', 'BanList'],category="Moderation",pass_context=True)
async def banList(ctx):
    # if "454184393636839426" in [str(role.id) for role in ctx.author.roles]:
    if ctx.message.author.guild_permissions.administrator:
        banned_users = await ctx.guild.bans()
        banList = "**Banned Users:**\n"
        for ban_Entry in banned_users:
            user = ban_Entry.user
            banList += user.name + "#" +user.discriminator + "\n"
        await ctx.send(banList)
    else:
        await ctx.send("Insufficient permissions")

@client.command(category="Moderation",pass_context=True)
async def unban(ctx,member):
    # if "454184393636839426" in [str(role.id) for role in ctx.author.roles]:
    if ctx.message.author.guild_permissions.administrator:
        banned_users = await ctx.guild.bans()
        memberName,memberDiscriminator = member.split("#")
        for ban_entry  in banned_users:
            user = ban_entry.user
            if (user.name,user.discriminator) == (memberName,memberDiscriminator):
                await ctx.guild.unban(user)
                await ctx.send("**Unbanned user**: {}".format(user.mention))
                return
    else:
        await ctx.send("Insufficient permissions")

@client.command(category="Moderation",pass_context=True)
async def clear(ctx,num=100):
    if ctx.message.author.guild_permissions.administrator:
        channel = ctx.guild.channel
        messages = []
        async for message in client.logs_from(channel,limit=int(num)):
            messages.append(message)
        await client.delete_messages(messages)

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

@client.command(name="EmojiWrite",
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

@client.event
async def on_message(msg):
    if msg.author == client.user or msg.author.bot:
        return
    contents = msg.content.split(" ")
    print(contents)
    for word in contents:
        if word.lower() in bannedWords:
            if not msg.author.guild_permissions.administrator:
                try:
                    await msg.channel.send("That word is banned")
                    await msg.delete()
                except errors.notFound:
                    return
    await client.process_commands(msg)


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
    await context.send("Version Number: v.1.0.2")

@client.command(name="Eito",
                description="Prints version of code",
                aliases=["eito","ninoh"])
async def eito(context):
    if str(context.author.id)=="270972813739819009":
        await context.send("You are my owner")
    else:
        await context.send("You are not Eito")

@client.command(name="MyRole",
                description="Prints out role of a user",
                aliases=["myRole","myr","myrole"])
async def myRole(context):
    roleList = [str(role.name) for role in context.author.roles][1:]
    if len(roleList)==0:
        await context.send("You do not have a role" + context.message.author.mention)
    else:
        roles = ""
        for i in range(len(roleList)):
            roles += roleList[i]
            if i!=len(roleList)-1:
                roles += ", "
        await context.send("You roles are: "+roles+ " "+context.message.author.mention)

@client.command()
async def showEmbed(ctx):
    embed = Embed(
        title="Here's a kewl title",
        description="This is a description baby",
        colour= Colour.blue()

    )
    embed.set_footer(text="this is a footer")
    embed.set_image(url="https://i.ytimg.com/vi/ezs7S9a_bNI/maxresdefault.jpg")
    embed.set_thumbnail(url="https://assets3.thrillist.com/v1/image/2813543/size/gn-gift_guide_variable_c.jpg")
    embed.set_author(name="Eimi",icon_url="https://vignette.wikia.nocookie.net/vocaloid/images/8/85/Eve_icon1.jpg/revision/latest?cb=20180618163614")
    embed.add_field(name="Field Name",value="Field value",inline=True)
    embed.add_field(name="Field Name", value="Field value", inline=False)
    await ctx.send(embed=embed)

@client.command(aliases=["botinfo","BotInfo"])
async def botInfo(ctx):
    embed = Embed(
        title="Lappy",
        description="Bot built to manage your server and have fun",
        colour=Colour.blue()
    )
    embed.set_footer(text="Lappy is a digital construction of Eimi's PC as a bot")
    embed.set_thumbnail(url="https://i.ytimg.com/vi/ezs7S9a_bNI/maxresdefault.jpg")
    embed.add_field(name="Owner", value="Eimi#8826", inline=True)
    embed.add_field(name="Version", value="1.6.0", inline=True)
    embed.add_field(name="Language", value="Python", inline=True)
    embed.add_field(name="Commands", value="x number", inline=True)
    embed.add_field(name="Hosting", value="Raspberry Pi 2 B at my house", inline=True)
    await ctx.send(embed=embed)

@client.command()
async def commands(ctx):
    embed = Embed(
        title="__**Commands**__",
        description="All commands are executed with prefix `!` (e.g. `!botinfo`)",
        colour=Colour.blue()
    )
    embed.set_footer(text="Lappy is a digital construction of Eimi's PC as a bot")
    embed.set_thumbnail(url="https://i.ytimg.com/vi/ezs7S9a_bNI/maxresdefault.jpg")
    embed.add_field(name="➤Info", value="`!botinfo`", inline=False)
    embed.add_field(name="➤Utility", value="`!emw`", inline=False)
    embed.add_field(name="➤Games", value="`!minesweeper`", inline=False)
    embed.add_field(name="➤Moderation", value="`!kick`,`!ban`,`!unban`,`!banlist`", inline=False)
    embed.add_field(name="➤Settings", value="None atm", inline=True)
    await ctx.send(embed=embed)


@client.command()
async def source(ctx):
    await ctx.send("https://github.com/Miyamura80/DiscordBot")


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)



client.loop.create_task(list_servers())

f = open("token.txt","r")
token = f.read()
f.close()
client.run(token)
