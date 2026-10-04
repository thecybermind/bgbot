import asyncio
import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from gtts import gTTS

from config import discord_config


DISCORD_TOKEN = discord_config.get("TOKEN", "")
DISCORD_GUILDID = discord_config.get("GUILDID", 0)
DISCORD_STATUS = discord_config.get("STATUS", "")
GTTS_FILENAME = discord_config.get("GTTS_FILENAME", "phrase.mp3")


def get_time_bg():
    now = datetime.now(ZoneInfo("Europe/Sofia"))
    return now.strftime("The time in Bulgaria is now %I:%M %p on %b %d.")


def get_time_bg_bg():
    months = [
        "месец",
        "януари",
        "февруари",
        "март",
        "април",
        "май",
        "юни",
        "юли",
        "август",
        "септември",
        "октомври",
        "ноември",
        "декември",
    ]
    now = datetime.now(ZoneInfo("Europe/Sofia"))
    return now.strftime(f"В момента в България е %H:%M на %d {months[now.month]}.")


def get_time_md():
    now = datetime.now(ZoneInfo("America/New_York"))
    timestr = now.strftime("%I:%M %p on %b %d")
    msg = f"Another pony was struck on Assateague at {timestr}."
    smsg = f"Another pony was struck on Ass-uh-teeg at {timestr}."
    return msg, smsg


def get_time_nc():
    now = datetime.now(ZoneInfo("America/New_York"))
    return now.strftime(
        "The time in North Carolina is now %I:%M %p on %b %d. "
        "Please take your shirt off and swing it round your head like a helicopter."
    )


def get_time_tx():
    now = datetime.now(ZoneInfo("America/Chicago"))
    timestr = now.strftime("%I:%M %p on %b %d")
    msg = f"The stars at {timestr} are big and bright, deep in the heart of Texas."
    smsg = f"The stars at {timestr} are big and bright. . Deep in the heart of Texas."
    return msg, smsg


def get_time_nm():
    now = datetime.now(ZoneInfo("America/Boise"))
    return now.strftime("The aliens probed my anus at %I:%M %p on %b %d in New Mexico.")


def get_art_bp():
    systolic = random.randint(95, 145)
    diastolic = random.randint(65, 100)
    return f"Art's blood pressure is currently {systolic} over {diastolic}."


def generate_tts_time(text, lang="en", tld="us"):
    # delete TTS file if it exists
    try:
        os.remove(GTTS_FILENAME)
    except:  # pylint: disable=bare-except
        pass

    slow = False
    if lang == "bg":
        slow = True
    # generate TTS
    speech = gTTS(text=text, lang=lang, tld=tld, slow=slow)
    speech.save(GTTS_FILENAME)


intents = discord.Intents.default()
# intents.message_content = True
# intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def do_time_cmd(interaction, msgs, lang="en", tld="us"):
    if not msgs:
        return
    # if msgs is a tuple or list, split them out into msg and speechmsg
    if type(msgs) in [list, tuple]:
        msg, speechmsg = msgs
    # otherwise, it's just 1 message to use for both
    else:
        msg = msgs
        speechmsg = msgs

    # send response to slash command (only to the user, and do not trigger notification)
    await interaction.response.send_message(msg, ephemeral=True, silent=True)

    # get active voice connection for this server
    voice = discord.utils.get(client.voice_clients, guild=interaction.guild)

    # if already in a voice channel or talking, cancel
    if voice or (voice and voice.is_playing()):
        return

    # is the user who did the command in a voice channel?
    connected = interaction.user.voice
    if connected:
        # join the channel
        await connected.channel.connect()

        # get TTS
        generate_tts_time(speechmsg, lang, tld)

        # get new voice connection for this server (since we just joined)
        voice = discord.utils.get(client.voice_clients, guild=interaction.guild)

        # play TTS to voice chat, and disconnect after
        voice.play(
            discord.FFmpegPCMAudio(GTTS_FILENAME),
            after=lambda e: asyncio.run_coroutine_threadsafe(
                voice.disconnect(), client.loop
            ),
        )


@tree.command(
    name="bgtime",
    description="What time is it now in Bulgaria?",
    guild=discord.Object(id=DISCORD_GUILDID),
)
async def bgtime(interaction):
    await do_time_cmd(interaction, get_time_bg())


@tree.command(
    name="bgtimebg",
    description="Колко е часът в България в момента?",
    guild=discord.Object(id=DISCORD_GUILDID),
)
async def bgtimebg(interaction):
    await do_time_cmd(interaction, get_time_bg_bg(), "bg", "bg")


@tree.command(
    name="bgtimemd",
    description="What time is it now in Maryland?",
    guild=discord.Object(id=DISCORD_GUILDID),
)
async def bgtimemd(interaction):
    await do_time_cmd(interaction, get_time_md())


@tree.command(
    name="bgtimenc",
    description="What time is it now in North Carolina?",
    guild=discord.Object(id=DISCORD_GUILDID),
)
async def bgtimenc(interaction):
    await do_time_cmd(interaction, get_time_nc())


@tree.command(
    name="bgtimetx",
    description="What time is it now in Texas?",
    guild=discord.Object(id=DISCORD_GUILDID),
)
async def bgtimetx(interaction):
    await do_time_cmd(interaction, get_time_tx())


@tree.command(
    name="bgtimenm",
    description="What time is it now in New Mexico?",
    guild=discord.Object(id=DISCORD_GUILDID),
)
async def bgtimenm(interaction):
    await do_time_cmd(interaction, get_time_nm())


@tree.command(
    name="artbp",
    description="What is Art's current BP?",
    guild=discord.Object(id=DISCORD_GUILDID),
)
async def artbp(interaction):
    await do_time_cmd(interaction, get_art_bp())


@client.event
async def on_ready():
    # sync command tree with server
    await tree.sync(guild=discord.Object(id=DISCORD_GUILDID))

    # update presence (line of text underneath name in user list)
    await client.change_presence(activity=discord.Game(DISCORD_STATUS))

    # seed prng
    random.seed()

    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")


client.run(DISCORD_TOKEN)
