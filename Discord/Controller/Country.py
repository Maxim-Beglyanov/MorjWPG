from nextcord import Interaction

from Discord.Controller.defaults import CountryParameters
from Discord.Cogs.Cog import MyCog


async def delete_country(
        inter: Interaction, cog: MyCog, 
        country_parameters: CountryParameters
):
    country = country_parameters.as_country(inter, cog)
    country.delete()
    await cog.send(inter, 'Delete Country', 'Я удалил страну')
