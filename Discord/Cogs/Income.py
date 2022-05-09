from datetime import time

from nextcord import Interaction, slash_command, SlashOption
from nextcord.ext.commands import Bot

from Discord.Controller.Income import get_income_times, add_income_time, delete_income_time
from Discord.Cogs.Cog import MyCog
from Discord.Cogs.Config import Config
from Service.Income import Income


class CogIncome(MyCog):
    income: Income

    def __init__(self, bot: Bot):
        super().__init__(bot)
        self.income = Income()

        self.income.add_observer(self)
    
    def update(self):
        channel = self.bot.get_channel(Config().publisher_channel)

        self.bot.loop.create_task(channel.send('Я выдал доход'))
    
    
    @MyCog.curators_and_players_perm()
    @slash_command(
            name='income-times',
            description='Посмотреть времена выдачи дохода'
    )
    async def income_times(self, inter: Interaction):
        await get_income_times(inter, self, self.income)
    

    @slash_command(name='income')
    async def income(self, inter: Interaction):
        pass

    @MyCog.curators_perm()
    @income.subcommand(name='get-out', description='Выдать доход')
    async def get_out_income(self, inter: Interaction):
        self.income.income()


    @income.subcommand(name='edit-times')
    async def edit_income_times(
            self, inter: Interaction,
            hour: int = SlashOption(
                name='час',
                description='Час выдачи дохода(в МСК)',
                min_value=0,
                max_value=24
            ),
            minute: int = SlashOption(
                name='минуты',
                description='Минуты выдачи дохода(в МСК)',
                min_value=0,
                max_value=59
            )
    ):
        pass

    @MyCog.curators_perm()
    @MyCog.add_parent_arguments()
    @edit_income_times.subcommand(name='add', description='Добавить время дохода')
    async def add_income_time(
            self, inter: Interaction,
            **kwargs
    ):
        await add_income_time(
                inter, self, self.income, 
                time(**kwargs)
        )
    
    @MyCog.curators_perm()
    @MyCog.add_parent_arguments()
    @edit_income_times.subcommand(name='delete', description='Удалить время дохода')
    async def delete_income_time(
            self, inter: Interaction,
            **kwargs
    ):
        await delete_income_time(
                inter, self, self.income, 
                time(**kwargs)
        )

def setup(bot: Bot):
    bot.add_cog(CogIncome(bot))
