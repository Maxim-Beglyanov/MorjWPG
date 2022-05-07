import sys; sys.path.append('..'); sys.path.append('.')

from nextcord import Interaction, Member

from Service.Economy import Economy
from Service.Country import OneCountry
from Discord.Cogs.Cog import MyCog
from Discord.Controller.defaults import CountryParameters


async def get_balance(
        inter: Interaction, cog: MyCog, 
        user: Member
):
    user = await cog.get_player(inter, user)
    country = OneCountry(cog.get_country_name(user))
    economy = Economy(country)

    money = economy.money
    income = economy.income

    await cog.send(inter, 'Balance', f'Деньги: {money}, Доход: {income}', user)

async def edit_money(
        inter: Interaction, cog: MyCog,
        country_parameters: CountryParameters, 
        money: float|int
):
    economy = Economy(country_parameters.as_country(inter, cog))
    economy.edit_money(money)

    await cog.send(inter, 'Edit Money', 'Деньги были изменены')

async def delete_money(
        inter: Interaction, cog: MyCog, 
        country_parameters: CountryParameters
):
    economy = Economy(country_parameters.as_country(inter, cog))
    economy.delete_money()

    await cog.send(inter, 'Delete Money', 'Деньги были у всех удалены')

async def pay(
        inter: Interaction, cog: MyCog,
        payee: Member, money: float
):
    cog.check_player(payee)

    country_payer = OneCountry(cog.get_country_name(inter.user))
    country_payee = OneCountry(cog.get_country_name(payee))

    economy = Economy(country_payer)
    economy.pay(country_payee, money)

    await cog.send(inter, 'Pay', 'Деньги переведены', inter.user)
