
import json
import discord
import asyncio

from random import sample
from random import choice, randint

from discord.ext import commands
from discord.ext import tasks

from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash
from discord_slash.utils.manage_commands import create_option, create_choice

from paginator import Paginator

class Riddles(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.last_user_ids = [0, 0, 0, 0]

        with open("data/riddles.json", "r") as f:
            self.riddles = json.load(f)

        if "main_ch" not in self.riddles.keys():
            self.riddles["main_ch"] = 866526262759129118

        self.main_ch = self.riddles["main_ch"]
        
        self.riddle_nonce = "aerhagj33££!34$$bea13513te131UKW!²╪Ur134hthh[}{ajwhd[]9a}_--=-#~jkwnanjavOKEadk:!@!"

        self.used_riddles = {}
        self.used_categories = []
        self.current_riddle = {"question": self.riddle_nonce, "answer": self.riddle_nonce}
        self.random_win = 500
        self.is_riddle_guessed = False

        self.clear_user_cache.start()

        self.get_ready.start()

        if self.riddles['active']:
            self.run_riddles.start()

    
    async def scramblestring(self, string: str):
        result = []
        for word in string.split(" "):
            result.append("".join(sample(word, len(word))))

        return " ".join(result)
    
    
    @tasks.loop(count=1)
    async def get_ready(self):
        guild = self.client.get_guild(865870663038271489)
        try:
            self.main_ch = guild.get_channel(self.main_ch)
            if not self.main_ch:
                self.riddles["active"] = False
        except (TypeError, AttributeError):
            self.client.remove_cog("commands.games.riddles")


    @tasks.loop(minutes=5.0)
    async def run_riddles(self):
        await asyncio.sleep(5)

        if not self.riddles['active']: return

        if len(self.last_user_ids) < 4:
            return

        cat_opts = [key for key in self.riddles["type"] if key not in self.used_categories]

        if not cat_opts:
            cat_opts = [key for key in self.riddles["type"].keys() if key != self.used_categories[-1]]
            self.used_categories = []

        cat = choice(list(self.riddles["type"].keys()))
        self.used_categories.append(cat)

        if cat not in self.used_riddles: 
            self.used_riddles[cat] = {}
        
        riddle_opts = [key for key in self.riddles["type"][cat] if key not in self.used_riddles[cat]]
        
        if not riddle_opts:
            riddle_opts = [key for key in self.riddles["type"][cat] if key != list(self.used_riddles[cat].keys())[-1]]
            self.used_riddles[cat] = {}

        riddle_num = choice(riddle_opts)

        self.used_riddles[cat][riddle_num] = self.riddles["type"][cat][riddle_num]

        self.current_riddle = self.riddles["type"][cat][riddle_num]
        
        if cat == "unscramble":
            self.current_riddle["question"] = await self.scramblestring(self.current_riddle["answer"])
            msg = f"Unscramble: {self.current_riddle['question']}"
        else:
            msg = self.current_riddle["question"]

        self.random_win = randint(500, 2500)

        em = discord.Embed(color=0x72F8EF, title="New chat riddle", description=msg+f"\n\n*Answer the riddle correctly for {self.random_win} <:real:931186583586107472>!*")
        em.set_footer(text="Pixel | Riddles", icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

        self.is_riddle_guessed = False

        try:
            await self.main_ch.send(embed=em)
            self.last_user_ids = []
        except (discord.HTTPException, discord.Forbidden):
            pass

    @run_riddles.before_loop
    @get_ready.before_loop
    async def before_run_riddles(self):
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):

        if msg.author.bot:
            return
        else:
            if not isinstance(self.main_ch, int):
                if msg.channel.id == self.main_ch.id and msg.author.id not in self.last_user_ids:
                    self.last_user_ids.append(msg.author.id)

        if self.is_riddle_guessed:
            return
        
        elif self.riddles["active"]:
            if msg.content.lower() == self.current_riddle["answer"].lower():
                self.is_riddle_guessed = True
                
                if "riddle_lb" not in self.client.po_data.keys():
                    self.client.po_data["riddle_lb"] = {str(msg.author.id): 1}

                elif str(msg.author.id) not in self.client.po_data["riddle_lb"].keys():
                    self.client.po_data["riddle_lb"][str(msg.author.id)] = 1
                else:
                    self.client.po_data["riddle_lb"][str(msg.author.id)] += 1

                await self.client.addcoins(msg.author.id, self.random_win)

                em = discord.Embed(
                    description=f"Congratulations {msg.author.mention}!         You guessed the riddle! You got `{self.random_win}` <:real:931186583586107472>",
                    color=0x72F8EF)
                em.set_footer(text="Pixel | Riddles",
                              icon_url=str(self.client.user.avatar_url_as(static_format="png", size=2048)))

                await msg.channel.send(embed=em)


    @cog_slash(name="riddles_config", description="[ADMIN] Configure riddles", guild_ids=[865870663038271489], options=[
        create_option(name="active", description="Activate or deactivate riddles", option_type=5, required=False),
        create_option(name="riddles_channel", description="Channel where riddles will be sent", option_type=7, required=False),
    ])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def riddles_config(self, ctx:SlashContext, active:bool=None, riddles_channel:discord.TextChannel=None):
        
        await ctx.defer(hidden=True)

        text = "Config settings:\n"

        if active is not None:
            if active == self.riddles["active"]:
                text += f"> Activated: Already set to `{active}`\n"
            else:
                self.riddles["active"] = active
                text += f"> Activated: Set to `{active}`\n"
        else:
            text += f"> Activated: `{active}` (unchanged)\n"

        if riddles_channel:
            if riddles_channel.id != self.riddles["main_ch"]:
                if isinstance(riddles_channel, discord.VoiceChannel):
                    return await ctx.send("Riddles channel must be a Text Channel, not a Voice Channel!", hidden=True)

                self.riddles["main_ch"] = riddles_channel.id
                self.main_ch = riddles_channel
                text += f"> Channel: Set to <#{riddles_channel.id}>\n"
            else:
                text += f"> Channel: Already set to <#{self.riddls['main_ch']}>\n"
        
        else:
            if not self.riddles['main_ch'] and self.riddles['active']:
                return await ctx.send("'Riddles channel' parameter MUST be specified if 'active' parameter is set to TRUE", hidden=True)
            text += f"> Channel: <#{self.riddles['main_ch']}> (unchanged)"

        with open("data/riddles.json", "w") as f:
            json.dump(self.riddles, f, indent=2)

        if self.riddles['active']:
            try:
                if self.run_riddles.is_running():
                    self.run_riddles.cancel()
                self.run_riddles.start()
            except RuntimeError:
                if self.run_riddles.is_running():
                    self.run_riddles.cancel()
                self.run_riddles.start()

        else:
            if self.run_riddles.is_running():
                self.run_riddles.cancel()

        return await ctx.send(text, hidden=True)


    @cog_slash(name="riddles_add", description="[ADMIN] Add a riddle", guild_ids=[865870663038271489], options=[
        create_option(name="type", description="Type of riddle", option_type=3, required=True, choices=[
            create_choice(value="question", name="Question"),
            create_choice(value="trivia", name="Trivia"),
            create_choice(value="riddle", name="Riddle"),
            create_choice(value="unscramble", name="Unscramble")
        ]),
        create_option(name="question", description="The question the users have to answer", option_type=3, required=True),
        create_option(name="answer", description="The answer to the question", option_type=3, required=True)
    ])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def riddles_add(self, ctx:SlashContext, type:str=None, question:str=None, answer:str=None):
        
        await ctx.defer(hidden=True)

        self.riddles[type][str(len(self.riddles[type])+1)] = {
            "question": question,
            "answer": answer
        }

        em = discord.Embed(color=0x72F8EF, title="New riddle added", 
        description=f"**Type: __{type.capitalize()}__**\n\n`#{len(self.riddles[type])}. {question}`\n> {answer}")
        em.set_footer(text="Pixel | Riddles", icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
        

        with open("data/games/riddles.json", "w") as f:
            json.dump(self.riddles, f, indent=2)

        return await ctx.send(embed=em, hidden=True)


    @cog_slash(name="riddles_delete", description="[ADMIN] Delete a riddle", guild_ids=[865870663038271489], options=[
        create_option(name="type", description="Type of riddle", option_type=3, required=True, choices=[
            create_choice(value="question", name="Question"),
            create_choice(value="trivia", name="Trivia"),
            create_choice(value="riddle", name="Riddle"),
            create_choice(value="unscramble", name="Unscramble")
        ]),
        create_option(name="riddle_number", description="The number of the riddle (use /riddles_questions)", option_type=4, required=True)
    ])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def riddles_delete(self, ctx:SlashContext, type:str=None, riddle_number:int=None):
        
        await ctx.defer(hidden=True)

        if not str(riddle_number) in self.riddles[type].keys():
            return await ctx.send(f"That riddle doesn't exist in the {type.capitalize()} category.", hidden=True)

        question = self.riddles[type][str(riddle_number)]["question"]
        answer = self.riddles[type][str(riddle_number)]["answer"]
        
        if not self.riddles[type].pop(str(riddle_number), False):
            return await ctx.send(f"That riddle doesn't exist in the {type.capitalize()} category.", hidden=True)

        copied_dict = self.riddles[type].copy()
        self.riddles[type] = {}

        for index, qna in enumerate(copied_dict.values()):
            self.riddles[type][str(index+1)] = qna

        em = discord.Embed(color=0x72F8EF, title="Riddle deleted", 
        description=f"**Type: __{type.capitalize()}__**\n\n`#{riddle_number}. {question}`\n> {answer}")
        em.set_footer(text="Pixel | Riddles", icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
        
        with open("data/games/riddles.json", "w") as f:
            json.dump(self.riddles, f, indent=2)

        return await ctx.send(embed=em, hidden=True)


    @cog_slash(name="riddles_questions", description="[ADMIN] Display all Riddles questions and answers", guild_ids=[865870663038271489], options=[
        create_option(name="type", description="Type of riddles", option_type=3, required=True, choices=[
            create_choice(value="question", name="Question"),
            create_choice(value="trivia", name="Trivia"),
            create_choice(value="riddle", name="Riddle"),
            create_choice(value="unscramble", name="Unscramble")
        ]) | {"focused": True}])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def riddles_questions(self, ctx:SlashContext, type:str=None):
        await ctx.defer(hidden=True)
        
        ranked = list(self.riddles[type].keys())

        embeds = []

        add_on = [y for y in range(9, len(self.riddles[type]), 10)] if len(self.riddles[type]) >= 10 else [len(self.riddles[type])-1]

        if len(add_on) > 1 and add_on[-1] % 10 != 0:
            add_on.append(len(self.riddles[type])-1)
        
        em = discord.Embed(color=0x72F8EF, title=f"Riddles Q & A's ({type.capitalize()})", description="")
        
        for x in range(len(self.riddles[type])):
            
            question = self.riddles[type][ranked[x]]["question"]
            answer = self.riddles[type][ranked[x]]["answer"]
            
            em.description += f"`#{ranked[x]}. {question}`\n"
            em.description += f"> {answer}\n\n"

            if x in add_on:
                em.set_footer(text=f"Pixel | Riddles | Page {add_on.index(x)+1}/{len(add_on)-1}",
                icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
                embeds.append(em)

                em = discord.Embed(color=0x72F8EF, title=f"Riddles Q & A's ({type.capitalize()})", description="")

        for index, embed in enumerate(embeds):
            embed: discord.Embed
            embed.set_footer(text=f"Pixel | Riddles | Page {index+1}/{len(embeds)}", icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

        return await Paginator(embeds, ctx).run()
        
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


    async def user_riddles_stats(self, member:discord.Member=None):
        if not isinstance(member, (discord.Member, discord.User)):
            _name = "~~Unknown~~"
            _id = "~~Unknown~~"
        else:
            _name = member.name
            _id = member.id           

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


    async def riddles_lb(self, ctx):
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

    @cog_slash(name='riddles',
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
            await self.riddles_lb(ctx)

    @tasks.loop(hours=24)
    async def clear_user_cache(self):
        self.client.user_cache = {}

def setup(client):
    client.add_cog(Riddles(client))