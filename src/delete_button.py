"""The delete button under the messages that fix links."""

import re
from typing import Self, override

import discore

from src import utils


class DeleteButton(discore.ui.DynamicItem[discore.ui.Button], template=r'fixtweetbot:delete:(?P<author_id>[0-9]+)'):
    """A button that deletes the message it sits on once the author of the fixed link presses it."""

    def __init__(self, author_id: int) -> None:
        """Builds the grey trash can button for the message fixing a link that the user with the id `author_id` posted."""
        super().__init__(discore.ui.Button(style=discore.ButtonStyle.secondary, emoji='🗑️', custom_id=f'fixtweetbot:delete:{author_id}'))
        self.author_id: int = author_id
        """The id of the user who posted the fixed link."""

    @classmethod
    @override
    async def from_custom_id(cls, interaction: discore.Interaction, item: discore.ui.Button, match: re.Match[str], /) -> Self:
        """Builds the button again from the author id in the custom id that `match` matched."""
        return cls(int(match['author_id']))

    @override
    async def callback(self, interaction: discore.Interaction) -> None:
        """
        Deletes the message the button sits on if the user of `interaction` is its author, and otherwise replies privately that the button is not theirs.

        A message that is already deleted is answered quietly.
        """
        utils.entrypoint_context.set(f"button delete {{interaction={interaction!r}}}")
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(utils.t('delete_button.not_author', locale=interaction.locale.value), ephemeral=True)
            return
        await interaction.response.defer()
        # For a component interaction, the original response is the message the button sits on.
        await utils.safe_send_coro(interaction.delete_original_response(), not_found=True)
