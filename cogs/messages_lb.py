import discord
from discord.ext import commands, tasks
import json
from datetime import datetime, time, timedelta
import asyncio
import random
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash import cog_ext
from typing import Optional
from discord.ext.commands import MemberConverter
import requests
from paginator import Paginator
from constants import const

mconv = MemberConverter()


class MessageLB(commands.Cog):
    def __init__(self, client):
        self.client = client

        with open("data/message_logs.json", "r") as f:
            self.msg_data = json.load(f)

        if "last_payout" not in self.msg_data.keys():
            self.msg_data["last_payout"] = None

        self.pinged = False
        self.ping_ts = 0

        self.save_data.start()
        self.send_payouts.start() if not const.DEBUG else None
        self.ping.start()
        self.daily_quote.start()
        self.users_in_paginator = {}

    async def icon(self, user):
        return user.avatar_url_as(static_format="png", size=2048)

    async def check(self, member):

        if member.bot:
            return "This is a bot therefore excluded from this feature."
        if str(member.id) not in self.msg_data.keys():
            self.msg_data[str(member.id)] = {
                "last_ts": 0,
                "count": 0,
                "vc_time": 0,
                "last_vs_ts": 0,
                "name": member.name
            }
        return None

    async def get_user(self, id: int = None) -> str:

        await self.client.wait_until_ready()

        if id in self.client.user_cache.keys():
            try:
                return self.client.user_cache[int(id)]
            except KeyError:
                pass

        obj = self.client.guilds[0].get_member(int(id))
        if not obj:
            return f"~~{id}~~"
        else:
            try:
                self.client.user_cache[id] = obj.name
                return obj.name
            except (TypeError, AttributeError):
                return f"~~{id}~~"

    @commands.Cog.listener()
    async def on_message(self, msg):

        if msg.channel.id not in [866526262759129118, 924778031845896252, 926746018140278814, 926751213649817650, 920493973640978432]:
            return

        if msg.author.bot:
            return

        if msg.author.name == "Dyno":
            print(msg.author)
            return

        await self.check(msg.author)

        if self.pinged:
            addon = 2
            if datetime.now().timestamp() - self.ping_ts >= 15*60:
                self.pinged = False
        else:
            addon = 1

        self.msg_data[str(msg.author.id)]["count"] += addon
        self.msg_data[str(msg.author.id)
                      ]["last_ts"] = datetime.now().timestamp()

    @tasks.loop(seconds=10)
    async def save_data(self):

        with open("data/message_logs.json", "w") as f:
            json.dump(self.msg_data, f, indent=2)

        with open("data/payouts.json", "w") as f:
            json.dump(self.client.po_data, f, indent=2)

    @tasks.loop(seconds=10)
    async def send_payouts(self):

        await self.client.wait_until_ready()

        "mon 12:01 AM - 1640563293"
        # 1640563293 + 5*60*60
        # 1643605260

        if "last_payout" in self.msg_data.keys():

            if not self.msg_data["last_payout"]:
                self.msg_data["last_payout"] = 1590811260
        else:
            self.msg_data["last_payout"] = 1590811260

        # curr = datetime.now().timestamp() + 5*60*60
        # if (first < curr) and (first+7*24*60*60 <= curr):
        #     pass

        # if datetime.now().timestamp() >= self.msg_data["last_payout"] + 7*24*60*60:
        if datetime.now() > datetime.fromtimestamp(self.msg_data["last_payout"]) + timedelta(weeks=1):
            data = sorted([[data[0], data[1]] for data in self.msg_data.items(
            ) if data[0] != "last_payout"], key=lambda e: e[1]["count"], reverse=True)[:10]

            payouts = [500000, 400000, 300000, 200000,
                       100000, 80000, 60000, 40000, 20000, 10000]

            guild = self.client.guilds[0]

            ch = guild.get_channel(867247651745038376)

            for _ in range(10):

                if data:
                    try:
                        user_obj = guild.get_member(int(data[_][0])).mention
                    except (TypeError, AttributeError):
                        user_obj = "~~Unknown~~"

                    em = discord.Embed(
                        colro=0x78BB67, description=f"<:Checkmark:886699674277396490> Added <:money:903467440829259796>**{payouts[0]:,}** to {user_obj}'s bank balance.")
                    em.set_author(name="Top 10 Weekly Messagesrs Payout", icon_url=await self.icon(self.client.user))

                    await ch.send(embed=em)

                    try:
                        await self.client.addcoins(int(data[_][0]), payouts[0])
                    except IndexError:
                        continue

                    try:
                        print(
                            f"Added {payouts[0]} coins to {data[_][1]['name'].encode('utf-8')} | {data[_][1]['count']}".encode("utf-8"))
                    except Exception as e:
                        print(e)

                    payouts.pop(0)

            self.client.po_data["count"] += 1
            self.msg_data = {
                "last_payout": datetime.now().timestamp()}

    @tasks.loop(hours=1)
    async def ping(self):
        await self.client.wait_until_ready()

        # if ((datetime.fromtimestamp(datetime.now().timestamp() - 5*60*60).time() >= time(20, 0))) and ((datetime.now().timestamp() - 29*60*60) - datetime.strptime(str(time(20, 0)),"%H:%M:%S") >= 24*60*60):

        if (datetime.now().time() >= time(20, 0)) and (datetime.now().time() < time(21, 0)):

            more_sleep = random.randint(1, 28800)

            await asyncio.sleep(more_sleep)

            msg = "<@&912004965537579049>\nITS A 2X MESSAGE EVENT!\n\nEVERY MESSAGE YOU SEND FOR THE NEXT 15 MINUTES WILL COUNT AS 2!"

            found = False
            for guild in self.client.guilds:
                channel = guild.get_channel(866526262759129118)
                if channel:
                    await channel.send(msg)
                    found = True
                    break

            if not found:
                print("[Message Event]> No channel found.")
            self.ping_ts = datetime.now().timestamp()
            self.pinged = True

    @tasks.loop(hours=24)
    async def daily_quote(self):
        await self.client.wait_until_ready()

        def e():
            e = requests.get("https://zenquotes.io/api/random")

            if e.status_code != 200:

                print("error", e.status_code, e.json())
                return None

            return e.json()
        f = (await self.client.loop.run_in_executor(None, e))

        if not f:
            return

        found = False
        for guild in self.client.guilds:
            ch = guild.get_channel(926742220340625419)
            if ch:
                em = discord.Embed(color=0x00F8EF, description=f[0]["q"])
                em.set_author(name="Inspirational quotes provided by ZenQuotes API", url="https://zenquotes.io/", icon_url=await self.icon(self.client.user))

                await ch.send(embed=em)
                found = True
                break

        if found == False:
            print("[Daily Quote]> No channel found.")

    async def __messages(self, member: discord.Member = None):

        try:
            test = await self.check(member)
        except TypeError:
            test = "`An Unknown Error has occured. Could not get the member object!`"

        try:
            _name = member.name
        except TypeError:
            _name = "~~Unknown~~"

        if test is None:
            ts = f"<t:{int(self.msg_data[str(member.id)]['last_ts'])}:R>" if self.msg_data[str(
                member.id)]['last_ts'] != 0 else "`N/A`"

            em = discord.Embed(
                color=0x00F8EF, description=f"**Count:** {self.msg_data[str(member.id)]['count']}\nLast Message: {ts}")
            em.set_author(name=f"{_name}'s messages stats:", icon_url=await self.icon(self.client.user))

            return em

        else:

            em = discord.Embed(color=0x00F8EF, description=test)
            em.set_author(name=f"Error!", icon_url=await self.icon(self.client.user))

            return em

    async def __top(self, ctx):
        em = discord.Embed(
            color=0x00F8EF, title="Most Active Chatters in Pixels Minecraft Lounge")
        em.set_author(name="\u200b", icon_url=await self.icon(self.client.user))

        # If there are no memebrs with that role, return an embed with the number 0 as the user count.
        if not self.msg_data:

            ad = f"The leaderboard for the biggest chatters in Pixels Minecraft Lounge for week #{self.client.po_data['count']}. The top 10 chatters win cash prizes in the games rooms every week!\n*Messages only count in lounge channels\n\nWeeks end Monday 00:01/12 AM EST and all weekly messages are reset*"
            em.description = ad + "\n\n" + f"`No players yet!`"

            await ctx.send(embed=em)
            return

        if len(self.msg_data.keys()) <= 10:

            data = enumerate(sorted([[data[0], data[1]] for data in self.msg_data.items(
            ) if data[0] != "last_payout"], key=lambda e: e[1]["count"], reverse=True))

            users = ""

            for user in data:
                if user[0] == 0:
                    users += f"🏆 - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 500k"

                elif user[0] == 1:
                    users += f"\n🥈 - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 400k"

                elif user[0] == 2:
                    users += f"\n🥉 - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 300k"

                elif user[0] == 3:
                    users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 200k"

                elif user[0] == 4:
                    users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 100k"

                elif user[0] == 5:
                    users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 80k"

                elif user[0] == 6:
                    users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 60k"

                elif user[0] == 7:
                    users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 40k"

                elif user[0] == 8:
                    users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 20k"

                elif user[0] == 9:
                    users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 10k"

                else:
                    users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages)"

            #  Initiate first embed (if there are less than 10 members for that role, send the embed)
            ad = f"The leaderboard for the biggest chatters in Pixels Minecraft Lounge for week #{self.client.po_data['count']}. The top 10 chatters win cash prizes in the games rooms every week!\n*Messages only count in lounge channels\n\nWeeks end Monday 00:01/12 AM EST and all weekly messages are reset*"
            em.description = ad + "\n\n" + users

            await ctx.send(embed=em)
            return
        # If there are more than 10 members for that role, create paginator and send embeds with 10 memebrs per embed.

        else:
            temp_li = []
            embeds = []
            count = 1
            user_count = 0

            data = sorted([[data[0], data[1]] for data in self.msg_data.items(
            ) if data[0] != "last_payout"], key=lambda e: e[1]["count"], reverse=True)
            total_pages = len(
                data) // 10 if len(data) % 10 == 0 else len(data) // 10 + 1

            for index, key in enumerate(data):  # x == member

                temp_li.append([index+1, key])
                user_count += 1

                if len(temp_li) == 10:

                    users = ""

                    for user in temp_li:
                        if user[0] == 1:
                            users += f"🏆 - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 500k"
                        elif user[0] == 2:
                            users += f"\n🥈 - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 400k"
                        elif user[0] == 3:
                            users += f"\n🥉 - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 300k"
                        elif user[0] == 4:
                            users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 200k"
                        elif user[0] == 5:
                            users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 100k"
                        elif user[0] == 6:
                            users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 80k"
                        elif user[0] == 7:
                            users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 60k"
                        elif user[0] == 8:
                            users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 40k"
                        elif user[0] == 9:
                            users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 20k"
                        elif user[0] == 10:
                            users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages) - <:money:903467440829259796> 10k"
                        else:
                            users += f"\n**{user[0]}.** - **{user[1][1]['name']}** ({user[1][1]['count']} messages)"

                    em = discord.Embed(
                        color=0x00F8EF, title="Most Active Chatters in Pixels Minecraft Lounge")
                    em.set_author(name="\u200b", icon_url=await self.icon(self.client.user))
                    em.set_footer(text=f"{ctx.guild.name} - Page {count}/{total_pages}",
                                  icon_url=str(self.client.user.avatar_url_as(static_format="png", size=2048)))

                    ad = f"The leaderboard for the biggest chatters in Pixels Minecraft Lounge for week #{self.client.po_data['count']}. The top 10 chatters win cash prizes in the games rooms every week!\n*Messages only count in lounge channels\n\nWeeks end Monday 00:01/12 AM EST and all weekly messages are reset*"
                    em.description = ad + "\n\n" + users

                    embeds.append(em)

                    count += 1
                    temp_li = []

                elif user_count == len(data):  # x == members[-1]

                    users = "\n".join(
                        f"**{user[0]}** - **{user[1][1]['name']}** ({user[1][1]['count']} messages)" for user in temp_li)

                    em = discord.Embed(
                        color=0x00F8EF, title="Most Active Chatters in Pixels Minecraft Lounge")
                    em.set_author(name="\u200b", icon_url=await self.icon(self.client.user))
                    em.set_footer(text=f"{ctx.guild.name} - Page {count}/{total_pages}",
                                  icon_url=str(self.client.user.avatar_url_as(static_format="png", size=2048)))

                    ad = f"The leaderboard for the biggest chatters in Pixels Minecraft Lounge for week #{self.client.po_data['count']}. The top 10 chatters win cash prizes in the games rooms every week!\n*Messages only count in lounge channels\n\nWeeks end Monday 00:01/12 AM EST and all weekly messages are reset*"
                    em.description = ad + "\n\n" + users

                    embeds.append(em)
                    count += 1
                    temp_li = []

        await Paginator(embeds, ctx).paginate()

    @cog_ext.cog_slash(name="messages", guild_ids=[865870663038271489], description="Display top messagers or a player's stats", options=[
        create_option(name="player", description="Display a player's messagers",
                      option_type=6, required=False)
    ])
    async def _msgs(self, ctx: SlashContext, player: Optional[discord.Member] = None):

        if player:
            if not isinstance(player, (discord.Member, discord.User)):
                return await ctx.send("Sorry, I could not find that user.", hidden=True)
            await ctx.send(embed=await self.__messages(player))
        else:
            await self.__top(ctx)


def setup(client):
    if not client.debug:
        client.add_cog(MessageLB(client))
