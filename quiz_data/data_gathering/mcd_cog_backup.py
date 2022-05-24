import discord
from discord.ext import commands, tasks
import json
from datetime import datetime
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash import cog_ext
from discord_slash.model import ButtonStyle
from discord_slash.utils import manage_components
import random
import asyncio


"DOCS: https://discord-py-slash-command.readthedocs.io/en/components/discord_slash.context.html#discord_slash.context.ComponentContext"
guild_ids = [865870663038271489]  # 865870663038271489 -PX, 840150806682664970 -SH

class McMadness(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        
        self.mm_channel_id = 927650030951759892
        self.tournament_id = 926333104401022976
        self.event_channel = None
        self.mm_channel = None
        self.tournament_channel = None
        self.is_tournament = False
        self.prize_pool = 0
        self.game_exmplanation = None

        with open("quiz_data/final_questions.json", "r", encoding="utf8") as f:
            self.quiz_data = json.load(f)

        self.participants = {}
        self.members_ready = False
        self.game_cache = {"message": None, "answer": None, "easy": 0, "normal": 0, "hard": 0, "embed": None, "total": 0}
        self.correct_answer = "answer_not_yet_found"
        self.used_questions = []
        self.question_start_ts = 0
        self.users_guessed = []
        self.correct_option = "NOT_READY"
        self.is_event_ongoing = False
        self.give_10k_to_winner = False
        self.all_game_participants = {}
        self.last_disqualified_team = []

        self.get_ready.start()
    
    @tasks.loop(count=1)
    async def get_ready(self):
        await self.client.wait_until_ready()
        self.event_channel = self.client.guilds[0].get_channel(self.mm_channel_id)
        self.mm_channel = self.client.guilds[0].get_channel(self.mm_channel_id)
        self.tournament_channel = self.client.guilds[0].get_channel(self.tournament_id)
        self.game_exmplanation = (discord.Embed(color=0x00F8EF, title="Welcome to 'Minecraft Madness'!",
        description="This is a 'Minecraft Trivia Quiz' where people compete against\neach other to win the top prize (if there is one).\n\n"
        "You will be asked a series of multiple choice questions with increasing difficulty. You have to answer them by pressing the correct button.\n"
        "\nYou only get one chance per game. Good luck!").set_thumbnail(url=self.client.user.avatar_url_as(static_format="png", size=2048)))
        self.tournamet.start()
    
    async def clear_variables(self):
        self.game_cache = {"message": None, "answer": None, "easy": 0, "normal": 0, "hard": 0, "total": 0}
        self.users_guessed = []
        self.members_ready = False
        self.question_start_ts = 0
        self.used_questions = []
        self.correct_answer = "answer_not_yet_found"
        self.participants = {}
        self.correct_option = "NOT_READY"
        self.prize_pool = 0
        self.give_10k_to_winner = False
        self.last_disqualified_team = []
        

    async def join_event(self, channel):
        
        start_time = datetime.now().timestamp() + 60

        em = discord.Embed(color=0x00F8EF, title="Minecraft Madness Event!", 
        description=f"*The event will begin <t:{int(start_time)}:R>*\n")

        em.add_field(name="Participants:", value="`No participants yet!`")

        join_button = [
            manage_components.create_button(
                style=ButtonStyle.green,
                label="Enter",
                custom_id="i_joined"
            )]
        
        action_row = [manage_components.create_actionrow(*join_button)]

        msg = await channel.send(embed=em, components=action_row)
        self.game_cache["embed"] = msg.embeds[0]

        while 1:
            if start_time - (datetime.now().timestamp()) >= 0:
                await asyncio.sleep(start_time - (datetime.now().timestamp()))
                break

        no_more_joins = [manage_components.create_button(
            style=ButtonStyle.danger,
            label="Event Started",
            custom_id="event_started",
            disabled=True
        )]
        action_row = [manage_components.create_actionrow(*no_more_joins)]
        
        if self.give_10k_to_winner:
            self.game_cache["embed"].description += "\n\nThe prize for the winner will be <:money:903467440829259796> **10,000**"
        elif self.is_tournament:
            self.game_cache["embed"].description += f"\n\nThe prize for the winner will be <:money:903467440829259796> **{len(self.participants.keys())*10000:,}**"

        await msg.edit(embed=self.game_cache["embed"], components=action_row)

        self.members_ready = True

    
    async def main_event_func(self):
        
        cancel_action_row = [manage_components.create_actionrow(*[
            manage_components.create_button(
                style=ButtonStyle.danger,
                label="🚫",
                custom_id="cancelled_button",
                disabled=True
            )
        ])]

        before_start = True

        while 1:
            if self.game_cache["total"] >= 240:

                templi = enumerate(sorted([[x[0], x[1]] for x in self.participants.items()], key=lambda pts: pts[1], reverse=True))
                
                # li[lb_pos][1(id)/0(pts)]
                result = "\n".join([f'**{pos[0]}.** <@!{pos[1][0]}> ({pos[1][1]})' for pos in templi])

                em = discord.Embed(color=0x00F8EF, title="GAME OVER!",
                description="It looks like you already answered all the questions that I had... damn!\nHere's the Leaderboard:\n"+result)
                
                await self.clear_variables()
                return await self.event_channel.send(embed=em)

            if before_start:
                before_start = False
                if len(self.participants) <= 1:
                    dont_start = discord.Embed(color=0x00F8EF)
                    if len(self.participants) == 1:
                        member = self.event_channel.guild.get_member(list(self.participants.keys())[0])
                        dont_start.set_author(name=f"Looks like the event is cancelled for today!\nOnly {member.name} joined :(",
                        icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
                        await self.clear_variables()
                        return await self.event_channel.send(embed=dont_start)
                    
                    elif len(self.participants) != 1:
                        dont_start.set_author(name=f"Looks like the event is cancelled for today!\nNo one joined :(",
                        icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
                        await self.clear_variables()
                        return await self.event_channel.send(embed=dont_start)

            main_em, ar, sleep_time = await self.prepare_question()

            msg = await self.event_channel.send(embed=main_em, components=ar)
            self.question_start_ts = datetime.now().timestamp()

            await asyncio.sleep(sleep_time[0])

            reminder = discord.Embed(color=0x00F8EF)
            reminder.set_author(name=f"{sleep_time[1]} SECONDS LEFT TO GUESS")
            await self.event_channel.send(embed=reminder, delete_after=10)

            await asyncio.sleep(sleep_time[1])

            await msg.edit(embed=main_em, components=cancel_action_row)

    # Check for users that didn't try...
            did_not_try = []
            for id, pts in self.participants.copy().items():
                if id not in self.users_guessed:
                    did_not_try.append((id, pts))
                    del self.participants[id]

            self.last_disqualified_team = did_not_try

            winner_id = 0; winner_points = 0

            if not did_not_try and len(self.participants) == 0:
                winner_id, winner_points = sorted(self.last_disqualified_team, key=lambda r: r[1], reversed=True)[0]

            elif len(self.participants) == 0:
                winner_id, winner_points = sorted(disqualified, key=lambda r: r[1], reverse=True)[0]

            disc_text = "**The following members were disqualified**\n\n"
            disqualified = ""
            for id, pts in did_not_try:
                if id != winner_id:
                    disqualified += f"<@!{id}> with **{pts}** points.\n"
            
            disqualified = disqualified[-(250 - len(disc_text)):]

            disc_em = discord.Embed(color=0x00F8EF, description=disc_text + disqualified)
            if did_not_try:
                await self.event_channel.send(embed=disc_em)

            if winner_id:
                text = f"<@!{winner_id}>, You are the last player standing with **{winner_points}** points!"
                if self.is_tournament:
                    text += f"\n\nAs the sole survivor, you will receive <:money:903467440829259796> **{self.prize_pool:,}**!"
                    # await self.client.addcoins(winner_id, self.prize_pool)
                else:
                    if self.give_10k_to_winner:
                        text += f"\n\nAs the sole survivor, you will receive <:money:903467440829259796> **10,000**!"
                        # await self.client.addcoins(winner_id, 10000)

                win_em = discord.Embed(title="Game Over!", description=text, color=0x00F8EF)
                win_em.set_thumbnail(url=self.client.user.avatar_url_as(static_format="png", size=2048))
                await self.clear_variables()
                return await self.event_channel.send(embed=win_em)

    # Check if there's 1 player left in the game.

            if len(self.participants) == 1:
                solo_win_id = list(self.participants.keys())[0]
                solo_win_pts = list(self.participants.values())[0]

                text = f"<@!{solo_win_id}>, You are the last player standing with **{solo_win_pts}** points!"
                if self.is_tournament:
                    text += f"\n\nAs the sole survivor, you will receive <:money:903467440829259796> **{self.prize_pool:,}**!"
                    # await self.client.addcoins(solo_win_id, self.prize_pool)
                else:
                    if self.give_10k_to_winner:
                        text += f"\n\nAs the sole suvivor, you will receive <:money:903467440829259796> **10,000**!"
                        # await self.client.addcoins(solo_win_id, 10000)

                win_em = discord.Embed(title="Game Over!", description=text, color=0x00F8EF)
                win_em.set_thumbnail(url=self.client.user.avatar_url_as(static_format="png", size=2048))
                await self.clear_variables()
                return await self.event_channel.send(embed=win_em)

            self.users_guessed = []

    
    @cog_ext.cog_slash(name='mm',
    guild_ids=guild_ids, 
     description='Start a Minecraft Madness game',)
    async def mm(self, ctx: SlashContext):
    
        await self.client.wait_until_ready()
    
        if self.is_event_ongoing:
            return await ctx.send("Sorry, a game is already in progress. Please wait until it's finished before starting a new one",
            hidden=True)
        self.is_tournament = False

        self.event_channel = self.mm_channel

        self.is_event_ongoing = True

        await self.join_event(self.event_channel)

        while not self.members_ready:  # wait until everyone is ready
            await asyncio.sleep(1)

        if len(self.participants) >= 5:
            self.give_10k_to_winner = True

        await self.main_event_func()

        await ctx.defer(edit_origin=False, hidden=False)

        self.is_event_ongoing = False

    @tasks.loop(hours=4)
    async def tournamet(self):
    
        await self.client.wait_until_ready()
    
        if self.is_event_ongoing:

            while self.is_event_ongoing:
                await asyncio.sleep(1)
        self.is_tournament = True
        self.is_event_ongoing = True
        self.event_channel = self.tournament_channel

        await self.join_event(self.event_channel)

        while not self.members_ready:  # wait until everyone is ready
            await asyncio.sleep(1)

        if len(self.participants) >= 5:
            self.give_10k_to_winner = True

        self.prize_pool = len(self.participants.keys()) * 10000

        await self.main_event_func()
        
        self.is_event_ongoing = False


    async def handle_join_button(self, ctx):
        try:
            em = ctx.origin_message.embeds[0]
            self.game_cache["embed"] = em
        except IndexError:
            em = self.game_cache["embed"]

        if not self.participants:
            em.set_field_at(index=0, value=f"<@!{ctx.author_id}>", name=em.fields[0].name)
            self.participants[ctx.author_id] = 0
            self.all_game_participants[ctx.author.id] = 0
            self.game_cache["message"] = ctx.origin_message
            await ctx.send(embed=self.game_exmplanation, hidden=True)

        elif ctx.author_id not in self.participants and self.participants:
            em.set_field_at(index=0, value=f"{em.fields[0].value} | <@!{ctx.author_id}>", name=em.fields[0].name)
            self.participants[ctx.author.id] = 0
            self.all_game_participants[ctx.author.id] = 0
            self.game_cache["message"] = ctx.origin_message
            await ctx.send(embed=self.game_exmplanation, hidden=True)

        else:
            await ctx.send("You are already participating in this event!", hidden=True)
            return

        self.game_cache["embed"] = em
        await self.game_cache["message"].edit(embed=em)

    async def return_difficulty(self):
        if self.game_cache["easy"] < 20 and self.game_cache["normal"] == 0 and self.game_cache["hard"] == 0:
            self.game_cache["easy"] += 1
            self.game_cache["total"] += 1
            return "easy"        

        elif self.game_cache["easy"] == 20 and self.game_cache["normal"] == 0 and self.game_cache["hard"] == 0:
            self.game_cache["normal"] += 1
            self.game_cache["total"] += 1
            return "normal"
        
        if self.game_cache["normal"] < 10 and self.game_cache["easy"] == 20 and self.game_cache["hard"] == 0:
            self.game_cache["normal"] += 1
            self.game_cache["total"] += 1
            return "normal"
        elif self.game_cache["normal"] == 10 and self.game_cache["easy"] == 20 and self.game_cache["hard"] == 0:
            self.game_cache["hard"] += 1
            self.game_cache["total"] += 1
            return "hard"

        if self.game_cache["hard"] < 10 and self.game_cache["easy"] == 20 and self.game_cache["normal"] == 10:
            self.game_cache["hard"] += 1
            self.game_cache["total"] += 1
            return "hard"

        elif self.game_cache["hard"] == 10 and self.game_cache["easy"] == 20 and self.game_cache["normal"] == 10:
            self.game_cache["hard"] = 0; self.game_cache["normal"] = 0; self.game_cache["easy"] = 0
            self.game_cache["easy"] += 1
            self.game_cache["total"] += 1
            return "easy"        

    async def prepare_question(self):
        difficulty = await self.return_difficulty()
        
        chosen_question = {}
        while 1:
            
            chosen_question = random.choice(list(self.quiz_data[difficulty]))
            if chosen_question not in self.used_questions:
                self.used_questions.append(chosen_question)
                break

        random.shuffle(self.quiz_data[difficulty][chosen_question]["options"])
        path = self.quiz_data[difficulty][chosen_question]
        desc = ""
        option_buttons = []
        labels = ["A", "B", "C"]
        for pos in range(len(path["options"])):
            if path["options"][pos].lower().strip() == path["answer"].lower().strip():
                self.correct_answer = f"option_{pos}"
                self.correct_option = labels[pos]

            desc += f"`{labels[pos]}) {path['options'][pos]}`\n\n"
            option_buttons.append(
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label=labels[pos],
                    custom_id=f"option_{pos}"
                ))

        sleep_time = [20, 10]
        if self.game_cache["easy"] == 5 and self.game_cache["normal"] == 0 and self.game_cache["hard"] == 0:
            sleep_time = [15, 10]
        elif self.game_cache["easy"] == 10 and self.game_cache["normal"] == 0 and self.game_cache["hard"] == 0:
            sleep_time = [10, 10]
        elif self.game_cache["easy"] == 15 and self.game_cache["normal"] == 0 and self.game_cache["hard"] == 0:
            sleep_time = [10, 5]
        elif self.game_cache["easy"] == 20 and self.game_cache["normal"] == 0 and self.game_cache["hard"] == 0:
            sleep_time = [5, 5]

        em = discord.Embed(color=0x00F8EF, title=chosen_question, description=desc)
        em.set_author(name=f"Difficulty: {difficulty.lower().title()} | Level {len(self.used_questions)}",
        icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
        em.set_footer(text=f"⏳ Try to answer it within {sleep_time[0] + sleep_time[1]} seconds", icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
        
        action_row = [manage_components.create_actionrow(*option_buttons)]

        return em, action_row, sleep_time

    async def handle_correct_answer(self, ctx):
        if ctx.author_id in self.users_guessed:

            em = discord.Embed(color=0x00F8EF)
            em.set_author(name="You already answered this question.",
            icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
            return await ctx.send(embed=em, hidden=True)
        
        elif ctx.author_id not in list(self.participants.keys()):

            em = discord.Embed(color=0x00F8EF)
            em.set_author(name="You cannot participate in this event right now.",
            icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
            return await ctx.send(embed=em, hidden=True)

        if datetime.now().timestamp() - self.question_start_ts <= 5:
            if not self.users_guessed:
                self.participants[ctx.author_id] += 30
            elif len(self.users_guessed) == 1:
                self.participants[ctx.author_id] += 25
            elif len(self.users_guessed) == 2:
                self.participants[ctx.author_id] += 20
            else:
                self.participants[ctx.author_id] += 10

        elif datetime.now().timestamp() - self.question_start_ts <= 15:
            if not self.users_guessed:
                self.participants[ctx.author.id] += 20
            elif len(self.users_guessed) == 1:
                self.participants[ctx.author_id] += 19
            elif len(self.users_guessed) == 2:
                self.participants[ctx.author_id] += 18
            elif len(self.users_guessed) == 3:
                self.participants[ctx.author_id] += 15
            elif len(self.users_guessed) == 4:
                self.participants[ctx.author_id] += 14
            elif len(self.users_guessed) == 5:
                self.participants[ctx.author_id] += 13
            elif len(self.users_guessed) == 6:
                self.participants[ctx.author_id] += 12
            elif len(self.users_guessed) == 7:
                self.participants[ctx.author_id] += 11
            elif len(self.users_guessed) == 8:
                self.participants[ctx.author_id] += 10
            else:
                self.participants[ctx.author_id] += 5
        
        elif datetime.now().timestamp() - self.question_start_ts <= 30:
            if not self.users_guessed:
                self.participants[ctx.author.id] += 10
            elif len(self.users_guessed) == 1:
                self.participants[ctx.author_id] += 9
            elif len(self.users_guessed) == 2:
                self.participants[ctx.author_id] += 8
            elif len(self.users_guessed) == 3:
                self.participants[ctx.author_id] += 5
            elif len(self.users_guessed) == 4:
                self.participants[ctx.author_id] += 4
            elif len(self.users_guessed) == 5:
                self.participants[ctx.author_id] += 3
            elif len(self.users_guessed) == 6:
                self.participants[ctx.author_id] += 2
            else:
                self.participants[ctx.author_id] += 1

        self.all_game_participants[ctx.author_id] = self.participants[ctx.author_id]

        self.users_guessed.append(ctx.author_id)

        em = discord.Embed(color=0x00F8EF)
        em.set_author(name="Your answer is correct! You're moving on to the next round.", 
        icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
        await ctx.send(embed=em, hidden=True)

    async def handle_incorrect_answer(self, ctx):
        if ctx.author_id in self.users_guessed and ctx.author_id in list(self.participants.keys()):
            em = discord.Embed(color=0x00F8EF)
            em.set_author(name="You already answered this question.",
            icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
            return await ctx.send(embed=em, hidden=True)

        if ctx.author_id in list(self.participants.keys()) and ctx.author_id not in self.users_guessed:
            em = discord.Embed(color=0x00F8EF, description="You are now eliminated from the game!\n"
            f"You accumulated a total of **{self.participants[ctx.author_id]}** points.")
            em.set_author(name=f"Wrong Answer, it was {self.correct_option}",
            icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
            await ctx.send(embed=em, hidden=True)
        
            del self.participants[ctx.author_id]
            return

        elif ctx.author_id in list(self.all_game_participants.keys()) and ctx.author_id not in list(self.participants.keys()):
            em = discord.Embed(color=0x00F8EF, description=f"Your score: **{self.all_game_participants[ctx.author_id]}**")
            em.set_author(name="You are already disqualified from the game!",
            icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
            return await ctx.send(embed=em, hidden=True)

        else:
            em = discord.Embed(color=0x00F8EF)
            em.set_author(name="You cannot participate in this event right now.",
            icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
            return await ctx.send(embed=em, hidden=True)


    @commands.Cog.listener()
    async def on_component(self, ctx):
        if ctx.custom_id == "i_joined":
            await self.handle_join_button(ctx)
        
        elif ctx.custom_id == self.correct_answer:
            await self.handle_correct_answer(ctx)

        elif ctx.custom_id in ["option_0", "option_1", "option_2"] and ctx.custom_id != self.correct_answer:
            await self.handle_incorrect_answer(ctx)

        else:
            # await ctx.defer(hidden=False, edit_origin=False)
            pass

    @cog_ext.cog_slash(name='add',
     guild_ids=guild_ids, 
     description='Add a new question to the quiz game.', 
     options=[
        create_option('difficulty', 'The difficulty level of the question', 3, True),
        create_option("question", "The question to be asked", 3, True),
        create_option("answer", "The correct answer to the question", 3, True),
        create_option("alternate_option_1", "An incorrect answer for the question", 3, True),
        create_option("alternate_option_2", "Another incorrect answer for the question", 3, True)
    ])
    async def add(self, ctx: SlashContext, difficulty=None, question=None, answer=None, alternate_option_1=None, alternate_option_2=None):
        
        if 867915052638941224 not in [r.id for r in ctx.author.roles]:
            return await ctx.send("You don't have enough permissions to run this command.")

        if None in [difficulty, question, answer, alternate_option_1, alternate_option_2]:
            return await ctx.send("You must enter all the required fields in this command.")
        
        with open("quiz_data/final_questions.json", "w", encoding="utf8") as f:
            self.quiz_data[difficulty.lower()][question] = {"options": [answer, alternate_option_2, alternate_option_1],
            "answer": answer}
            json.dump(self.quiz_data, f, indent=2)
        
        return await ctx.send(f"New question added to the {difficulty.lower().capitalize()} difficulty.")

    @cog_ext.cog_slash(name='edit',
     guild_ids=guild_ids, 
     description='Edit an existing question.', 
     options=[
        create_option('difficulty', 'The difficulty level of the question', 3, True),
        create_option("question_to_edit", "The question to edit", 3, True),
        create_option("new_question", "The new questions to be asked in the game", 3, True),
        create_option("answer", "The correct answer to the question", 3, True),
        create_option("alternate_option_1", "An incorrect answer for the question", 3, True),
        create_option("alternate_option_2", "Another incorrect answer for the question", 3, True)
    ])
    async def edit(self, ctx: SlashContext, difficulty=None, question=None, new_question=None, answer=None, alternate_option_1=None, alternate_option_2=None):
        
        if 867915052638941224 not in [r.id for r in ctx.author.roles]:
            return await ctx.send("You don't have enough permissions to run this command.")

        if None in [difficulty, question, new_question, answer, alternate_option_1, alternate_option_2]:
            return await ctx.send("You must enter all the required fields in this command.")
        
        try:
            del self.quiz_data[difficulty.lower()][question]
        except KeyError:
            return await ctx.send(f"The question `{question}` doesn't exst in the `{difficulty.lower().capitalize()}` difficulty questions bank.")
                
        with open("quiz_data/final_questions.json", "w", encoding="utf8") as f:
            self.quiz_data[difficulty.lower()][question] = {"options": [answer, alternate_option_2, alternate_option_1],
            "answer": answer}
            json.dump(self.quiz_data, f, indent=2)
        
        return await ctx.send(f"Question data changed to: {difficulty.lower().capitalize()} difficulty.")

    @cog_ext.cog_slash(name='delete',
    guild_ids=guild_ids, 
     description='Delete a question from the questions bank.', 
     options=[
        create_option('difficulty', 'The difficulty level of the question', 3, True),
        create_option("question_to_delete", "The question to delete", 3, True),
    ])
    async def delete(self, ctx: SlashContext, difficulty=None, question=None):
        
        if 867915052638941224 not in [r.id for r in ctx.author.roles]:
            return await ctx.send("You don't have enough permissions to run this command.")

        if None in [difficulty, question]:
            return await ctx.send("You must enter all the required fields in this command.")
        try:
            del self.quiz_data[difficulty.lower()][question]
        except KeyError:
            return await ctx.send(f"The question `{question}` doesn't exst in the `{difficulty.lower().capitalize()}` difficulty questions bank.")
                
        with open("quiz_data/final_questions.json", "w", encoding="utf8") as f:
            json.dump(self.quiz_data, f, indent=2)
        
        return await ctx.send(f"Deleted `{question}` from the questions bank in the {difficulty.lower().capitalize()} difficulty.")


def setup(client):
    if not client.debug:
        client.add_cog(McMadness(client))
