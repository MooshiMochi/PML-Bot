from re import A
import discord
from discord.ext import commands, tasks
import json
from datetime import datetime
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash import cog_ext
from typing import Optional
from discord.ext.commands import MemberConverter

mconv = MemberConverter()

class PrivateChat(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.category_id = 889001024684175360
        self.category_ch = None

        with open("data/priv_chats.json", "r") as f:
            self.pv = json.load(f)
        
        self.self_ready.start()

    async def delete(self, key):
        if str(key) in self.pv.keys():
            del self.pv[str(key)]
            print("Deleted", key)
        else:
            print("Couldn't find", key)

    @tasks.loop(count=1)
    async def self_ready(self):
        await self.client.wait_until_ready()

        self.category_ch = self.client.guilds[0].get_channel(self.category_id)
        self.check_priv_status.start()


    async def create_channel(self, ctx, members:list=None):
        await self.client.wait_until_ready()

        guild = ctx.guild
        member = ctx.author

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        for mem in members:
            overwrites[mem] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        category = self.client.get_channel(self.category_id)

        channel = await guild.create_text_channel(name=f'{ctx.author.name}-pchat', overwrites=overwrites, category=category)

        self.pv[str(channel.id)] = {
            # "ts": datetime.now().timestamp(), 
            "author": str(ctx.author.id), 
            "created_at": datetime.now().timestamp()}

        await channel.send(embed=discord.Embed(description=f"Welcome to your very own Private Chat!\n\
\n\
__In this Private Chat, you can do the following:__\n\
- Chat, of course, privately\n\
- Send and share memes, images, videos, etc\n\
- Play Truth or Dare /tod\n\
+ whatever else you can think of!\n\
\n\
You will have this private chat for 48 hours. Have fun! \n\
To close your private chat, at any time, type: /close <#{channel.id}>\n\
\n\
*Messages for leaderboards do not count here, only in general.*", color=0x00F8EF).set_author(name=ctx.author, 
icon_url=ctx.author.avatar_url_as(static_format="png", size=2048)))

        return channel

    
    async def get_users(self, ctx, _str):
        
        uli = []

        if ("<" in _str) and (">" in _str):
            write = ""
            start = False

            for char in _str:
                if char == "<":
                    start = True
                    continue

                if char == ">":
                    start = False
                    uli.append(int(write))
                    write = ""
                    continue

                if start:    
                    try:
                        char = int(char)
                        write += f"{char}"
                    except ValueError:
                        continue

            fails = []
            success = []
            for mem in uli:
                try:
                    mem = ctx.guild.get_member(mem)
                    success.append(mem)
                except commands.errors.MemberNotFound:
                    fails.append(mem)

            if fails:
                return [False, f"Failed: the following members were not found:\n{', '.join([f'{x}' for x in fails])}\n"
                "You must ping up to 10 members separated by `space` or `,` while running this command."]

            else:
                return [True, success]

        else:
            return [False, "You must ping the members you want to add to your private chat."]
            



    @cog_ext.cog_slash(name='pc',
     guild_ids=[865870663038271489], 
     description='Create a private chat for up to 10 members', 
     options=[
        create_option('members', 'The members to add to the chat', 3, True),
    ])
    async def _pc(self, ctx: SlashContext, members: Optional[str]=None):
        
        await self.client.wait_until_ready()

        if len(self.category_ch.channels) == 10:
            return await ctx.send("Private Chats limit reached. Please wait until a private chat is deleted.")

        for key in self.pv.keys():
            if self.pv[key]["author"] == str(ctx.author.id):
                return await ctx.send("You can have a maximum of 1 priavte channel at a time.")

        if members:

            test = await self.get_users(ctx, members)

            if not test[0]:
                return await ctx.send(test[1])

            memroles = [r.id for r in ctx.author.roles]
            if 926972884470087790 not in memroles:
                msg = await self.client.addcoins(ctx.author.id, -69420)
                if msg == "You are too poor to afford a private chat.":
                    return await ctx.send(msg + " A private chat costs <:money:903467440829259796>**69,420**.")

                await ctx.send("You have been charged <:money:903467440829259796>**69,420**.")


            ch = await self.create_channel(ctx, test[1])

            em = discord.Embed(color=0x00F8EF, description=f"A private chat <#{ch.id}> has been created by <@!{ctx.author.id}> for {', '.join([f'<@!{e.id}>' for e in test[1]])}\nYou will have this private chat for 48 hours.")
            em.set_author(name=ctx.author, icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
            await ctx.send(embed=em)

    @commands.command()
    async def pc(self, ctx, *, members:str=None):

        await self.client.wait_until_ready()

        if not members:
            return await ctx.send("You must ping up to 10 members separated by `space` or `,` while running this command.")
        
        if len(self.category_ch.channels) == 10:
            return await ctx.send("Private Chats limit reached. Please wait until a private chat is deleted.")

        for key in self.pv.keys():
            if self.pv[key]["author"] == str(ctx.author.id):
                return await ctx.send("You can have a maximum of 1 priavte channel at a time.")

        if members:

            test = await self.get_users(ctx, members)

            if not test[0]:
                return await ctx.send(test[1])

            memroles = [r.id for r in ctx.author.roles]
            if 926972884470087790 not in memroles:
                msg = await self.client.addcoins(ctx.author.id, -69420)
                if msg == "You are too poor to afford a private chat.":
                    return await ctx.send(msg + " A private chat costs <:money:903467440829259796>**69,420**.")
                await ctx.send("You have been charged <:money:903467440829259796>**69,420**.")


            ch = await self.create_channel(ctx, test[1])

            em = discord.Embed(color=0x00F8EF, description=f"A private chat <#{ch.id}> has been created by <@!{ctx.author.id}> for {', '.join([f'<@!{e.id}>' for e in test[1]])}\nYou will have this private chat for 48 hours.")
            em.set_author(name=ctx.author, icon_url=self.client.user.avatar_url_as(static_format="png", size=2048))
            await ctx.send(embed=em)


    async def __close(self, ctx, chat:str=None):

        await self.client.wait_until_ready()

        # if not ctx.author.guild_permissions.manage_channels:
        #     return await ctx.send("You do not have enough permissions to run this command.")

        if (("<" not in chat) and (">" not in chat) and ("#" not in chat)):
            return await ctx.send("The channel must be pinged when using this command.")
        
        chat = chat.replace("<", "").replace(">", "").replace("#", "")

        if chat not in self.pv.keys():
            return await ctx.send("This chat is not a private chat.")

        if not chat:
            return await ctx.send("Somehow that channel doesn't exist?")

        for channel in self.category_ch.channels:
            if (channel.id == int(chat) and (str(channel.id) in self.pv.keys())):

                await self.delete(channel.id)

                await channel.delete()
                return

        return await ctx.send("Somehow this channel doesn't exist.")

    @cog_ext.cog_slash(name='close',
     guild_ids=[865870663038271489], 
     description='Close a private channel', 
     options=[
        create_option('channel_name', 'The name of the channel to close', 3, False),
    ])
    async def _close(self, ctx: SlashContext, channel_name: Optional[str]=None):
        if not channel_name:
            channel_name = f"<#{ctx.channel.id}>"

        await self.__close(ctx, channel_name)

    @commands.command()
    async def close(self, ctx, *, channel_name:str=None):
        if not channel_name:
            channel_name = f"<#{ctx.channel.id}>"
        await self.__close(ctx, channel_name)

    @tasks.loop(seconds=10)
    async def check_priv_status(self):

        await self.client.wait_until_ready()

        if not self.pv:
            return

        for ch_id in self.pv.copy().keys():
            try:
                if int(ch_id) not in [x.id for x in self.category_ch.channels]:
                    await self.delete(ch_id)
                
                elif datetime.now().timestamp() - self.pv[ch_id]["created_at"] >= 48*60*60:
                    channel = self.client.guilds[0].get_channel(int(ch_id))
                    await self.delete(ch_id)
                    await channel.delete()
            except KeyError:
                print(f"I tried to delete PRIVATE CHAT {ch_id} but couldn't find it.")

        with open("data/priv_chats.json", "w") as f:
            json.dump(self.pv, f, indent=2)


def setup(client):
    if not client.debug:
        client.add_cog(PrivateChat(client))