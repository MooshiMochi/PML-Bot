"""
https://github.com/PrismarineJS/mineflayer/tree/master/examples/python

pip install discord-py-slash-command==3.0.1a

Timnoot / Custom Bot Commission Discord-Minecraft
"""

import mimetypes
import os
import json
import asyncio

import aiohttp
import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from dotenv import load_dotenv
from constants import const
import discord_slash
from discord_slash.error import AlreadyResponded
from discord_slash import SlashContext
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
prefix = "?"
debug = False

if debug:
    prefix = "!"
    TOKEN = os.getenv("DISCORD_TEST_TOKEN")

apikey = os.getenv("HYPIXEL_API_KEY")
unbelievaboattoken = os.getenv("UNBELIEVABOAT_TOKEN")
guild_id = 865870663038271489

if not "logs" in os.listdir():
    os.system("mkdir logs")


class PixelSlashContext(SlashContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def embed(self, embed, *, footer=None):

        if footer is None:
            footer = "PML"
        embed.set_footer(icon_url=self.bot.png,
                         text=f"Pixel Master | {footer}")
        embed.timestamp = datetime.utcnow()

        try:
            if self.deferred:
                if not self.responded:
                    return await self.send(embed=embed, hidden=self._deferred_hidden)

                return await self.channel.send(embed=embed)
            if not self.responded:
                return await self.send(embed=embed)

            try:
                return await self.channel.send(embed=embed)
            except AlreadyResponded:
                guild = self.bot.get_guild(self.guild_id)
                ch = guild.get_channel(self.channel_id)
                return await ch.send(embed=embed)
        except discord.HTTPException as e:
            raise e


discord_slash.context.SlashContext = PixelSlashContext


class MyClient(commands.Bot):
    # noinspection PyUnresolvedReferences

    failure = 0xff0000
    success = 0x00ff00

    async def close(self):
        await self.session.close()
        await super().close()

    async def getuuid(self, name):
        async with client.session.get(f"https://api.mojang.com/users/profiles/minecraft/{name}") as f:
            if f.status == 200:
                res = await f.json()
                return res["id"]
            else:
                return f.status

    async def getplayerdata(self, uuid):
        async with client.session.get(f"https://api.hypixel.net/player?key={apikey}&uuid={uuid}") as f:
            if f.status == 200:
                res = await f.json()
                return res["player"]
            else:
                return f.status

    async def getname(self, uuid):
        async with client.session.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}") as r:
            if r.status == 200:
                return (await r.json())["name"]
            else:
                return r.status

    async def isonline(self, uuid):
        async with client.session.get(f"https://api.hypixel.net/player?key={apikey}&uuid={uuid}") as f:
            if f.status == 200:
                res = await f.json()
                return res["player"]["lastLogin"] > res["player"]["lastLogout"]
            else:
                return f.status

    async def addcoins(self, userid, amount):

        if amount < 0:
            async with client.session.get(f"https://unbelievaboat.com/api/v1/guilds/{guild_id}/users/{userid}", headers={"Authorization": unbelievaboattoken}) as r:
                if r.status == 200:
                    r = await r.json()
                    if r["bank"] < (amount/-1):
                        return "You are too poor to afford a private chat."
                else:
                    print(r.status, await r.json())
                    return

        headers = {"Authorization": unbelievaboattoken,
                   'Accept': 'application/json'}
        async with client.session.patch(f"https://unbelievaboat.com/api/v1/guilds/{guild_id}/users/{userid}",
                                        headers=headers,
                                        json={"bank": amount, "reason": "Guessed the riddle correct."}) as f:
            try:
                data = await f.json(content_type="application/json")
                return data
            except Exception as e:
                print("New exception in addcoins:\n", e)
                return None


client = MyClient(command_prefix=commands.when_mentioned_or(prefix), case_insensitive=True,
                  allowed_mentions=discord.AllowedMentions(everyone=False), intents=discord.Intents.all(),
                  help_command=None)

slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True)

client.session = None

client.debug = debug

client.user_cache = {}

with open("data/payouts.json", "r") as f:
    client.po_data = json.load(f)

if "count" not in client.po_data.keys():
    client.po_data["count"] = 1

# client.bot = None


@tasks.loop(count=1)
async def init_session():
    client.session = aiohttp.ClientSession()
    print("Session: Successful")

init_session.start()

files = []
content = ""
for ext in const.exts:
    try:
        client.load_extension(ext)
        files.append({'name': ext, 'success': True})
    except Exception as E:
        files.append({'name': ext, 'success': False})
        print(f'Something is wrong: {E}')

for f in range(len(files)):
    if files[f]['success'] == True:
        content += f"Filename: {files[f]['name']} Successful\n"
    elif files[f]['success'] == False:
        content += f"Filename: {files[f]['name']} Failed\n"


@client.command()
async def reload(ctx, filename):
    if ctx.author.id not in [186896273742233600, 383287544336613385]:
        return await ctx.send("You're not allowed to run this command.")

    if filename == "mcd":
        filename = "mc_madness"

    if f"{filename}.py" not in os.listdir("cogs"):
        text = '\n'.join(
            [f'[{x}]' for x in os.listdir('cogs') if x.endswith('.py')])
        return await ctx.send(f"```ini\n{text}\n```")
    try:
        client.unload_extension(f"cogs.{filename}")
        client.load_extension(f"cogs.{filename}")
        return await ctx.send(f"Reloaded **{filename}**.")
    except Exception as e:
        await ctx.send(f"```yaml\n{e}\n```"[-1500:])


@client.command()
async def load(ctx, filename):
    if ctx.author.id not in [186896273742233600, 383287544336613385]:
        return await ctx.send("You're not allowed to run this command.")

    if filename == "mcd":
        filename = "mc_madness"

    if f"{filename}.py" not in os.listdir("cogs"):
        text = '\n'.join(
            [f'[{x}]' for x in os.listdir('cogs') if x.endswith('.py')])
        return await ctx.send(f"```ini\n{text}\n```")
    try:
        if filename == "mcd":
            filename = "mc_madness"
        client.load_extension(f"cogs.{filename}")
        return await ctx.send(f"Loaded **{filename}**.")
    except Exception as e:
        if len(str(e)) >= 1500:
            e = e[-1500:]
        await ctx.send(f"```yaml\n{e}\n```"[-1500:])


@client.event
async def on_ready():
    # os.system("clear") # You are welcome c: - Mooshi
    print("Bot is online.\n")
    print(content)

client.run(TOKEN)

loop = asyncio.get_event_loop()
loop.set_debug(True)
loop.create_task(client.start(TOKEN))
loop.run_forever()
