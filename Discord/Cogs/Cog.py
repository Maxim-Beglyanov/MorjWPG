from typing import Any

from nextcord import Interaction, Embed, Member
from nextcord.application_command import ApplicationCommand, ApplicationSubcommand, SlashOption
from nextcord.utils import MISSING
from nextcord.ext import application_checks
from nextcord.ext.commands import Bot, Cog

from Discord.Cogs.View import Question, Pages, Confirm
from Discord.Cogs.exceptions import IsntAdministrator, IsntCurator, IsntRuler, NoAnswer
from Discord.Controller.Config import Config


BLUE = 0x8cd1ff

class MyCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    @staticmethod
    def autocomplete(autocomplete, arg: str):
        def decorator(command: ApplicationCommand):
            @command.on_autocomplete(arg)
            async def on_autocomplete(*args, **kwargs):
                await autocomplete(*args, **kwargs)

            return command

        return decorator

    @staticmethod
    def add_parent_arguments():
        def decorator(command: ApplicationSubcommand):
            if 'kwargs' in command.options:
                del(command.options['kwargs'])
            
            parent_req_options, parent_nonreq_options = \
                    MyCog._sort_command_options(command.parent_command)
            command_req_options, command_nonreq_options = \
                    MyCog._sort_command_options(command)

            command.options = parent_req_options | command_req_options |\
                          command_nonreq_options | parent_nonreq_options

            return command
        
        return decorator

    @staticmethod
    def _sort_command_options(
            command: ApplicationSubcommand
    ) -> tuple[dict[str, SlashOption], dict[str, SlashOption]]:
        req_options = {}
        nonreq_options = {}
        for option in command.options:
            if command.options[option].required in (MISSING, True):
                req_options[option] = command.options[option]
            else:
                nonreq_options[option] = command.options[option]

        return req_options, nonreq_options


    async def send(
            self, inter: Interaction,
            title: str, message: str, 
            user: Member=None
    ):
        if not user:
            user = self.bot.user

        embed = Embed(
                title=title,
                description=message,
                color=BLUE
        )
        embed.set_author(name=user.name, 
                         icon_url=user.avatar)

        await inter.send(embed=embed)

    async def question(
            self, inter: Interaction, 
            question: str, values: dict[str, Any]
    ):
        embed = Embed(
                title='Question',
                description=question,
                color=BLUE
        )
        view = Question(inter.user, values)
        await inter.send(embed=embed, view=view)

        await view.wait()
        if view.answer_ == None: raise NoAnswer
        else: return view.answer_

    async def page(
            self, inter: Interaction, 
            title: str, pages: list[str], 
            user: Member=None, page_number: int=1
    ):
        if not user:
            user = self.bot.user

        embeds = []
        for page in pages:
            embed = Embed(
                    title=title,
                    description=page,
                    color=BLUE
            )
            embed.set_author(name=user.name, icon_url=user.avatar)
            embeds.append(embed)
            
        view = Pages(inter.user, embeds, page_number)
        
        page_number -= 1
        await inter.response.send_message(embed=embeds[page_number], view=view)
        view.msg = await inter.original_message()

    
    
    async def confirm(
            self, inter: Interaction, 
            user: Member, message: str
    ) -> bool:
        view = Confirm(user)

        await inter.send(message, view=view)
        
        await view.wait()
        if view.switch_ == None: raise NoAnswer
        else: return view.switch_


    @staticmethod
    def get_country_name(user: Member) -> str:
        for role in user.roles:
            if role.name.startswith(Config().country_prefix):
                return role.name.replace(Config().country_prefix, '')

    @staticmethod
    async def get_player(inter: Interaction, player: Member):
        """Метод для получения пользователя
        Из команд где при неуказании пользователя, 
        подразумевается тот кто вызвал функцию

        """

        try:
            check_player = MyCog.check_player(inter.user)
        except IsntRuler:
            pass

        if player == None and check_player:
            return inter.user
        elif player == None and not check_player:
            raise IsntRuler(inter.user)

        if MyCog.check_curator(inter.user) and MyCog.check_player(player):
           return player


    @staticmethod
    def administrators_perm():
        def check(inter: Interaction):
            return MyCog.check_administrator(inter.user)
        
        return application_checks.check(check)

    @staticmethod
    def curators_and_players_perm():
        def check(inter: Interaction):
            check_curator = False
            check_player = False
            try:
                check_curator = MyCog.check_curator(inter.user)
                check_player = MyCog.check_player(inter.user)

                return True
            except Exception as e:
                if not any((check_curator, check_player)):
                    raise e
                else:
                    return True

        return application_checks.check(check)

    @staticmethod
    def curators_perm():
        def check(inter: Interaction):
            return MyCog.check_curator(inter.user)
        
        return application_checks.check(check)

    @staticmethod
    def players_perm():
        def check(inter: Interaction):
            return MyCog.check_player(inter.user)
        
        return application_checks.check(check)


    @staticmethod
    def check_administrator(user: Member) -> bool:
        if user.guild_permissions.administrator:
            return True
        else:
            raise IsntAdministrator

    @staticmethod
    def check_curator(user: Member) -> bool:
        if user.get_role(Config().curator_role):
            return True
        else:
            raise IsntCurator

    @staticmethod
    def check_player(user: Member) -> bool:
        if user.get_role(Config().player_role):
            return True
        else:
            raise IsntRuler(user)
