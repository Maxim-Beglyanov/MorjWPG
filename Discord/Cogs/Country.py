from nextcord import Interaction, Member, slash_command, SlashOption
from nextcord.ext.commands import Bot

from default import MISSING
from Service.Country import AllCountries
from Discord.Controller.defaults import CountryParameters
from Discord.Controller.Country import delete_country_alliance, get_country_alliance, add_country_alliance, delete_country
from Discord.Cogs.Cog import MyCog
from Discord.Cogs.Items import Lists, Autocomplete


class AllianceLists(Lists):
    alliances: dict[str, str]

    def __init__(self):
        self.update()

    def update(self):
        self.alliances = self._get_alliances()

    def _get_alliances(self) -> dict[str, str]:
        alliances = AllCountries().get_alliance()

        return self._cut_back_items(dict(zip(alliances, alliances)))

g_alliances_lists = AllianceLists()
def alliances_lists() -> AllianceLists:
    return g_alliances_lists


class AllianceAutocomplete(Autocomplete):
    async def alliances(self, cog: MyCog, inter: Interaction, alliance: str):
        await inter.response.send_autocomplete(
                self._get_same_words(alliances_lists().alliances, alliance)
        )

g_alliance_autocomplete = AllianceAutocomplete()
def alliance_autocomplete() -> AllianceAutocomplete:
    return g_alliance_autocomplete

class Country(MyCog):
    @MyCog.curators_and_players_perm()
    @slash_command(name='alliance', description='Посмотреть союзников страны')
    async def alliance(
            self, inter: Interaction,
            player: Member = SlashOption(
                name='игрок',
                description='Игрок, чьих союзников вы хотите увидеть',
                required=False,
                default=MISSING
            )
    ):
        await get_country_alliance(inter, self, player)


    @slash_command(name='country', description='Изменение стран')
    async def country(self, inter: Interaction):
        pass
    
    @MyCog.autocomplete(alliance_autocomplete().alliances, 'alliance')
    @MyCog.curators_perm()
    @country.subcommand(name='add-alliance', description='Добавить в альянс')
    async def add_country_alliance(
            self, inter: Interaction,
            player: Member = SlashOption(
                name='игрок',
                description='Игрок, которого вы добавите в альянс'
            ),
            alliance: str = SlashOption(
                name='альянс',
                description='Альянс в который будет добавлен игрок'
            )
    ):
        await add_country_alliance(inter, self, player, alliance)
        alliances_lists().update()


    @country.subcommand(name='delete')
    async def delete(
            self, inter: Interaction,
            player: Member = SlashOption(
                name='игрок',
                description='Игрок, которого вы хотите изменить',
                required=False,
                default=MISSING
            ),
            for_all_countries: bool = SlashOption(
                name='для-всех-стран',
                description='Изменить все страны',
                required=False,
                default=MISSING
            )
    ):
        pass

    @MyCog.curators_perm()
    @MyCog.add_parent_arguments()
    @delete.subcommand(name='alliance', description='Удалить альянс')
    async def delete_alliance(
            self, inter: Interaction,
            **kwargs
    ):
        await delete_country_alliance(
                inter, self, 
                CountryParameters(self, **kwargs)
        )

    @MyCog.curators_perm()
    @MyCog.add_parent_arguments()
    @delete.subcommand(name='country', description='Удалить страну')
    async def delete_country(
            self, inter: Interaction,
            **kwargs
    ):
        await delete_country(
                inter, self, 
                CountryParameters(self, **kwargs)
        )


def setup(bot: Bot):
    bot.add_cog(Country(bot))
