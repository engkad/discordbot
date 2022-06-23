# Discord bot, created by engkad. Apologies for the bad programming, my python is pretty rusty.

import os
import discord
import random

from dotenv import load_dotenv
from discord.ext import commands
from discord import FFmpegPCMAudio
from pathlib import Path
from discord import PCMVolumeTransformer

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
playbackVolume = 1.0
ErrorMessage = 'Error!'
quietMode = False
is_playing = False
randomPick = False
filename = False
pathToClips = '/path/to/clipsDirectory'

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@bot.command(help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(help='Joins bot to voice', pass_context=True)
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.send("joined the channel")
    else:
        await ctx.send(ErrorMessage)

@bot.command(help='Disconnects bot from voice', pass_context=True)
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("left the channel")
    else:
        await ctx.send(ErrorMessage)

@bot.command(pass_context=True)
async def pr(ctx):
    await play(ctx,'random')

@bot.command(pass_context=True)
async def pl(ctx):
    await play(ctx,'list')

@bot.command(help='Plays <filename>.wav', pass_context=True,aliases=['p'])
async def play(ctx,arg):
    if (ctx.author.voice):
        path = Path(pathToClips).resolve()
        if arg.lower() == 'list':
            files = os.listdir(path)
            # I have all my audio clips in .wav, you can change this and all other mentions to another format if desired
            matchers = ['.wav']
            wavs = [s for s in files if any(xs in s for xs in matchers)]
            # I have no idea how this^ works but it does
            separator = ', '
            text = separator.join(wavs)
            msg = '```'+str(text)+'```'
            await ctx.send(msg)
            return

        # To see whether clip to play should be random or the argument
        elif arg.lower() == 'random':
            global randomPick
            files = os.listdir(path)
            matchers = ['.wav']
            wavs = [s for s in files if any(xs in s for xs in matchers)]
            # print(wavs)
            randomPick = random.choice(wavs)
            print(randomPick)
            sourcefile = str(path)+'/'+randomPick
        else:
            global filename
            filename = arg.lower()+'.wav'
            sourcefile = str(path)+'/'+filename
            if os.path.isfile(sourcefile):
                pass
            else:
                await ctx.send("File "+filename+" does not exist.")
                return
            
        
        if ctx.guild.voice_client:
            pass
        else:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        channel = ctx.message.author.voice.channel
        voice = ctx.guild.voice_client
        
        try:
            voice.play(FFmpegPCMAudio(sourcefile))
        except:
            voice = discord.utils.get(bot.voice_clients,guild=ctx.guild)
            voice.stop()
            voice.play(FFmpegPCMAudio(sourcefile))
        voice.source = PCMVolumeTransformer(voice.source)
        voice.source.volume = playbackVolume

        # Echo name of file played
        if quietMode == False:
            if filename:
                name = filename
            if randomPick:
                name = randomPick
            await ctx.send('Playing '+name+' at volume '+str(playbackVolume))

    else:
        await ctx.send(ErrorMessage+' User not in voice channel')

@bot.command(help='Stops playback', pass_context=True)
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients,guild=ctx.guild)
    voice.stop()

@bot.command(help='Set quiet mode with on/off', pass_context=True)
async def quiet(ctx,arg):
        arg = arg.lower()
        global quietMode
        if arg == 'on':
            quietMode = True
            await ctx.send('Quiet mode on')
        elif arg == 'off':
            quietMode = False
            await ctx.send('Quiet mode off')
        else:
            await ctx.send('Set quiet mode with on or off')
    

@bot.command(help='Changes float volume of playback', pass_context=True,aliases=['vol'])
async def volume(ctx,arg=None):
    global playbackVolume
    if arg == None:
        await ctx.send('Volume is set to '+str(playbackVolume))
        return
    if float(arg) > 0 and float(arg) <= 1:
        playbackVolume = float(arg)
        await ctx.send('Volume set to '+str(playbackVolume))
    else:
        await ctx.send('Enter a float value between 0 and 1')

@bot.command(help='Checks bot latency')
async def ping(ctx):
    latency = bot.latency
    latency = latency*1000
    latency = int(round(latency))
    await ctx.send(str(latency)+' ms')

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    if 'STRING' in message.content.lower():
        await message.channel.send('RESPONSE')

    # This is needed so that the bot processes commmands instead of only responding to messages
    await bot.process_commands(message)


bot.run(TOKEN)
