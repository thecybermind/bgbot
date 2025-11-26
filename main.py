import asyncio
import os
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


def get_time():
    return datetime.now(ZoneInfo("Europe/Sofia")).strftime(
        "The time in Bulgaria is now %I:%M %p on %b %d, %Y."
    )


def generate_tts_time():
    # delete TTS file if it exists
    try:
        os.remove(GTTS_FILENAME)
    except:  # pylint: disable=bare-except
        pass

    # generate TTS
    speech = gTTS(text=get_time(), lang="en", tld="us", slow=False)
    speech.save(GTTS_FILENAME)


intents = discord.Intents.default()
# intents.message_content = True
# intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(
    name="bgtime",
    description="What time is it now in Bulgaria?",
    guild=discord.Object(id=DISCORD_GUILDID),
)
async def bgtime(interaction):
    # send response to slash command (only to the user, and do not trigger notification)
    await interaction.response.send_message(get_time(), ephemeral=True, silent=True)

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
        generate_tts_time()

        # get new voice connection for this server (since we just joined)
        voice = discord.utils.get(client.voice_clients, guild=interaction.guild)

        # play TTS to voice chat, and disconnect after
        voice.play(
            discord.FFmpegPCMAudio(GTTS_FILENAME),
            after=lambda e: asyncio.run_coroutine_threadsafe(
                voice.disconnect(), client.loop
            ),
        )


@client.event
async def on_ready():
    # sync command tree with server
    await tree.sync(guild=discord.Object(id=DISCORD_GUILDID))

    # update presence (line of text underneath name in user list)
    await client.change_presence(activity=discord.Game(DISCORD_STATUS))

    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")


# generate_tts_time()

client.run(DISCORD_TOKEN)
