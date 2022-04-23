from typing import Any
import sys

sys.path.append('..'); sys.path.append('.')

from nextcord import Member, Interaction

from Service.Items import ItemFabric
from Service.Lists import ShopFabric, InventoryFabric
from Service.Country import Country, OneCountry, AllCountries
from Discord.Cogs.Cog import MyCog
from Discord.Controller.Items import get_item_id
from Discord.Cogs.exceptions import IsntRuler


async def get_shop(
        inter: Interaction, cog: MyCog, 
        item_type: str, page: int=1
):
    shop = ShopFabric().get_shop(item_type)

    shop = shop.get_shop()
    shop = get_list(shop)

    await cog.page(inter, 'Shop', inter.user, shop, page)


async def get_inventory(
        inter: Interaction, cog: MyCog,
        item_type: str, user: Member, page: int=1
):
    user = await cog.get_player(inter, user)
    country = OneCountry(cog.get_country_name(user))
    inventory = InventoryFabric().get_inventory(country, item_type)

    inventory = inventory.get_inventory()
    inventory = get_list(inventory)

    await cog.page(inter, 'Inventory', user, inventory, page)

async def edit_inventory(
        inter: Interaction, cog: MyCog, item_type: str, 
        user: Member, for_all_countries: bool, 
        item_id: int, count: int
):
    country = await get_country_parameters(inter, cog, user, for_all_countries)
    inventory = InventoryFabric().get_inventory(country, item_type)

    inventory.edit_inventory(item_id, count)

    await cog.send(inter, 'Edit Inventory', 'Инвентарь был изменен')

async def delete_item_inventory(
        inter: Interaction, cog: MyCog, item_type: str,
        user: Member, for_all_countries: bool, item_id: int
):
    country = await get_country_parameters(inter, cog, user, for_all_countries)
    inventory = InventoryFabric().get_inventory(country, item_type)

    inventory.delete_inventory_item(item_id)

    await cog.send(inter, 'Delete Item Inventory', 'Предмет удален из инвентаря')

async def delete_inventory(
        inter: Interaction, cog: MyCog, item_type: str,
        user: Member, for_all_countries: bool
):
    country = await get_country_parameters(inter, cog, user, for_all_countries)
    inventory = InventoryFabric().get_inventory(country, item_type)

    inventory.delete_inventory()

    await cog.send(inter, 'Delete Inventory', 'Инвентарь удален')


_ITEMS_PARAMTERS = {
    'price': 'Цена',
    'count': 'Количество',
    'description': 'Описание',
    'income': 'Доход',
    'features': 'Характеристики',
    'buyability': 'Способность покупать',
    'saleability': 'Способность продавать',
    'needed_for_purchase': 'Необходимо для покупки'
}
_VALUES = {
    True: 'Можно',
    False: 'Нельзя'
}
def get_list(list: dict[str, dict[str, Any]]):
    list_output = []
    
    item_list = ''
    exist_groups = []

    count = 0
    step = 5
    for item in list:
        count+=1
        if list[item]['group_item'] and not list[item]['group_item'] in exist_groups:
            exist_groups.append(list[item]['group_item'])
            item_list+=f"\n> **{list[item]['group_item']}**\n"
        list[item].pop('group_item')

        item_list+=get_item_parameters(item, list[item])

        if count%step == 0 or count == len(list):
            list_output.append(item_list)

            item_list = ''
    
    return list_output

def get_item_parameters(item_name: str, parameters: dict[str, Any]) -> str:
    item = f"\n**{item_name}**\n"

    for parameter in parameters:
        if parameter in ('buyability', 'saleability', 'needed_for_purchase'):
            if parameters[parameter] == None: continue
            if parameter == 'needed_for_purchase': 
                # Изменяю необходимое для покупки для вывода пользователю
                parameters[parameter] = parameters[parameter][:-2]
            else:
                parameters[parameter] = _VALUES[parameters[parameter]]

        item += f'{_ITEMS_PARAMTERS[parameter]}: {parameters[parameter]}\n'

    return item

async def get_country_parameters(inter: Interaction, cog: MyCog, 
                                 user: Member, for_all_countries: bool) -> Country:
    """
    Функция для получения страны из команд по типу: 
    /edit-money player: ... for_all_countries: ...
    
    """
    
    if user:
        return OneCountry(cog.get_country_name(user))
    elif for_all_countries:
        _add_all_countries(inter, cog)
        return AllCountries()
    else:
        await inter.send(':x: Ошибка параметров')
        return

def _add_all_countries(inter: Interaction, cog: MyCog):
    for member in inter.guild.humans:
        try:
            cog.check_player(member)
            OneCountry(cog.get_country_name(member))
        except IsntRuler:
            continue
