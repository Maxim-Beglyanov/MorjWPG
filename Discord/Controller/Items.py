from dataclasses import dataclass
import sys

from Service.exceptions import CantTransact; sys.path.append('..')
from typing import Any

import regex
from nextcord import Interaction, Member

from Service.Items import ALL_ITEMS, Item, ItemFabric, ItemForm, \
                          ItemParameters, NeededForPurchaseForm, \
                          NeededForPurchaseGroupParameters, NeededForPurchaseGroupForm
from Service.Country import OneCountry
from Controller.exceptions import NoItemsThatName, WrongFormParameter
from Discord.Cogs.Cog import MyCog


def item_parameters(func):
    async def decorator(
            inter: Interaction, cog: MyCog, 
            *args, **kwargs
    ):
        parameters: ItemParameters = args[-1]
        if parameters.needed_for_purchase == '-':
            # Если необходимое для покупки -, то оно удаляется
            parameters.needed_for_purchase = True
        elif parameters.needed_for_purchase:
            needed_for_purchase = parameters.needed_for_purchase
            parameters.needed_for_purchase = NeededForPurchaseGroupForm()

            # Поиск параметров основной группы "!(Мельница: 3, Завод: 2)"
            _GET_NEEDED_FOR_PURCHASE_PARAMETERS_PATTERN = \
                    rf'^([{_SHOULD_NOT_BE}{_ANYTHING}]*)\('

            if needed_for_purchase_parameters := regex.findall(
                    _GET_NEEDED_FOR_PURCHASE_PARAMETERS_PATTERN,
                    needed_for_purchase
            ):
                parameters.needed_for_purchase.parameters = \
                        _get_needed_for_purchase_group_parameters(
                                needed_for_purchase_parameters[0]
                        )
                # Удаляю параметры из основной группы
                needed_for_purchase = regex.sub(
                        _GET_NEEDED_FOR_PURCHASE_PARAMETERS_PATTERN,
                        '', needed_for_purchase
                )

            needed_for_purchase, parameters.needed_for_purchase.needed_for_purchase_groups = \
                    await _get_needed_for_purchase_groups(
                            inter, cog, 
                            needed_for_purchase
                    )
            parameters.needed_for_purchase.needed_for_purchases = \
                    await _get_needed_for_purchases(
                            inter, cog,
                            needed_for_purchase
                    )

        args = list(args)
        args[-1] = parameters
        await func(inter, cog, *args, **kwargs)

    return decorator


_SHOULD_NOT_BE = '!'
_ANYTHING = '|'
def _get_needed_for_purchase_group_parameters(
        parameters: str
) -> NeededForPurchaseGroupParameters:
    """Метод для получения параметров необходимых для покупок зданий
    ВХОД: параметры
    ВЫХОД: параметры необходимого для покупки

    """

    needed_for_purchase_parameters_form = NeededForPurchaseGroupParameters()
    if _SHOULD_NOT_BE in parameters:
        needed_for_purchase_parameters_form.should_not_be = True
    if _ANYTHING in parameters:
        needed_for_purchase_parameters_form.type = 'Any'

    return needed_for_purchase_parameters_form

# Получение групп необходимых для покупки зданий по типу "!|(Мельница: 2, (Завод: 1), Шахта: 3)"
_GET_GROUPS_PATTERN = rf'([{_SHOULD_NOT_BE}{_ANYTHING}]*)\(((?:[^)(]++|(?R))*)\)(, [ ]*)?'
async def _get_needed_for_purchase_groups(
        inter: Interaction, cog: MyCog,
        needed_for_purchase: str
) -> tuple[str, list[NeededForPurchaseGroupForm]]:
    """Метод для получения необходимых для покупки групп
    ВХОД: Interaction, MyCog для взаимодействия с пользователем,
          необходимое для покупки в виде строки
    ВЫХОД: возвращает необходимое для покупки с удаленными группами и 
           список необходимых для покупки групп

    """

    needed_for_purchase_groups = regex.findall(
            _GET_GROUPS_PATTERN, needed_for_purchase
    )

    group_forms = []
    GROUP_PARAMETERS_INDEX = 0
    GROUP_BODY_INDEX = 1
    for group in needed_for_purchase_groups:
        group = list(group)
        needed_for_purchase_group_form = NeededForPurchaseGroupForm()

        if group[GROUP_PARAMETERS_INDEX]:
            needed_for_purchase_group_form.parameters = \
                    _get_needed_for_purchase_group_parameters(
                            group[GROUP_PARAMETERS_INDEX]
                    )

        group[GROUP_BODY_INDEX], needed_for_purchase_group_form.needed_for_purchase_groups = \
                await _get_needed_for_purchase_groups(
                        inter, cog, 
                        group[GROUP_BODY_INDEX]
                )
        needed_for_purchase_group_form.needed_for_purchases = \
                await _get_needed_for_purchases(
                        inter, cog, 
                        group[GROUP_BODY_INDEX]
                )

        group_forms.append(needed_for_purchase_group_form)

    # Удаляю из необходимых для покупки группы
    needed_for_purchase = regex.sub(_GET_GROUPS_PATTERN, '', needed_for_purchase)

    return needed_for_purchase, group_forms


_PROPORTIONALLY = '*'

# Получение необхдимых для покупки зданий "Мельница: 3, *Завод: 1"
_GET_NEEDED_FOR_PURCHASES_PATTERN = rf'([{_SHOULD_NOT_BE}{_PROPORTIONALLY}]*)([а-яА-я\w ]+):[ ]*([+-]?([0-9]*[.])?[0-9]+)'
async def _get_needed_for_purchases(
        inter: Interaction, cog: MyCog,
        needed_for_purchases_input: str
) -> list[NeededForPurchaseForm]:
    """Метод для получение необходимых для покупки зданий в группе
    ВХОД: классы Interaction, MyCog, для взаимодействия с пользователем
          необходимое для покупки в виде строки
    ВЫХОД: массив NeededForPurchaseForm для занесения их в группу

    """

    needed_for_purchases = regex.findall(
            _GET_NEEDED_FOR_PURCHASES_PATTERN, needed_for_purchases_input
    )

    needed_for_purchases_output = []
    PARAMETERS_INDEX = 0
    BUILD_NAME_INDEX = 1
    BUILD_COUNT_INDEX = 2
    for needed_for_purchase in needed_for_purchases:
        build_id = await get_item_id(
                inter, cog, 
                ItemFabric().get_item('build'), 
                needed_for_purchase[BUILD_NAME_INDEX]
        )
        count = float(needed_for_purchase[BUILD_COUNT_INDEX])

        needed_for_purchase_form = NeededForPurchaseForm(build_id, count)

        if _SHOULD_NOT_BE in needed_for_purchase[PARAMETERS_INDEX]:
            needed_for_purchase_form.should_not_be = True
        if _PROPORTIONALLY in needed_for_purchase[PARAMETERS_INDEX]:
            needed_for_purchase_form.proportionally_items = True

        needed_for_purchases_output.append(needed_for_purchase_form)

    return needed_for_purchases_output

@dataclass
class CommandItemForm(ItemForm):
    item_id: int = None
    group: str = None

    def __init__(
            self, item_type: str,
            item_name: str = None, items_group: str = None, 
            *args, **kwargs
    ):
        item = ItemFabric().get_item(item_type)

        self.item_id = None
        self.group = None
        if item_name:
            if item_name == 'all':
                self.item_id = ALL_ITEMS
            else:
                self.item_id = item.get_id_by_concrete_name(item_name)
        elif items_group:
            self.group = items_group



@item_parameters
async def create_item(
        inter: Interaction, cog: MyCog, item_type: str, 
        parameters: ItemParameters
):
    item = ItemFabric().get_item(item_type)
    item.insert(parameters)

    await cog.send(inter, 'Create Item', 'Предмет создан')

@item_parameters
async def update_item(
        inter: Interaction, cog: MyCog, item_type: str, 
        item_form: CommandItemForm, parameters: ItemParameters
):
    item = ItemFabric().get_item(item_type)
    item.update(item_form, parameters)

    await cog.send(inter, 'Update Item', 'Предмет обновлен')

async def delete_item(
        inter: Interaction, cog: MyCog, item_type: str, 
        item_form: CommandItemForm
):
    item = ItemFabric().get_item(item_type)
    item.delete(item_form)
    
    await cog.send(inter, 'Delete Item', 'Предмет удален')


async def buy_item(
        inter: Interaction, cog: MyCog, item_type: str, 
        item_name: str, count: int
):
    await inter.send('В процессе покупки')
    message = await inter.original_message()

    try:
        item = ItemFabric().get_item(item_type)
        country = OneCountry(cog.get_country_name(inter.user))

        item.buy(country, item.get_id_by_concrete_name(item_name), count)
        await message.edit('Предмет куплен')
    except CantTransact as e:
        await message.edit(':x: '+str(e))

async def sell_item(
        inter: Interaction, cog: MyCog, item_type: str, 
        customer: Member, 
        item_name: str,  count: int, price: float
):
    cog.check_player(customer)

    item = ItemFabric().get_item(item_type)
    seller_country = OneCountry(cog.get_country_name(inter.user))
    customer_country = OneCountry(cog.get_country_name(customer))

    switch = await cog.confirm(
        inter, customer, 
        f'{customer.mention}, вы согласны купить {count} {item_name} за {price}?'
    )

    if switch:
        item.sell(
                seller_country, customer_country, 
                item.get_id_by_concrete_name(item_name), count, price
        )
    
        await cog.send(inter, 'Sell Item', 'Предмет продан')


async def get_item_id(
        inter: Interaction, cog: MyCog, 
        item: Item, name: str
) -> int:
    items = item.get_id_by_name(name)
    if len(items) == 0:
        raise NoItemsThatName(name)
    elif len(items) == 1:
        return tuple(items.values())[0]
    else:
        item_id = await cog.question(
                inter, f'Выбери предмет, который ты имел ввиду({name})', items
        )
        return int(item_id)
