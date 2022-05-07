from nextcord import Member, Interaction, slash_command, SlashOption
from nextcord.ext.commands import Bot

from Discord.Controller.Lists import get_shop, get_inventory, \
                                     edit_inventory, \
                                     delete_item_inventory
from Discord.Cogs.Cog import MyCog
from Discord.Cogs.Items import builds_autocomplete, units_autocomplete
from Discord.Controller.defaults import CountryParameters


class Lists(MyCog):
    @slash_command(name='shop')
    async def shop(
            self, inter: Interaction,
            page_number: int = SlashOption(
                name='страница',
                description='Страница с которой начать просмотр магазина',
                required=False,
                default=1
            )
    ):
        pass

    @MyCog.curators_and_players_perm()
    @MyCog.add_parent_arguments()
    @shop.subcommand(name='builds', description='Магазин зданий')
    async def shop_builds(
            self, inter: Interaction,
            **kwargs
    ):
        await get_shop(inter, self, 'build', **kwargs)

    @MyCog.curators_and_players_perm()
    @MyCog.add_parent_arguments()
    @shop.subcommand(name='units', description='Магазин юнитов')
    async def shop_units(
            self, inter: Interaction,
            **kwargs
    ):
        await get_shop(inter, self, 'unit', **kwargs)


    @slash_command(name='inv')
    async def inventory(
            self, inter: Interaction,
            player: Member = SlashOption(
                name='игрок',
                description='Игрок, чей инвентарь вы хотите увидеть',
                required=False,
                default=None
            ),
            page_number: int = SlashOption(
                name='страница',
                description='Страница, с которой вы хотите начать просмотр инвентаря',
                required=False,
                default=1
            )
    ):
        pass

    @MyCog.curators_and_players_perm()
    @MyCog.add_parent_arguments()
    @inventory.subcommand(name='builds', description='Инвентарь зданий')
    async def inventory_builds(
            self, inter: Interaction,
            **kwargs
    ):
        await get_inventory(
                inter, self, 'build',
                **kwargs
        )
    
    @MyCog.curators_and_players_perm()
    @MyCog.add_parent_arguments()
    @inventory.subcommand(name='units', description='Инвентарь юнитов')
    async def inventory_units(
            self, inter: Interaction,
            **kwargs
    ):
        await get_inventory(
                inter, self, 'unit',
                **kwargs
        )


    @slash_command(name='manage-inv')
    async def manage_inventory(self, inter: Interaction):
        pass

    @manage_inventory.subcommand(name='edit')
    async def edit_inventory(
            self, inter: Interaction,
            count: int = SlashOption(
                name='количество',
                description='Количество добавляемого предмета',
                required=False,
                default=1
            ),
            player: Member = SlashOption(
                name='игрок',
                description='Игрок, у которого будет изменен инвентарь',
                required=False,
                default=None
            ),
            for_all_countries: bool = SlashOption(
                name='для-всех-стран',
                description='Изменить инвентари всем игрокам',
                required=False,
                default=False
            )
    ):
        pass

    ITEM_NAME = SlashOption(
            name='имя',
            description='Имя добавляемого предмета'
    )
    @MyCog.autocomplete(builds_autocomplete.items, 'item_name')
    @MyCog.curators_perm()
    @MyCog.add_parent_arguments()
    @edit_inventory.subcommand(name='build', description='Изменить инвентарь зданий')
    async def edit_inventory_build(
            self, inter: Interaction,
            item_name: str = ITEM_NAME,
            **kwargs
    ):
        await edit_inventory(
                inter, self, 'build', 
                CountryParameters(self, **kwargs), item_name,
                kwargs['count']
        )

    @MyCog.autocomplete(units_autocomplete.items, 'item_name')
    @MyCog.curators_perm()
    @MyCog.add_parent_arguments()
    @edit_inventory.subcommand(name='unit', description='Изменить инвентарь зданий')
    async def edit_inventory_unit(
            self, inter: Interaction,
            item_name: str = ITEM_NAME,
            **kwargs
    ):
        await edit_inventory(
                inter, self, 'unit', 
                CountryParameters(self, **kwargs), item_name,
                kwargs['count']     
        )


    @manage_inventory.subcommand(name='delete')
    async def delete_inventory(
            self, inter: Interaction,
            player: Member = SlashOption(
                name='игрок',
                description='Игрок, чей инвентарь будет удален',
                required=False,
                default=None
            ),
            for_all_countries: bool = SlashOption(
                name='для-всех-стран',
                description='Удалить инвентари всем игрокам',
                required=False,
                default=False
            )
    ):
        pass

    ITEM_NAME = SlashOption(
            name='имя',
            description='Имя удаляемого предмета'
    )
    @MyCog.autocomplete(builds_autocomplete.items, 'item_name')
    @MyCog.curators_perm()
    @MyCog.add_parent_arguments()
    @delete_inventory.subcommand(name='build', description='Удалить здание из инвентаря')
    async def delete_inventory_build(
            self, inter: Interaction,
            item_name: str = ITEM_NAME,
            **kwargs
    ):
        await delete_item_inventory(
                inter, self, 'build',                
                CountryParameters(self, **kwargs), item_name,
        )

    @MyCog.autocomplete(units_autocomplete.items, 'item_name')
    @MyCog.curators_perm()
    @MyCog.add_parent_arguments()
    @delete_inventory.subcommand(name='unit', description='Удалить здание из инвентаря')
    async def delete_inventory_unit(
            self, inter: Interaction,
            item_name: str = ITEM_NAME,
            **kwargs
    ):
        await delete_item_inventory(
                inter, self, 'unit',                
                CountryParameters(self, **kwargs), item_name,
        )


def setup(bot: Bot):
    bot.add_cog(Lists(bot))
