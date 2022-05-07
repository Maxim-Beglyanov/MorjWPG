from nextcord import Interaction, Member, slash_command, SlashOption
from nextcord.ext.commands import Bot

from Discord.Controller.defaults import CountryParameters
from Discord.Controller.Country import delete_country
from Discord.Cogs.Cog import MyCog


class Country(MyCog):
    @MyCog.curators_perm()
    @slash_command(name='country', description='Изменение стран')
    async def country(self, inter: Interaction):
        pass

    @country.subcommand(name='del-country', description='Удалить страну')
    async def delete_country(
            self, inter: Interaction,
            player: Member = SlashOption(
                name='игрок',
                description='Игрок, которого вы хотите удалить',
                required=False,
                default=None
            ),
            for_all_countries: bool = SlashOption(
                name='для-всех-стран',
                description='Удалить все страны',
                required=False,
                default=None
            )
    ):
        await delete_country(
                inter, self, 
                CountryParameters(self, player, for_all_countries)
        )


def setup(bot: Bot):
    bot.add_cog(Country(bot))
