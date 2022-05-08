from nextcord import Member, Interaction, slash_command, SlashOption
from nextcord.ext.commands import Bot

from default import MISSING
from Discord.Controller.defaults import CountryParameters
from Discord.Controller.Economy import get_balance, pay, edit_money, delete_money
from Discord.Cogs.Cog import MyCog


class Economy(MyCog):
    @MyCog.curators_and_players_perm()
    @slash_command(name='bal', description='Узнать свой баланс и доход')
    async def get_balance(
            self, inter: Interaction,
            player: Member = SlashOption(
                name='игрок',
                description='Игрок, баланс которого вы хотите посмотреть',
                required=False,
                default=MISSING
            )
    ):
        await get_balance(inter, self, player)

    @MyCog.players_perm()
    @slash_command(name='pay', description='Перевести деньги')
    async def pay(
            self, inter: Interaction,
            payee: Member = SlashOption(
                name='получатель',
                description='Игрок которому придут деньги'
            ),
            money: float = SlashOption(
                name='деньги',
                description='Отправляемые деньги'
            )
    ):
        await pay(inter, self, payee, money)


    @slash_command(name='economy')
    async def economy(self, inter: Interaction):
        pass

    @MyCog.curators_perm()
    @economy.subcommand(
            name='edit-money', 
            description='Изменить деньги стране'
    )
    async def edit_money(
            self, inter: Interaction,
            money: float = SlashOption(
                name='деньги',
                description='Значение на которое изменится баланс'
            ),
            player: Member = SlashOption(
                name='игрок',
                description='Игрок, чей баланс вы хотите изменить',
                required=False,
                default=MISSING
            ),
            for_all_countries: bool = SlashOption(
                name='для-всех-стран',
                description='Если верно, то изменит деньги всем странам',
                required=False,
                default=MISSING
            )
    ):
        await edit_money(
                inter, self, 
                CountryParameters(self, player, for_all_countries), 
                money
        )

    @MyCog.curators_perm()
    @economy.subcommand(
            name='del-money', 
            description='Удалить все деньги стране'
    )
    async def delete_money(
            self, inter: Interaction,
            player: Member = SlashOption(
                name='игрок',
                description='Игрок, чей баланс будет удален',
                required=False,
                default=MISSING
            ),
            for_all_countries: bool = SlashOption(
                name='для-всех-стран',
                description='Если верно, то удалятся все деньги стран',
                required=False,
                default=MISSING
            )
    ):
        await delete_money(
                inter, self, 
                CountryParameters(self, player, for_all_countries)
        )


def setup(bot: Bot):
    bot.add_cog(Economy(bot))
