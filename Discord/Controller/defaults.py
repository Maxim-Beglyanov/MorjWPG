from nextcord import Interaction, Member

from Discord.Cogs.Cog import MyCog
from Discord.Cogs.exceptions import IsntRuler
from Discord.Controller.exceptions import WrongFormParameter
from Service.Country import Country, OneCountry, AllCountries


class CountryParameters:
    player: Member
    for_all_countries: bool

    def __init__(
            self, cog: MyCog, player: Member, for_all_countries: bool, 
            *args, **kwargs
    ):
        self.player = None
        self.for_all_countries = None
        if player and cog.check_player(player):
            self.player = player
        elif for_all_countries:
            self.for_all_countries = for_all_countries
        else:
            raise WrongFormParameter('Страна')

    def as_country(self, inter: Interaction, cog: MyCog) -> Country:
        if self.player:
            country = OneCountry(cog.get_country_name(self.player))
        else:
            _add_all_countries(inter, cog)
            country = AllCountries()

        return country

def _add_all_countries(inter: Interaction, cog: MyCog):
    for user in inter.guild.humans:
        try:
            cog.check_player(user)
            OneCountry(cog.get_country_name(user))
        except IsntRuler:
            continue
