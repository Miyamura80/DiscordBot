import random
import asyncio
import aiohttp
import json
from random import randint
from discord.ext import commands,tasks
from discord import Game,Member,Embed,Colour,errors
from discord.ext.commands import Bot
from itertools import cycle
import time
import discord
import youtube_dl
from async_timeout import timeout

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

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

ytdl_format_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'default_search': 'ytsearch',
    'noplaylist': True,
    "forcethumbnail": True,
    "writethumbnail": True,

}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        #return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)




statusCycle = cycle(["with Ninoh's tasks","with server managament",
                     "with minesweeper puzzles","Echo","Music"
                     ,"Your soul"])


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




class RandomSlapper(commands.Converter):
    async def convert(self, ctx, argument):
        to_slap = random.choice(ctx.guild.members)
        return '@{0.author} slapped @{1} because *{2}*'.format(ctx, to_slap, argument)

#CLASS ISN'T USED
class MusicPlayer:
    def __init__(self,ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        self._cog  = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.now_playing = None
        self.volume = 0.5
        self.current = None

    async def player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()
            try:
                async with timeout(300):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self.guild)
            if not isinstance(source,YTDLSource):
                try:
                    source = await YTDLSource.regather_stream(source,loop=self.bot.loop)
                except Exception as e:
                    await self.channel.send("There was an error processing your song. \n {}".format(e))
                    continue
            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(f'**Now Playing:** `{source.title}` requested by '
                                               f'`{source.requester}`')
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self,guild):
        self.bot.loop.create_task(self._cog.cleanup(guild))

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self,guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self,ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            pass

    @commands.command(aliases=["play","yt"])
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""
        async with ctx.typing():
            MusicPlayer = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            guildName = ctx.guild
            authorName = ctx.author

            ctx.voice_client.play(MusicPlayer, after=lambda e: print('Player error: %s' % e) if e else None)

        embed = Embed(
            title="**Now playing:** {}".format(MusicPlayer.title),
            description="**Requested by:** {0} \n **Server:** {1}".format(authorName.mention,guildName),
            colour=Colour.blue()

        )
        embed.set_footer(text="Lappy is a digital construction of Eimi's PC as a bot")
        embed.set_thumbnail(url="https://assets3.thrillist.com/v1/image/2813543/size/gn-gift_guide_variable_c.jpg")
        embed.set_author(name="Eimi",
                         icon_url="https://vignette.wikia.nocookie.net/vocaloid/images/8/85/Eve_icon1.jpg/revision/latest?cb=20180618163614")
        #Add url of music video
        # embed.add_field(name="URL:", value=MusicPlayer.url, inline=True)
        await ctx.send(embed=embed)


    @commands.command(aliases=["v"])
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()


    @commands.command()
    async def pause(self,ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send("Currently not playing anything!",delete_after=20)
        elif vc.is_paused():
            return
        vc.pause()
        await ctx.send("{} paused the song".format(ctx.author))

    @commands.command()
    async def resume(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send("Currently not playing anything!", delete_after=20)
        elif not vc.is_paused():
            return
        vc.resume()
        await ctx.send("{} resumed the song".format(ctx.author),delete_after=20)

    @commands.command()
    async def skip(self,ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send("Currently not playing anything!", delete_after=20)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send("{} skipped the song".format(ctx.author))


    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.",delete_after=20)
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)

BOT_PREFIX = ("?", "!")

client = Bot(command_prefix=BOT_PREFIX)
# client.remove_command("help")

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
        await ctx.send("Insufficient permissions",delete_after=20)

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
        await ctx.send("Insufficient permissions",delete_after=20)

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
        await ctx.send("Insufficient permissions",delete_after=20)

@client.command(category="Moderation",pass_context=True)
async def clear(ctx,num=5):
    num += 1
    if ctx.message.author.guild_permissions.administrator:
        await ctx.channel.purge(limit=num)

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
async def emojiWrite(context,*,word):
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
    change_Status.start()
    print("Logged in as " + client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(msg):
    if msg.author == client.user or msg.author.bot:
        return
    contents = msg.content.split(" ")
    with open("chatFilterList.txt", "r") as f:
        bannedWordsPrepro = f.readlines()
    bannedWords = [word.lower() for word in bannedWordsPrepro]
    for word in contents:
        if word.lower() in bannedWords:
            if not msg.author.guild_permissions.administrator:
                try:
                    await msg.channel.send("That word is banned")
                    await msg.delete()
                except errors.notFound:
                    return
    await client.process_commands(msg)

@client.event
async def on_member_join(member):
    embed = Embed(
        title="Hello!",
        description="Hello. My name is Lappy and I am your server management bot!",
        colour=Colour.from_rgb(32, 244, 0)
    )
    embed.set_footer(text="Lappy is a digital construction of Eimi's PC as a bot")
    embed.set_thumbnail(url="https://i.ytimg.com/vi/ezs7S9a_bNI/maxresdefault.jpg")
    embed.add_field(name="Features", value="I'm here to filter any bad language and keep order in this server.\nI can also generate minesweeper puzzles and play games with you when you are bored.",
                    inline=False)
    embed.add_field(name="Getting started", value="Since I am a bot, I'm not able to get you up to speed right away.\n Please mention the administrator to get started!."
                    , inline=False)
    embed.add_field(name="Once you're in the server",
                    value="Type !commands to get a list of commands"
                    , inline=False)
    await member.send(embed=embed)

# @client.event
# async def on_command_error(ctx,error):
#     if isinstance(error,discord.commandNotFound):
#         await ctx.send("The command does not exist!")
#     elif isinstance(error,discord.MissingRequiredArgument):
#         await ctx.send("Please pass the relevant argument after the command")

@tasks.loop(minutes=10)
async def change_Status():
    await client.change_presence(activity=discord.Game(next(statusCycle)))


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

@client.command(name="filterList",description="Lists the words that are filtered by the bot",
                aliases=["fList","filterlist","FilterList"])
async def chatFilterList(ctx):
    with open("chatFilterList.txt", "r") as f:
        bannedWordsPrepro = f.readlines()
    bannedWords = [word.lower() for word in bannedWordsPrepro]
    result = ""
    for word in bannedWords:
        result += word+"\n"
    await ctx.send(result)

@client.command(name="Ping",
                description="Tells you your latency to the server",
                aliases=["ping"])
async def ping(context):
    await context.send("Pong! Your latency is: "+str(round(client.latency*1000))+"ms")

@client.command(name="Version",
                description="Prints version of code",
                aliases=["ver","version"])
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
        colour=Colour.from_rgb(254,33,98)
    )
    embed.set_footer(text="Lappy is a digital construction of Eimi's PC as a bot")
    embed.set_thumbnail(url="https://i.ytimg.com/vi/ezs7S9a_bNI/maxresdefault.jpg")
    embed.add_field(name="Owner", value="Eimi#8826", inline=True)
    embed.add_field(name="Version", value="1.6.0", inline=True)
    embed.add_field(name="Language", value="Python", inline=True)
    embed.add_field(name="Source", value="https://github.com/Miyamura80/DiscordBot", inline=True)
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
async def join(ctx):
    """Joins a voice channel"""
    channel = ctx.message.author.voice.channel
    if channel is None:
        await ctx.send("You are not in a voice channel",delete_after=20)
        return
    await channel.connect()

client.loop.create_task(list_servers())

f = open("token.txt","r")
token = f.read()
f.close()
client.add_cog(Music(client))
client.run(token)
