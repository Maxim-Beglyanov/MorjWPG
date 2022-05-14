from nextcord import Interaction, Member

from Service.Country import OneCountry
from Discord.Controller.defaults import CountryParameters
from Discord.Cogs.Cog import MyCog


async def get_country_alliance(inter: Interaction, cog: MyCog, player: Member):
    if player:
        country = OneCountry(cog.get_country_name(player))
    else:
        country = OneCountry(cog.get_country_name(inter.user))

    alliance, members = country.get_alliance()
    await cog.send(inter, alliance, 'Участники: '+', '.join(members))

async def add_country_alliance(
        inter: Interaction, cog: MyCog, 
        player: Member, alliance: str
):
    country = OneCountry(cog.get_country_name(player))
    country.add_alliance(alliance)

    await cog.send(inter, 'Add Country Alliance', 'Страна добавлена в альянс')

async def delete_country_alliance(
        inter: Interaction, cog: MyCog,
        country_parameters: CountryParameters
):
    country = country_parameters.as_country(inter, cog)
    country.delete_alliance()
    
    await cog.send(inter, 'Delete Alliance', 'Альянс удален')


async def delete_country(
        inter: Interaction, cog: MyCog, 
        country_parameters: CountryParameters
):
    country = country_parameters.as_country(inter, cog)
    country.delete()
    await cog.send(inter, 'Delete Country', 'Я удалил страну')
