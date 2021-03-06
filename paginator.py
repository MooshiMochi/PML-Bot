
from uuid import uuid4
from typing import Iterable
from asyncio import TimeoutError

from discord.embeds import Embed
from discord.errors import NotFound
from discord.ext.commands import Context

from discord_slash import ComponentContext
from discord_slash.model import ButtonStyle
from discord_slash.utils import manage_components


class Paginator:
    def __init__(self, _iterable:list=None, ctx:Context=None) -> None:
        self._iterable = _iterable
        self.ctx = ctx

        self.button_left_id = str(uuid4()).replace("-", "_")
        self.button_right_id = str(uuid4()).replace("-", "_")
        self.button_stop_id = str(uuid4()).replace("-", "_")

        if not self._iterable and not self.ctx:
            raise AttributeError("A list of items of type 'Union[str, int, discord.Embed]' was not provided to iterate through as well as the invocation context.")

        elif not _iterable:
            raise AttributeError("A list of items of type 'Union[str, int, discord.Embed]' was not provided to iterate through.")

        elif not ctx:
            raise AttributeError("The ctx of the invocation command was not provided.")

        if not isinstance(_iterable, Iterable):
            raise AttributeError("An iterable containing items of type 'Union[str, int, discord.Embed]' classes is required.")
        
        elif False in [isinstance(item, (str, int, Embed)) for item in _iterable]:
            raise AttributeError("All items within the iterable must be of type 'str', 'int' or 'discord.Embed'.")

        self._iterable = list(self._iterable)

    async def paginate(self):

        command_buttons = [
        manage_components.create_button(
            style=ButtonStyle.blue,
            label="◀",
            custom_id=self.button_left_id
        ),
        manage_components.create_button(
            style=ButtonStyle.blue,
            label="⏹",
            custom_id=self.button_stop_id
        ),
        manage_components.create_button(
            style=ButtonStyle.blue,
            label="▶",
            custom_id=self.button_right_id
        )]

        timeout_buttons = [manage_components.create_button(
            style=ButtonStyle.danger,
            label="Menu timed out.",
            custom_id="paginator_button_timeout",
            disabled=True
        )]

        cancel_buttons = [manage_components.create_button(
            style=ButtonStyle.danger,
            label="Cancelled.",
            custom_id="paginator_button_cancel",
            disabled=True
        )]

        my_action_row = manage_components.create_actionrow(*command_buttons)

        timeout_action_row = manage_components.create_actionrow(*timeout_buttons)

        cancel_action_row = manage_components.create_actionrow(*cancel_buttons)

        msg = await self.ctx.send(embed=self._iterable[0], components=[my_action_row])

        page = 0
        while 1:

            try:
                button_ctx: ComponentContext = await manage_components.wait_for_component(
                    self.ctx.bot, components=[my_action_row], timeout=30
                    )

                if button_ctx.author_id != self.ctx.author.id:
                    await button_ctx.reply("You were not the author of this command therefore cannot use these components.", hidden=True)
                    continue
                
                if button_ctx.custom_id == self.button_left_id:
                    page -= 1
                    if page == -1:
                        page = len(self._iterable)-1

                elif button_ctx.custom_id == self.button_stop_id:
                    await button_ctx.defer(edit_origin=True)
                    try:
                        if isinstance(self._iterable[page], Embed):
                            await msg.edit(embed=self._iterable[page], components=[cancel_action_row])
                        else:
                            await msg.edit(content=self._iterable[page], components=[cancel_action_row])
                    except NotFound:
                        pass
                    return

                elif button_ctx.custom_id == self.button_right_id:
                    page += 1
                    if page > len(self._iterable)-1:
                        page = 0

                try:
                    if isinstance(self._iterable[page], Embed):
                        await button_ctx.edit_origin(embed=self._iterable[page])
                    else:
                        await button_ctx.edit_origin(content=self._iterable[page])
                except NotFound:
                    raise TimeoutError

            except TimeoutError:
                if isinstance(self._iterable[page], Embed):
                    await msg.edit(embed=self._iterable[page], components=[timeout_action_row])
                else:
                    await msg.edit(content=self._iterable[page], components=[timeout_action_row])
                break
