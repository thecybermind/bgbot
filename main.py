import os
from datetime import datetime

import discord
from discord.ext import commands
from gtts import gTTS

from config import discord_config

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(
    command_prefix="/",
    description="cybermind's BG bot",
    intents=intents,
)


def get_time():
    return datetime.now().strftime("The time in Bulgaria is now %H:%M:%S on %b %d, %Y.")


@bot.event
async def on_ready():
    # Tell the type checker that User is filled up at this point
    assert bot.user is not None

    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.command()
async def bgtime(ctx):
    connected = ctx.author.voice
    if not connected:
        await ctx.send(get_time())
    else:
        await connected.channel.connect()
        # ctx.voice_client.stop()

        phrase_there = os.path.isfile("phrase.mp3")
        if phrase_there:
            os.remove("phrase.mp3")

        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        speech = gTTS(text=get_time(), lang="en", slow=False)
        speech.save("phrase.mp3")
        voice.play(discord.FFmpegPCMAudio("phrase.mp3"))

        await voice.disconnect()


bot.run(discord_config["TOKEN"])
