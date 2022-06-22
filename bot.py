from datetime import datetime
import time
import discord
import os
from dotenv import load_dotenv
from dateutil.parser import parse, ParserError

from tzdata import *


load_dotenv()
bot = discord.Bot(debug_guilds=[987784828512534538])


def generate_response_message(time_orig: datetime, tz_orig: str):
    time_aware = time_orig.replace(tzinfo=TZINFOS[tz_orig])
    ts = get_timestamp_from_datetime(time_aware)
    return f"{time_aware.strftime(f'%{STRFTIME_NONZERO_PAD_CHAR}I:%M %p %Z')} is {ts} for you."


def get_timestamp_from_datetime(dt: datetime):
    return f'<t:{int(dt.timestamp())}:T>'


class TimeZoneView(discord.ui.View):
    def __init__(self, *items, timeout=180, t: datetime, isdst: bool):
        super().__init__(*items, timeout=timeout)
        self.time = t
        self.isdst = isdst

    @discord.ui.button(label="US pacific")
    async def p_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        tz = "PDT" if self.isdst else "PST"
        msg = generate_response_message(self.time, tz)
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(label="US mountain")
    async def m_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        tz = "MDT" if self.isdst else "MST"
        msg = generate_response_message(self.time, tz)
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(label="US central")
    async def c_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        tz = "CDT" if self.isdst else "CST"
        msg = generate_response_message(self.time, tz)
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(label="US eastern")
    async def e_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        tz = "EDT" if self.isdst else "EST"
        msg = generate_response_message(self.time, tz)
        await interaction.response.send_message(msg, ephemeral=True)


@bot.message_command(name="Translate time")
async def translate_time(ctx: discord.ApplicationContext, message: discord.Message):
    try:
        parsed_datetime = parse(message.content.upper(),
                                fuzzy=True, tzinfos=TZOFFSETS)
        if not parsed_datetime.tzinfo:
            isdst = time.localtime().tm_isdst
            print(
                f'no timezone detected, sending time zone selector for {ctx.user.name} ({ctx.user.id=}), assuming {isdst=}')
            await ctx.respond(f"I can't tell what time zone {message.author.name} is in.",
                              view=TimeZoneView(t=parsed_datetime, isdst=isdst), ephemeral=True)
            return
        result = generate_response_message(
            parsed_datetime, parsed_datetime.tzname())
    except ParserError:
        result = "Couldn't find a time in that message."
    await ctx.respond(result, ephemeral=True)


@bot.event
async def on_ready():
    print(f"{bot.user} is online")


bot.run(os.environ['TOKEN'])
