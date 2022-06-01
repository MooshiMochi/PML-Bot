import discord
from discord.ext import commands, tasks
import json

from paginator import Paginator
from datetime import datetime
from discord.mentions import AllowedMentions
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash import cog_ext
from discord_slash.model import ButtonStyle
from discord_slash.utils import manage_components
import random
import asyncio
from discord.ext.commands import MemberConverter
from constants import const

mconv = MemberConverter()

"DOCS: https://discord-py-slash-command.readthedocs.io/en/components/discord_slash.context.html#discord_slash.context.ComponentContext"
# 865870663038271489 -PX, 840150806682664970 -SH
guild_ids = [865870663038271489]


class McMadness(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        self.unbelievaboat_api_enabled = True

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
        self.game_cache = {"message": None, "answer": None, "easy": 0,
                           "normal": 0, "hard": 0, "embed": None, "total": 0}
        self.correct_answer = "answer_not_yet_found"
        self.used_questions = []
        self.question_start_ts = 0
        self.users_guessed = []
        self.correct_option = "NOT_READY"
        self.is_event_ongoing = False
        self.give_10k_to_winner = False
        self.all_game_participants = {}
        self.eliminated = []

        self.get_ready.start()
        self.check_for_monthly_pay.start() if not const.DEBUG else None

    @tasks.loop(count=1)
    async def get_ready(self):
        await self.client.wait_until_ready()
        self.event_channel = self.client.guilds[0].get_channel(
            self.mm_channel_id)
        self.mm_channel = self.client.guilds[0].get_channel(self.mm_channel_id)
        self.tournament_channel = self.client.guilds[0].get_channel(
            self.tournament_id)
        self.game_exmplanation = (discord.Embed(color=0x00F8EF, title="Welcome to 'Minecraft Madness'!",
                                                description="This is a 'Minecraft Trivia Quiz' where people compete against\neach other to win the top prize (if there is one).\n\n"
                                                "You will be asked a series of multiple choice questions with increasing difficulty. You have to answer them by pressing the correct button.\n"
                                                "\nYou only get one chance per game. Good luck!").set_thumbnail(url=self.client.user.avatar_url_as(static_format="png", size=2048)))
        self.tournamet.start()

    @tasks.loop(minutes=1)
    async def check_for_monthly_pay(self):

        await self.client.wait_until_ready()

        scheduled_pay_time = datetime.strptime(
            "2022-02-01 05:01:00", "%Y-%m-%d %H:%M:%S").timestamp()

        if "mm_tournament_payout_ts" in self.client.po_data.keys() and self.client.po_data["mm_tournament_payout_ts"]:
            scheduled_pay_time = self.client.po_data["mm_tournament_payout_ts"]

        if datetime.now().timestamp() >= scheduled_pay_time:

            _date = str(datetime.now().date())
            next_schedule = ""
            if int(_date[5:7]) > 12:
                next_schedule = datetime.strptime(str(int(str(datetime.now().date())[
                                                  :4])+1) + "-01-01 05:01:00", "%Y-%m-%d %H:%M:%S").timestamp()
            else:
                if int(str(datetime.now().date())[5:7])+1 < 10:
                    filler = "0"
                else:
                    filler = ""

                next_schedule = datetime.strptime(str(datetime.now().date())[:5] + filler + str(int(
                    str(datetime.now().date())[5:7])+1) + "-01 05:01:00", "%Y-%m-%d %H:%M:%S").timestamp()

            # payout code here
            data = sorted([[key, self.client.po_data["mm_tournament"][key]]
                          for key in self.client.po_data["mm_tournament"].keys()], key=lambda e: e[1], reverse=True)[:10]

            payouts = [500000, 400000, 300000, 200000,
                       100000, 80000, 60000, 40000, 20000, 10000]

            guild = self.client.guilds[0]

            ch = guild.get_channel(867247651745038376)

            if data:
                for index in range(10):
                    if self.unbelievaboat_api_enabled:
                        try:
                            await self.client.addcoins(int(data[index][0]), payouts[0])
                        except IndexError:
                            continue
                    try:
                        mem = await self.get_user(int(data[index][0]))

                        em = discord.Embed(
                            colro=0x78BB67, description=f"<:Checkmark:886699674277396490> Added <:money:903467440829259796>**{payouts[0]:,}** to {mem}'s bank balance.")
                        em.set_author(name="Top 10 Monthly Minecraft Maddness Winner Payout",
                                      icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

                        await ch.send(embed=em)

                        print(
                            f"Added {payouts[0]} coins to {mem} - {data[index][0]} | {self.client.po_data['mm_tournament'][data[index][0]]}".encode('utf-8'))
                    except Exception as e:
                        print(e)

                    payouts.pop(0)

            if not "mm_month_count" in self.client.po_data.keys():
                self.client.po_data["mm_month_count"] = 2
            else:
                self.client.po_data["mm_month_count"] += 1

            if "mm_tournament" in self.client.po_data.keys():
                self.client.po_data["mm_tournament"] = {}
            else:
                self.client.po_data["mm_tournament"] = {}

            self.client.po_data["mm_tournament_payout_ts"] = next_schedule

            with open("data/payouts.json", "w") as f:
                json.dump(self.client.po_data, f, indent=2)

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
            except TypeError:
                return f"~~{id}~~"

    async def clear_variables(self):
        self.game_cache = {"message": None, "answer": None,
                           "easy": 0, "normal": 0, "hard": 0, "total": 0}
        self.users_guessed = []
        self.members_ready = False
        self.question_start_ts = 0
        self.used_questions = []
        self.correct_answer = "answer_not_yet_found"
        self.participants = {}
        self.correct_option = "NOT_READY"
        self.prize_pool = 0
        self.give_10k_to_winner = False
        self.is_tournament = False
        self.is_event_ongoing = False
        self.eliminated = []
        self.all_game_participants = {}

    async def update_tournament_lb(self, id: int = None):
        if "mm_tournament" not in self.client.po_data.keys():
            self.client.po_data["mm_tournament"] = {str(id): 1}
        elif str(id) not in self.client.po_data["mm_tournament"].keys():
            self.client.po_data["mm_tournament"][str(id)] = 1
        else:
            self.client.po_data["mm_tournament"][str(id)] += 1

    async def update_casual_lb(self, id: int = None):
        if "mm_casual" not in self.client.po_data.keys():
            self.client.po_data["mm_casual"] = {str(id): 1}
        elif str(id) not in self.client.po_data["mm_casual"].keys():
            self.client.po_data["mm_casual"][str(id)] = 1
        else:
            self.client.po_data["mm_casual"][str(id)] += 1

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
            self.game_cache[
                "embed"].description += f"\n\nThe prize for the winner will be <:money:903467440829259796> **{len(self.participants.keys())*10000:,}**"

        await msg.edit(embed=self.game_cache["embed"], components=action_row)

        self.members_ready = True

    async def main_event_func(self):

        before_start = True

        while 1:
            if self.game_cache["total"] >= 240:

                templi = enumerate(sorted([[x[0], x[1]] for x in self.participants.items(
                )], key=lambda pts: pts[1], reverse=True))

                # li[lb_pos][1(id)/0(pts)]
                result = "\n".join(
                    [f'**{pos[0]}.** <@!{pos[1][0]}> ({pos[1][1]})' for pos in templi])

                em = discord.Embed(color=0x00F8EF, title="GAME OVER!",
                                   description="It looks like you already answered all the questions that I had... damn!\nHere's the Leaderboard:\n"+result)

                await self.clear_variables()
                return await self.event_channel.send(embed=em)

            if before_start:
                before_start = False
                if len(self.participants) <= 1:
                    dont_start = discord.Embed(color=0x00F8EF)
                    if len(self.participants) == 1:
                        member = await self.get_user(list(self.participants.keys())[0])
                        dont_start.set_author(name=f"Looks like the event is cancelled for today!\nOnly {member} joined :(",
                                              icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
                        await self.clear_variables()
                        return await self.event_channel.send(embed=dont_start)

                    elif len(self.participants) != 1:
                        dont_start.set_author(name=f"Looks like the event is cancelled for today!\nNo one joined :(",
                                              icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
                        await self.clear_variables()
                        return await self.event_channel.send(embed=dont_start)

            # ar == action_row (3 buttons)
            main_em, ar, sleep_time = await self.prepare_question()

            msg = await self.event_channel.send(embed=main_em, components=ar)

            self.question_start_ts = datetime.now().timestamp()

            stop_ts = datetime.now().timestamp() + \
                sleep_time[0] + sleep_time[1]
            sent_notif = False

            reminder = discord.Embed(color=0x00F8EF).set_author(
                name=f"{sleep_time[1]} SECONDS LEFT TO GUESS", icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

            while datetime.now().timestamp() < stop_ts:

                if len(self.participants.keys()) == (len(self.users_guessed) + len(self.eliminated)):
                    break

                elif stop_ts - datetime.now().timestamp() <= sleep_time[1]:
                    if not sent_notif:
                        await self.event_channel.send(embed=reminder, delete_after=sleep_time[1])
                        sent_notif = True

                await asyncio.sleep(1)

            await msg.delete()

            disqualified_users = []
            disc_text = "**The following members were disqualified**\n\n"
            disqualified = ""

            for id, pts in self.participants.copy().items():
                if id not in self.users_guessed:
                    del self.participants[id]
                    disqualified_users.append((id, pts))

                if (id not in self.eliminated) and (id not in self.users_guessed):
                    try:
                        del self.participants[id]
                    except KeyError:
                        pass
                    disqualified += f"<@!{id}> with **{pts}** points.\n"

            disqualified = disqualified[-(250 - len(disc_text)):]

            disc_em = discord.Embed(
                color=0x00F8EF, description=disc_text + disqualified)
            if disqualified:
                await self.event_channel.send(embed=disc_em, delete_after=10)

            if not self.participants and disqualified_users:
                winner_id, winner_points = sorted(
                    disqualified_users, key=lambda r: r[1], reverse=True)[0]

                text = f"<@!{winner_id}>, You are the last player standing with **{winner_points}** points!"
                if self.is_tournament:
                    await self.update_tournament_lb(winner_id)
                    text += f"\n\nAs the sole survivor, you will receive <:money:903467440829259796> **{self.prize_pool:,}**!"
                    if self.unbelievaboat_api_enabled:
                        await self.client.addcoins(winner_id, self.prize_pool)
                else:
                    await self.update_casual_lb(winner_id)
                    if self.give_10k_to_winner:
                        text += f"\n\nAs the sole survivor, you will receive <:money:903467440829259796> **10,000**!"

                        if self.unbelievaboat_api_enabled:
                            await self.client.addcoins(winner_id, 10000)

                win_em = discord.Embed(
                    title="Game Over!", description=text, color=0x00F8EF)
                win_em.set_thumbnail(url=self.client.user.avatar_url_as(
                    static_format="png", size=2048))

                await self.clear_variables()
                await self.event_channel.send(embed=win_em)
                await self.event_channel.send("Check the win leaderboard with /mm_lb (tournaments/casual)")
                return

            elif len(self.participants) == 1:
                winner_id, winner_points = list(self.participants.keys())[
                    0], list(self.participants.values())[0]

                text = f"<@!{winner_id}>, You are the last player standing with **{winner_points}** points!"
                if self.is_tournament:
                    await self.update_tournament_lb(winner_id)
                    text += f"\n\nAs the sole survivor, you will receive <:money:903467440829259796> **{self.prize_pool:,}**!"
                    if self.unbelievaboat_api_enabled:
                        await self.client.addcoins(winner_id, self.prize_pool)
                else:
                    await self.update_casual_lb(winner_id)
                    if self.give_10k_to_winner:
                        text += f"\n\nAs the sole survivor, you will receive <:money:903467440829259796> **10,000**!"

                        if self.unbelievaboat_api_enabled:
                            await self.client.addcoins(winner_id, 10000)

                win_em = discord.Embed(
                    title="Game Over!", description=text, color=0x00F8EF)
                win_em.set_thumbnail(url=self.client.user.avatar_url_as(
                    static_format="png", size=2048))

                await self.clear_variables()
                await self.event_channel.send(embed=win_em)
                await self.event_channel.send("Check the win leaderboard with /mm_lb (tournaments/casual)")
                return

            self.users_guessed = []
            self.eliminated = []

    @cog_ext.cog_slash(name='mm',
                       guild_ids=guild_ids,
                       description='Start a Minecraft Madness game',)
    async def mm(self, ctx: SlashContext):

        await self.client.wait_until_ready()

        await ctx.defer(hidden=True)

        if self.is_event_ongoing:
            return await ctx.send("Sorry, a game is already in progress. Please wait until it's finished before starting a new one",
                                  hidden=True)
        self.is_tournament = False

        self.event_channel = self.mm_channel

        self.is_event_ongoing = True

        if not ctx.channel_id == self.event_channel.id:
            await ctx.send(f"A 'Minecraft Madness' event has started in <#{self.event_channel.id}>. Head there to join the fun!")

        await ctx.send("Success!", hidden=True)

        await self.join_event(self.event_channel)

        while not self.members_ready:  # wait until everyone is ready
            await asyncio.sleep(1)

        if len(self.participants) >= 5:
            self.give_10k_to_winner = True

        await self.main_event_func()

        self.is_event_ongoing = False

    @tasks.loop(minutes=470)
    async def tournamet(self):

        await self.client.wait_until_ready()

        await self.tournament_channel.send("<@&928113440617287800>, a tournament will begin in 10 minutes. Get ready!", allowed_mentions=AllowedMentions(roles=True))

        await asyncio.sleep(600)

        if self.is_event_ongoing:

            while self.is_event_ongoing:
                await asyncio.sleep(1)

        self.is_tournament = True
        self.is_event_ongoing = True
        self.event_channel = self.tournament_channel

        await self.event_channel.send("<@&928113440617287800>", allowed_mentions=AllowedMentions(roles=True))

        await self.join_event(self.event_channel)

        while not self.members_ready:  # wait until everyone is ready
            await asyncio.sleep(1)

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
            self.participants[ctx.author.id] = 0
            em.set_field_at(
                index=0, value=f"<@!{ctx.author_id}>", name=em.fields[0].name)
            self.all_game_participants[ctx.author.id] = 0
            self.game_cache["message"] = ctx.origin_message
            await ctx.edit_origin(embed=em)
            await ctx.send(embed=self.game_exmplanation, hidden=True)
            return

        elif ctx.author_id not in self.participants and self.participants:
            self.participants[ctx.author.id] = 0
            em.set_field_at(index=0, value=' | '.join(
                [f'<@!{str(x)}>' for x in list(self.participants.keys())]), name=em.fields[0].name)
            self.all_game_participants[ctx.author.id] = 0
            self.game_cache["message"] = ctx.origin_message
            await ctx.edit_origin(embed=em)
            await ctx.reply(embed=self.game_exmplanation, hidden=True)

        else:
            await ctx.reply("You are already participating in this event!", hidden=True)
            return

        self.game_cache["embed"] = em

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
            self.game_cache["hard"] = 0
            self.game_cache["normal"] = 0
            self.game_cache["easy"] = 0
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
        if (5 < self.game_cache["easy"] <= 10) and self.game_cache["normal"] == 0 and self.game_cache["hard"] == 0:
            sleep_time = [15, 10]
        elif (11 <= self.game_cache["easy"] <= 15) and self.game_cache["normal"] == 0 and self.game_cache["hard"] == 0:
            sleep_time = [10, 10]
        elif (16 <= self.game_cache["easy"] <= 20) and self.game_cache["normal"] == 0 and self.game_cache["hard"] == 0:
            sleep_time = [10, 5]

        em = discord.Embed(
            color=0x00F8EF, title=chosen_question, description=desc)
        em.set_author(name=f"Difficulty: {difficulty.lower().title()} | Level {len(self.used_questions)}",
                      icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
        em.set_footer(text=f"⏳ Try to answer it within {sleep_time[0] + sleep_time[1]} seconds",
                      icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

        action_row = [manage_components.create_actionrow(*option_buttons)]

        return em, action_row, sleep_time

    async def handle_correct_answer(self, ctx):

        await ctx.defer(hidden=True)

        if ctx.author_id in self.users_guessed:

            em = discord.Embed(
                color=0x00F8EF, description=f"Your current score is: **{self.all_game_participants[ctx.author_id]}**")
            em.set_author(name="You already answered this question.",
                          icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

            return await ctx.reply(embed=em, hidden=True)

        elif (ctx.author_id in self.eliminated):

            em = discord.Embed(
                color=0x00F8EF, description=f"Your score: **{self.all_game_participants[ctx.author_id]}**")
            em.set_author(name="You are already disqualified from the game!",
                          icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

            return await ctx.reply(embed=em, hidden=True)

        elif (ctx.author_id not in self.participants.keys()) and (
            ctx.author_id in self.all_game_participants.keys()
        ):
            em = discord.Embed(
                color=0x00F8EF, description=f"Your score: **{self.all_game_participants[ctx.author_id]}**")
            em.set_author(name="You are already disqualified from the game!",
                          icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

            return await ctx.reply(embed=em, hidden=True)

        elif (ctx.author_id not in self.all_game_participants.keys()):
            em = discord.Embed(color=0x00F8EF)
            em.set_author(name="You cannot participate in this event right now.",
                          icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

            return await ctx.reply(embed=em, hidden=True)

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

        await ctx.reply(embed=em, hidden=True)

    async def handle_incorrect_answer(self, ctx):

        await ctx.defer(hidden=True)

        if (ctx.author.id not in self.participants.keys()) and (ctx.author.id not in self.all_game_participants.keys()):
            em = discord.Embed(color=0x00F8EF)
            em.set_author(name="You cannot participate in this event right now.",
                          icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

            return await ctx.reply(embed=em, hidden=True)

        if ctx.author_id in self.users_guessed and ctx.author_id in self.participants.keys():
            em = discord.Embed(color=0x00F8EF)
            em.set_author(name="You already answered this question.",
                          icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

            return await ctx.reply(embed=em, hidden=True)

        if (ctx.author_id not in self.eliminated) and (ctx.author_id not in self.users_guessed) and (ctx.author.id in self.all_game_participants.keys()):

            try:
                self.all_game_participants[ctx.author_id] = self.participants[ctx.author_id]
            except KeyError:
                pass

            em = discord.Embed(color=0x00F8EF, description="You are now eliminated from the game!\n"
                               f"You accumulated a total of **{self.all_game_participants[ctx.author_id]}** points.")
            em.set_author(name=f"Wrong Answer, it was {self.correct_option}",
                          icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

            try:
                self.all_game_participants[ctx.author_id] = self.participants[ctx.author_id]
                # del self.participants[ctx.author_id]

                await ctx.reply(embed=em, hidden=True)
                self.eliminated.append(ctx.author_id)

                await self.event_channel.send(embed=(discord.Embed(description=f"**{ctx.author.name}** was disqualified with **{self.all_game_participants[ctx.author_id]}**\n**{len(self.participants) - len(self.eliminated)}** players remaining", color=0x00F8EF).set_author(name="R.I.P",
                                                                                                                                                                                                                                                                                 icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))), delete_after=5)
                return
            except KeyError:
                em = discord.Embed(
                    color=0x00F8EF, description=f"Your score: **{self.all_game_participants[ctx.author_id]}**")
                em.set_author(name="You are already disqualified from the game!",
                              icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

                return await ctx.reply(embed=em, hidden=True)

        elif ctx.author_id in self.all_game_participants.keys() and ctx.author_id in self.eliminated:
            em = discord.Embed(
                color=0x00F8EF, description=f"Your score: **{self.all_game_participants[ctx.author_id]}**")
            em.set_author(name="You are already disqualified from the game!",
                          icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

            return await ctx.reply(embed=em, hidden=True)

        else:
            em = discord.Embed(color=0x00F8EF)
            em.set_author(name="You cannot participate in this event right now.",
                          icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

            return await ctx.reply(embed=em, hidden=True)

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
                           create_option(
                               'difficulty', 'The difficulty level of the question', 3, True),
                           create_option(
                               "question", "The question to be asked", 3, True),
                           create_option(
                               "answer", "The correct answer to the question", 3, True),
                           create_option("alternate_option_1",
                                         "An incorrect answer for the question", 3, True),
                           create_option("alternate_option_2",
                                         "Another incorrect answer for the question", 3, True)
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
                           create_option(
                               'difficulty', 'The difficulty level of the question', 3, True),
                           create_option("question_to_edit",
                                         "The question to edit", 3, True),
                           create_option("new_question",
                                         "The new questions to be asked in the game", 3, True),
                           create_option(
                               "answer", "The correct answer to the question", 3, True),
                           create_option("alternate_option_1",
                                         "An incorrect answer for the question", 3, True),
                           create_option("alternate_option_2",
                                         "Another incorrect answer for the question", 3, True)
                       ])
    async def edit(self, ctx: SlashContext, difficulty=None, question_to_edit=None, new_question=None, answer=None, alternate_option_1=None, alternate_option_2=None):

        if 867915052638941224 not in [r.id for r in ctx.author.roles]:
            return await ctx.send("You don't have enough permissions to run this command.")

        if None in [difficulty, question_to_edit, new_question, answer, alternate_option_1, alternate_option_2]:
            return await ctx.send("You must enter all the required fields in this command.")

        try:
            del self.quiz_data[difficulty.lower()][question_to_edit]
        except KeyError:
            return await ctx.send(f"The question `{question_to_edit}` doesn't exst in the `{difficulty.lower().capitalize()}` difficulty questions bank.")

        with open("quiz_data/final_questions.json", "w", encoding="utf8") as f:
            self.quiz_data[difficulty.lower()][question_to_edit] = {"options": [answer, alternate_option_2, alternate_option_1],
                                                                    "answer": answer}
            json.dump(self.quiz_data, f, indent=2)

        return await ctx.send(f"Question data changed to: {difficulty.lower().capitalize()} difficulty.")

    @cog_ext.cog_slash(name='delete',
                       guild_ids=guild_ids,
                       description='Delete a question from the questions bank.',
                       options=[
                           create_option(
                               'difficulty', 'The difficulty level of the question', 3, True),
                           create_option("question_to_delete",
                                         "The question to delete", 3, True),
                       ])
    async def delete(self, ctx: SlashContext, difficulty=None, question_to_delete=None):

        if 867915052638941224 not in [r.id for r in ctx.author.roles]:
            return await ctx.send("You don't have enough permissions to run this command.")

        if None in [difficulty, question_to_delete]:
            return await ctx.send("You must enter all the required fields in this command.")
        try:
            del self.quiz_data[difficulty.lower()][question_to_delete]
        except KeyError:
            return await ctx.send(f"The question `{question_to_delete}` doesn't exst in the `{difficulty.lower().capitalize()}` difficulty questions bank.")

        with open("quiz_data/final_questions.json", "w", encoding="utf8") as f:
            json.dump(self.quiz_data, f, indent=2)

        return await ctx.send(f"Deleted `{question_to_delete}` from the questions bank in the {difficulty.lower().capitalize()} difficulty.")

    async def __mm_player_stats(self, member: discord.Member = None):

        try:
            the_name = member.name
        except TypeError:

            the_name = "~~Unknown~~"

        em = discord.Embed(color=0x00F8EF, description="")
        em.set_author(name=f"{the_name}'s Minecraft Madness Stats:",
                      icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))

        if "mm_tournament" not in self.client.po_data.keys() and "mm_casual" not in self.client.po_data.keys():

            em.description = "**Tournaments:** __0__ wins.\n**Casual:** __0__ wins."
            return em

        elif "mm_tournament" in self.client.po_data.keys() and "mm_casual" not in self.client.po_data.keys():
            if str(member.id) in self.client.po_data["mm_tournament"].keys():
                em.description = f"**Tournaments:** __{self.client.po_data['mm_tournament'][str(member.id)]}__ wins.\n**Casual:** __0__ wins."
            else:
                em.description = "**Tournaments:** __0__ wins.\n**Casual:** __0__ wins."
            return em

        elif "mm_tournament" not in self.client.po_data.keys() and "mm_casual" in self.client.po_data.keys():
            if str(member.id) in self.client.po_data["mm_casual"].keys():
                em.description = f"**Tournaments:** __0__ wins.\n**Casual:** __{self.client.po_data['mm_casual'][str(member.id)]}__ wins."
            else:
                em.description = f"**Tournaments:** __0__ wins.\n**Casual:** __0__ wins."
            return em

        elif "mm_tournament" in self.client.po_data.keys() and "mm_casual" in self.client.po_data.keys():
            if str(member.id) in self.client.po_data["mm_tournament"].keys() and str(member.id) in self.client.po_data['mm_casual'].keys():
                em.description = f"**Tournaments:** _{self.client.po_data['mm_tournament'][str(member.id)]}_ wins.\n**Casual:** _{self.client.po_data['mm_casual'][str(member.id)]}_ wins."

            elif str(member.id) in self.client.po_data['mm_tournament'].keys() and str(member.id) not in self.client.po_data['mm_casual'].keys():
                em.description = f"**Tournaments:** _{self.client.po_data['mm_tournament'][str(member.id)]}_ wins.\n**Casual:** _0_ wins."

            elif str(member.id) not in self.client.po_data['mm_tournament'].keys() and str(member.id) in self.client.po_data['mm_casual'].keys():
                em.description = f"**Tournaments:** _0_ wins.\n**Casual:** _{self.client.po_data['mm_casual'][str(member.id)]}_ wins."

            else:
                em.description = "**Tournaments:** __0__ wins.\n**Casual:** __0__ wins."
            return em

        else:

            em.author.name = "Error!"
            return em

    async def __mm_lb(self, ctx, tournament_or_casual):

        em = discord.Embed(
            color=0x00F8EF, title=f"Minecraft Madness ({tournament_or_casual.lower().capitalize()}) Leaderboard")
        em.set_author(name="\u200b", icon_url=self.client.user.avatar_url_as(
            static_format="png", size=2048))

        if not "mm_month_count" in self.client.po_data.keys():
            self.client.po_data["mm_month_count"] = 1

        # If there are no memebrs with that role, return an embed with the number 0 as the user count.
        if (("mm_casual" not in self.client.po_data.keys() or not self.client.po_data["mm_casual"]) and tournament_or_casual.lower() == "casual") or (("mm_tournament" not in self.client.po_data.keys() or not self.client.po_data["mm_tournament"]) and tournament_or_casual.lower() == "tournaments"):

            if tournament_or_casual == "tournaments":
                ad = f"The leaderboard for the biggest 'Minecraft Madness' (tournaments) winners in Pixels Minecraft Lounge for month #{self.client.po_data['mm_month_count']}. The top 10 biggest winners win cash prizes every month!\n\n*Wins only count for Minecraft Madness Tournaments\n\n1st of every month at 00:01/12 AM EST and all monthly tournament winners are reset*"
            else:
                ad = f"The leaderboard for the biggest 'Minecraft Madness' (casual) winners in Pixels Minecraft Lounge."
            em.description = ad + "\n\n" + f"`No players yet!`"

            await ctx.send(embed=em)
            return

        # len <= 10
        if (
            (tournament_or_casual == "tournaments" and ("mm_tournament" in self.client.po_data.keys()) and len(self.client.po_data['mm_tournament'].keys()) <= 10) or (
                tournament_or_casual == "casual" and ("mm_casual" in self.client.po_data.keys()) and len(self.client.po_data["mm_casual"].keys()) <= 10)
        ):

            if tournament_or_casual == "tournaments":
                data = enumerate(sorted([[key, self.client.po_data["mm_tournament"][key]]
                                 for key in self.client.po_data["mm_tournament"].keys()], key=lambda e: e[1], reverse=True))
            else:
                data = enumerate(sorted([[key, self.client.po_data["mm_casual"][key]]
                                 for key in self.client.po_data["mm_casual"].keys()], key=lambda e: e[1], reverse=True))

            users = ""

            for user in data:
                mem = await self.get_user(int(user[1][0]))

                if user[0] == 0:
                    if tournament_or_casual == "tournaments":
                        users += f"🏆 - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 500k"
                    else:
                        users += f"🏆 - **{mem}** ({user[1][1]} wins)"

                elif user[0] == 1:
                    if tournament_or_casual == "tournaments":
                        users += f"\n🥈 - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 400k"
                    else:
                        users += f"\n🥈 - **{mem}** ({user[1][1]} wins)"
                elif user[0] == 2:
                    if tournament_or_casual == "tournaments":
                        users += f"\n🥉 - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 300k"
                    else:
                        users += f"\n🥉 - **{mem}** ({user[1][1]} wins)"
                elif user[0] == 3:
                    if tournament_or_casual == "tournaments":
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 200k"
                    else:
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"
                elif user[0] == 4:
                    if tournament_or_casual == "tournaments":
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 100k"
                    else:
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"
                elif user[0] == 5:
                    if tournament_or_casual == "tournaments":
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 80k"
                    else:
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"
                elif user[0] == 6:
                    if tournament_or_casual == "tournaments":
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 60k"
                    else:
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"
                elif user[0] == 7:
                    if tournament_or_casual == "tournaments":
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 40k"
                    else:
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"
                elif user[0] == 8:
                    if tournament_or_casual == "tournaments":
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 20k"
                    else:
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"
                elif user[0] == 9:
                    if tournament_or_casual == "tournaments":
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 10k"
                    else:
                        users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"
                else:
                    users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"

            #  Initiate first embed (if there are less than 10 members for that role, send the embed)
            if tournament_or_casual == "tournaments":
                ad = f"The leaderboard for the biggest 'Minecraft Madness' (tournaments) winners in Pixels Minecraft Lounge for month #{self.client.po_data['mm_month_count']}. The top 10 biggest winners win cash prizes every month!\n\n*Wins only count for Minecraft Madness Tournaments\n\n1st of every month at 00:01/12 AM EST and all monthly tournament winners are reset*"
            else:
                ad = f"The leaderboard for the biggest 'Minecraft Madness' (casual) winners in Pixels Minecraft Lounge."

            em.description = ad + "\n\n" + users

            await ctx.send(embed=em)
            return
        # If there are more than 10 members for that role, create paginator and send embeds with 10 memebrs per embed.

        else:
            temp_li = []
            embeds = []
            count = 1
            user_count = 0

            if tournament_or_casual == "tournaments":
                data = sorted([[key, self.client.po_data["mm_tournament"][key]]
                              for key in self.client.po_data["mm_tournament"].keys()], key=lambda e: e[1], reverse=True)
            else:
                data = sorted([[key, self.client.po_data["mm_casual"][key]]
                              for key in self.client.po_data["mm_casual"].keys()], key=lambda e: e[1], reverse=True)

            for index, key in enumerate(data):  # x == member

                temp_li.append([index+1, key])
                user_count += 1

                if len(temp_li) == 10:

                    users = ""

                    for user in temp_li:

                        mem = await self.get_user(user[1][0])

                        if user[0] == 1:
                            if tournament_or_casual == "tournaments":
                                users += f"🏆 - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 500k"
                            else:
                                users += f"🏆 - **{mem}** ({user[1][1]} wins)"

                        elif user[0] == 2:
                            if tournament_or_casual == "tournaments":
                                users += f"\n🥈 - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 400k"
                            else:
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"

                        elif user[0] == 3:
                            if tournament_or_casual == "tournaments":
                                users += f"\n🥉 - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 300k"
                            else:
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"

                        elif user[0] == 4:
                            if tournament_or_casual == "tournaments":
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 200k"
                            else:
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"

                        elif user[0] == 5:
                            if tournament_or_casual == "tournaments":
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 100k"
                            else:
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"

                        elif user[0] == 6:
                            if tournament_or_casual == "tournaments":
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 80k"
                            else:
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"

                        elif user[0] == 7:
                            if tournament_or_casual == "tournaments":
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 60k"
                            else:
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"

                        elif user[0] == 8:
                            if tournament_or_casual == "tournaments":
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 40k"
                            else:
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"

                        elif user[0] == 9:
                            if tournament_or_casual == "tournaments":
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 20k"
                            else:
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"

                        elif user[0] == 10:
                            if tournament_or_casual == "tournaments":
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins) - <:money:903467440829259796> 10k"
                            else:
                                users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"

                        else:
                            users += f"\n**{user[0]}.** - **{mem}** ({user[1][1]} wins)"

                    em = discord.Embed(
                        color=0x00F8EF, title=f"Minecraft Madness ({tournament_or_casual.lower().capitalize()}) Leaderboard")
                    em.set_author(name="\u200b", icon_url=self.client.user.avatar_url_as(
                        static_format="png", size=2048))

                    if tournament_or_casual == "tournaments":
                        ad = f"The leaderboard for the biggest 'Minecraft Madness' (tournaments) winners in Pixels Minecraft Lounge for month #{self.client.po_data['mm_month_count']}. The top 10 biggest winners win cash prizes every month!\n\n*Wins only count for Minecraft Madness Tournaments\n\n1st of every month at 00:01/12 AM EST and all monthly tournament winners are reset*"
                    else:
                        ad = f"The leaderboard for the biggest 'Minecraft Madness' (casual) winners in Pixels Minecraft Lounge."

                    em.description = ad + "\n\n" + users

                    embeds.append(em)

                    count += 1
                    temp_li = []

                elif user_count == len(data):  # x == members[-1]

                    users = "\n".join([f"**{user[0]}** - **{await self.get_user(user[1][0])}** ({user[1][1]} wins)" for user in temp_li])

                    em = discord.Embed(
                        color=0x00F8EF, title=f"Minecraft Madness ({tournament_or_casual.lower().capitalize()}) Leaderboard")
                    em.set_author(name="\u200b", icon_url=self.client.user.avatar_url_as(
                        static_format="png", size=2048))

                    if tournament_or_casual == "tournaments":
                        ad = f"The leaderboard for the biggest 'Minecraft Madness' (tournaments) winners in Pixels Minecraft Lounge for month #{self.client.po_data['mm_month_count']}. The top 10 biggest winners win cash prizes every month!\n\n*Wins only count for Minecraft Madness Tournaments\n\n1st of every month at 00:01/12 AM EST and all monthly tournament winners are reset*"
                    else:
                        ad = f"The leaderboard for the biggest 'Minecraft Madness' (casual) winners in Pixels Minecraft Lounge."
                    em.description = ad + "\n\n" + users

                    embeds.append(em)
                    count += 1
                    temp_li = []

        for index in range(len(embeds)):
            embeds[index].set_footer(
                text=f"{ctx.guild.name} - Page {index+1}/{len(embeds)}")

        await Paginator(embeds, ctx).paginate()

    @cog_ext.cog_slash(name='mm_stats', guild_ids=guild_ids, description="View your or someone else's Minecraft Madness stats.",
                       options=[create_option(name="player", description="The player you want to view stats for.", option_type=6, required=False)])
    async def mm_stats(self, ctx: SlashContext, player: discord.Member = None):
        await ctx.defer(hidden=True)
        if not player:
            player = ctx.author
        return await ctx.send(embed=await self.__mm_player_stats(player), hidden=True)

    @cog_ext.cog_slash(
        name='mm_leaderboard',
        guild_ids=guild_ids,
        description='Display the leaderboard for Minecraft Madness Tournaments or Casual most winners.',
        options=[
            create_option(
                    'leaderboard_type', 'The leaderboard type to view: Casual or Tournaments leaderboard', 3, True, choices=[
                        create_choice(value="tournaments", name="Tournaments"),
                        create_choice(value="casual", name="Casual")])])
    async def _mm_lb(self, ctx: SlashContext, leaderboard_type: str = None):
        await ctx.defer(hidden=False)
        await self.__mm_lb(ctx, leaderboard_type)


def setup(client):
    if not client.debug:
        client.add_cog(McMadness(client))
