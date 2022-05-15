"""
https://github.com/PrismarineJS/mineflayer/tree/master/examples/python


Timnoot / Custom Bot Commission Discord-Minecraft

Ingame Commands:

    1. !help. To execute this command a player in the housing may type in chat !help (request) or !Help (request) and
    this command will send an embedded message to a discord channel (#help-requests) only jr staff, staff, sr staff, and up may see.
    The format for the embed is:

    Help Request

    User: (Player name here)

    Request: (Request Here)

    React with <:Checkmark:886699674277396490> to head to this person. React with <:no:886699710193238046> to remove this help request and mute the player.
    If the staff reacts with checkmark the in-housing bot will execute /tp (staff name) (player requesting helps' name)
    If the staff reacts with no/x the in-housing bot will execute /h mute (player requesting helps' name) and remove the
    embedded message and replace it with Player (player requesting helps name)'s help request has been deleted by staff member (staff member name here)
    because it did not follow the format or was a troll request. The request deleted was: (request here) in a seperate channel, #help-logs

    2. !skip. Similar to help, to execute this command a player will do !skip or !Skip and this will send an embedded message to the channel (#skips) with the format:

    Skip Request

    User: (username here)

    # of skips used already:

    React with <:Checkmark:886699674277396490> to head to this person and give them a skip. React with <:no:886699710193238046> to remove this skip request and decline it because they have already used 3 skips.
    If the staff reacts with checkmark the in-housing bot will execute /tp (staff name) (player requesting helps' name)
     to give the player a skip and the embedded skip message will delete and post in #skip-logs with (Skip Completed! Username: # of skips already used: Staff Member responsible:)

    3. !cookies. When a player types !cookies or !Cookies in the housing chat this bot will detect if the player sending the command has given the housing cookies.
    You can check this with the hypixel api.
    If they have given cookies, it will tp them to a set of coordinates (a place with exclusive items for cookie-givers). If not, then it will not teleport the player/do anything.
    when they run !cookies it should give them -1 skip if they havent used the cmd before
    so naturally they get 1 free skip to use
    then an extra skip to use if they get a riddle or give cookies


    4. Riddle Games Feature. This feature is a bit complicated, so I will explain this like so:
    Every 5 minutes the bot will send a message into the chat, a random riddle that players can complete for a bonus.
    An example riddle will be: [RIDDLE] Answer the following riddle for a Free Skip! How many dogs does it take to unscrew a lightbulb?
    Now let's say the answer to this is 18. The first player to type 18 in the chat will win and their skip # will be moved down, so if they already used 3 skips it'll be moved to 2, if they're at 0 and have used no skips then -1 and so on.
    Once a player wins, the bot will say in the chat Congratulations (player_name)! You won the riddle. Use !skip to use your free skip!

Discord commands:
    1.
    All chat message's will be send over to the discord
    then staff should be able to do a command
    !skips add (player name) number
    that adds an extra skip manually

    2. !verify minecraftname This command will use the hypixel api to link discord accounts to minecraft accounts for usage of commands. It will also give a verified role




Notes:
    Hosting supplied by customer.

"""

import asyncio
from datetime import datetime
import json
import random as rand2
from random import choice, shuffle, random, randint

import discord
from discord.ext import commands
from discord.ext import tasks
from discord_slash import cog_ext
from discord.ext.commands import MemberConverter
from discord_slash.context import ComponentContext, SlashContext
from discord_slash.model import ButtonStyle
from discord_slash.utils import manage_components
from discord_slash.utils.manage_commands import create_option

from paginator import Paginator

mconv = MemberConverter()


class CrCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.run = True
        self.checkmark = "<:Checkmark:886699674277396490>"
        self.no = "<:no:886699710193238046>"
        self.is_riddle_guessed1 = False
        self.curr_riddle = ["", "aerhagj33££!34$$bear134hthh[}{ajwhd[]9a}_--=-#~jkwnanjavOKEadk:!@!"]
        self.last_used_riddle_category = "None"
        self.used_riddles = []
        self.add_in_progress = False
        self.remove_in_progress = False
        self.switchvar = True
        self.last_channel_riddle = 0
        self.random_win = 500
        self.users_in_paginator = {}
        self.my_on_ready.start()
        self.clear_user_cache.start()

    @tasks.loop(count=1)
    async def my_on_ready(self):
        await self.client.wait_until_ready()

        self.guild = self.client.get_guild(865870663038271489)

        self.generalchannels = [self.guild.get_channel(866526262759129118)]
        self.riddle.start()
        self.run = False

        with open("data/riddles.json", "r") as f:
            self.cGamesData = json.load(f)


    async def get_user(self, id:int=None) -> str:
        
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
            except TypeError:
                return f"~~{id}~~"

    async def scramblestring(self, string: str):
        result = []
        for word in string.split(" "):
            result.append("".join(rand2.sample(word, len(word))))

        return " ".join(result)


    async def user_riddles_stats(self, member:discord.Member=None):

        try:
            _name = member.name
            _id = member.id
        except TypeError:
            _name = "~~Unknown~~"
            _id = "~~Unknown~~"

        em = discord.Embed(color=0x00F8EF)
        em.set_author(name=f"{_name}'s riddles stats:", icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

        if "riddle_lb" not in self.client.po_data.keys():
            em.description = f"**Total Guessed:** __0__ riddles." 
            return em

        elif str(_id) not in self.client.po_data["riddle_lb"].keys():
            em.description = f"**Total Guessed:** __0__ riddles."
            return em

        elif str(_id) in self.client.po_data["riddle_lb"].keys():
            em.description = f"**Total Guessed:** __{self.client.po_data['riddle_lb'][str(_id)]}__ riddles."
            return em

        else:
            em.description = "Error!"
            return em


    async def top_(self, ctx):
        
        em = discord.Embed(color=0x00F8EF, title="People with the 'smartest pants' in Pixels Minecraft Lounge")
        em.set_author(name="\u200b", icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

        if (not "riddle_lb" in self.client.po_data.keys()) or (not self.client.po_data["riddle_lb"]):  # If there are no memebrs with that role, return an embed with the number 0 as the user count.
            
            ad = f"The leaderboard of people who guessed the most riddles corerctly."
            em.description = ad + "\n\n" + f"`No players yet!`"
            
            await ctx.send(embed=em)
            return

        else:
            temp_li = []
            embeds = []
            count = 1
            user_count = 0

            data = sorted([[int(key), self.client.po_data["riddle_lb"][key]] for key in self.client.po_data["riddle_lb"].keys()], key=lambda e: e[1], reverse=True)


            for index, key in enumerate(data):  # x == member

                temp_li.append([index+1, key])
                user_count += 1

                if len(temp_li) == 10:
                    users = ""

                    for user in temp_li:

                        mem = await self.get_user(user[1][0])

                        if user[0] == 1:
                            users += f"🏆 - **{mem}** ({user[1][1]} riddles)"
                        elif user[0] == 2:
                            users += f"\n🥈 - **{mem}** ({user[1][1]} riddles)"
                        elif user[0] == 3:
                            users += f"\n🥉 - **{mem}** ({user[1][1]} riddles)"
                        else:
                            users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} riddles)"

                    em = discord.Embed(color=0x00F8EF, title="People with the 'smartest pants' in Pixels Minecraft Lounge")
                    em.set_author(name="\u200b", icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

                    ad = f"The leaderboard of people who guessed the most riddles corerctly."                    
                    em.description = ad + "\n\n" + users

                    embeds.append(em)

                    count += 1
                    temp_li = []

                elif user_count == len(data):  # x == members[-1]

                    users = "\n".join([f"**{user[0]}** - **{await self.get_user(user[1][0])}** ({user[1][1]} riddles)" for user in temp_li])

                    em = discord.Embed(color=0x00F8EF, title="People with the 'smartest pants' in Pixels Minecraft Lounge")
                    em.set_author(name="\u200b", icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

                    
                    ad = f"The leaderboard of people who guessed the most riddles corerctly."
                    em.description = ad + "\n\n" + users

                    embeds.append(em)
                    count += 1
                    temp_li = []

        if len(embeds) == 1:
            embeds[0].set_footer(text=f"{ctx.guild.name}",
                                  icon_url=str(self.client.user.avatar_url_as(static_format="png", size=2048)))
            return await ctx.send(embed=embeds[0])
        
        else:
            for index in range(len(embeds)):
                embeds[index].set_footer(text=f"{ctx.guild.name} - Page {index+1}/{len(embeds)}",
                                  icon_url=str(self.client.user.avatar_url_as(static_format="png", size=2048)))

        await Paginator(embeds, ctx).paginate()



    @cog_ext.cog_slash(name='riddles',
    guild_ids=[865870663038271489], 
     description='Display the leaderboard for most riddles guessed correctly.', 
     options=[
        create_option('player', 'The player\'s stats to check', 6, False),
    ])
    async def _riddles(self, ctx: SlashContext, player:discord.Member=None):
        
        if player:
            if not isinstance(player, (discord.Member, discord.User)):
                return await ctx.send("Sorry, I couldn't find that user.", hidden=True)
            return await ctx.send(embed=await self.user_riddles_stats(player))
        
        else:
            await ctx.defer(hidden=False)
            await self.top_(ctx)


    @commands.Cog.listener()
    async def on_message(self, message):
        if self.run:
            return
        elif self.is_riddle_guessed1:
            return
        if message.channel in self.generalchannels:
            if str(message.content).lower() == self.curr_riddle[1].lower():
                self.is_riddle_guessed1 = True

                if "riddle_lb" not in self.client.po_data.keys():
                    self.client.po_data["riddle_lb"] = {str(message.author.id): 1}
                elif str(message.author.id) not in self.client.po_data["riddle_lb"].keys():
                    self.client.po_data["riddle_lb"][str(message.author.id)] = 1
                else:
                    self.client.po_data["riddle_lb"][str(message.author.id)] += 1

                await self.client.addcoins(message.author.id, self.random_win)
                em = discord.Embed(
                    description=f"Congratulations {message.author.mention}!         You guessed the riddle! You got `{self.random_win}` cash",
                    color=0x00f8ef)
                em.set_footer(text=self.guild.name,
                              icon_url=str(self.client.user.avatar_url_as(static_format="png", size=2048)))

                await message.channel.send(embed=em)


    @tasks.loop(hours=24)
    async def clear_user_cache(self):
        self.client.user_cache = {}


def setup(client):
    if not client.debug:
        client.add_cog(CrCommands(client))
