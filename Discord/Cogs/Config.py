import sys; sys.path.append('.')

from nextcord import Interaction, slash_command, SlashOption, Role
from nextcord.ext.commands import Bot
from nextcord.abc import GuildChannel
from nextcord.enums import ChannelType

from Discord.Cogs.Cog import MyCog
from Discord.Controller.Config import Config



class CogConfig(MyCog):

    @MyCog.administrators_perm()
    @slash_command(name='configs', description='Конфигурации бота')
    async def configs(self, inter: Interaction):
        pass

    @configs.subcommand(
            name='set-curator-role', 
            description='Присвоить роль куратора'
    )
    async def set_curator_role(
            self, inter: Interaction,
            role: Role = SlashOption(
                name='роль',
                description='Роль куратора'
            )
    ):
        Config().set_curator_role_id(role.id)
        
        await self.send(inter, 'Set Curator Role', 'Роль куратора присвоена')
    
    @configs.subcommand(
            name='set-player-role', 
            description='Присвоить роль игрока'
    )
    async def set_player_role(
            self, inter: Interaction,
            role: Role = SlashOption(
                name='роль',
                description='Роль игрока'
            )
    ):
        Config().set_player_role_id(role.id)

        await self.send(inter, 'Set Player Role', 'Роль игрока присвоена')

    @configs.subcommand(
            name='set-publish-channel', 
            description='Присвоить канал публикаций о выдаче дохода'
    )
    async def set_publish_channel(
            self, inter: Interaction,
            channel: GuildChannel = SlashOption(
                name='канал',
                description=('Текстовый канал в который бот будет '
                             'публиковать сообщения о доходе'),
                channel_types=[ChannelType.text]
            )
    ):
        
        Config().set_publisher_channel_id(channel.id)
        
        await self.send(
                inter, 
                'Set Publisher Channel', 
                'Канал для публикации присвоен'
        )
    
    @configs.subcommand(
            name='set-country-prefix', 
            description='Присвоить префикс роли страны'
    )
    async def set_publisher_channel(
            self, inter: Interaction,
            prefix: str = SlashOption(
                name='префикс',
                description='Префикс с которого начинаются имена роли стран'
            )
    ):
        Config().set_country_prefix(prefix)

        await self.send(inter, 'Set Country Prefix', 'Префикс для стран присвоен')


def setup(bot: Bot):
    bot.add_cog(CogConfig(bot))
