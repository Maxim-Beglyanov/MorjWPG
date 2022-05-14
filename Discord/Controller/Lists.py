from typing import Any
import sys

sys.path.append('..'); sys.path.append('.')

from nextcord import Member, Interaction

from Service.Items import ItemFabric
from Service.Lists import ShopFabric, InventoryFabric
from Service.Country import OneCountry
from Discord.Cogs.Cog import MyCog
from Discord.Controller.defaults import CountryParameters


async def get_shop(
        inter: Interaction, cog: MyCog, item_type: str, 
        page_number: int=1
):
    shop = ShopFabric().get_shop(item_type)

    shop = shop.get_shop()
    shop = get_list(shop)

    await cog.page(inter, 'Shop', shop, page_number=page_number)


async def get_inventory(
        inter: Interaction, cog: MyCog, item_type: str, 
        player: Member, page_number: int=1
):
    player = await cog.get_player(inter, player)

    country = OneCountry(cog.get_country_name(player))
    inventory = InventoryFabric().get_inventory(country, item_type)

    inventory = inventory.get_inventory()
    inventory = get_list(inventory)

    await cog.page(inter, 'Inventory', inventory, player, page_number)

async def edit_inventory(
        inter: Interaction, cog: MyCog, item_type: str, 
        country_parameters: CountryParameters, 
        item_name: str, count: int
):
    item = ItemFabric().get_item(item_type)
    inventory = InventoryFabric().get_inventory(
            country_parameters.as_country(inter, cog), item_type
    )
    inventory.edit_inventory(
            item.get_id_by_concrete_name(item_name), 
            count
    )

    await cog.send(inter, 'Edit Inventory', 'Инвентарь был изменен')

async def delete_item_inventory(
        inter: Interaction, cog: MyCog, item_type: str,
        country_parameters: CountryParameters, 
        item_name: str
):
    item = ItemFabric().get_item(item_type)
    inventory = InventoryFabric().get_inventory(
            country_parameters.as_country(inter, cog), item_type
    )
    inventory.delete_inventory_item(
            item.get_id_by_concrete_name(item_name)
    )

    await cog.send(inter, 'Delete Item Inventory', 'Предмет удален из инвентаря')


def get_list(list_: dict[str, dict[str, Any]]) -> list[str]:
    pages = []
    
    page = ''
    exist_groups = []

    count = 0
    step = 5
    for item in list_:
        count+=1
        # Добавляю группы
        group = list_[item]['group_name'] 
        list_[item].pop('group_name')
        if group and not group in exist_groups:
            exist_groups.append(group)
            page+=f"\n> **{group}**\n"

        page+=_get_item_parameters(item, list_[item])

        # Если количество предметов достигает шага или это конец листа
        if count%step == 0 or count == len(list_):
            pages.append(page)

            page = ''
    
    return pages

ITEMS_PARAMTERS = {
    'price': 'Цена',
    'count': 'Количество',
    'description': 'Описание',
    'income': 'Доход',
    'features': 'Характеристики',
    'expenses': 'Трата',
    'buyability': 'Способность покупать',
    'saleability': 'Способность продавать',
    'needed_for_purchase': 'Необходимо для покупки'
}
PARAMETERS_VALUES = {
    True: 'Можно',
    False: 'Нельзя'
}
def _get_item_parameters(item_name: str, parameters: dict[str, Any]) -> str:
    item = f"\n**{item_name}**\n"

    for parameter in parameters:
        if parameter in ('buyability', 'saleability', 'needed_for_purchase'):
            if parameters[parameter] == None: continue
            if parameter == 'needed_for_purchase': 
                # Изменяю необходимое для покупки для вывода пользователю
                parameters[parameter] = parameters[parameter][:-2]
            else:
                parameters[parameter] = PARAMETERS_VALUES[parameters[parameter]]

        item += f'{ITEMS_PARAMTERS[parameter]}: {parameters[parameter]}\n'

    return item
