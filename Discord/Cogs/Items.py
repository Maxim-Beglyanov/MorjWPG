import re

from nextcord import Interaction, slash_command, SlashOption
from nextcord.embeds import Embed
from nextcord.ext.commands import Bot
from nextcord.member import Member

from Service.Items import ItemFabric, BuildParameters, UnitParameters
from Discord.Cogs.View import Pages
from Discord.Controller.Items import CommandItemForm, \
                                     create_item, update_item, delete_item, \
                                     buy_item, sell_item
from Discord.Cogs.Cog import MyCog


class ItemLists:
    items: dict[str, dict[str, str]]
    buyable_items: dict[str, dict[str, str]]
    saleable_items: dict[str, dict[str, str]]
    items_with_all: dict[str, dict[str, str]]

    item_groups: dict[str, dict[str, str]]

    def __init__(self):
        self.items = {}
        self.buyable_items = {}
        self.saleable_items = {}
        self.items_with_all = {}

        self.item_groups = {}

        for item in ('builds', 'units'):
            self.update_items(item)

    def update_items(self, item_type: str):
        self.items[item_type] = self._get_items(item_type)
        self.buyable_items[item_type] = self._get_buyable_items(item_type)
        self.saleable_items[item_type] = self._get_saleable_items(item_type)
        self.items_with_all[item_type] = self._get_items_with_all(item_type)
        
        self.item_groups[item_type] = self._get_item_groups(item_type)

    def _get_items(self, item_type: str) -> dict[str, str]:
        item = ItemFabric().get_item(item_type)
        items = self._get_dict_lists(item.get_all_items())

        return self._cut_back_items(items)
    def _get_buyable_items(self, item_type: str) -> dict[str, str]:
        item = ItemFabric().get_item(item_type)
        items = self._get_dict_lists(item.get_buyable_items())

        return self._cut_back_items(items)
    def _get_saleable_items(self, item_type: str) -> dict[str, str]:
        item = ItemFabric().get_item(item_type)
        items = self._get_dict_lists(item.get_saleable_items())

        return self._cut_back_items(items)
    def _get_items_with_all(self, item_type: str) -> dict[str, str]:
        item = ItemFabric().get_item(item_type)
        items = self._get_dict_lists(item.get_all_items())
        items = self._cut_back_items(items)
        items['all'] = 'all'

        return items
    def _get_item_groups(self, item_type: str) -> dict[str, str]:
        item = ItemFabric().get_item(item_type)
        groups = self._get_dict_lists(item.get_groups_name())

        return self._cut_back_items(groups)
    
    def _get_dict_lists(self, list_: list[str]) -> dict[str, str]:
        return dict(zip(list_, list_))

    def _cut_back_items(self, items: dict[str, str]) -> dict[str, str]:
        items_output = {}
        for item in items:
            words = item.split()
            word_index = 0
            while len(' '.join(words)) > 25 and word_index < len(words):
                vowels = list(
                        re.finditer('[уеёыаоэяиюУЕЁЫАОЭЯИЮ]', words[word_index])
                )
                if len(vowels) >= 2:
                    words[word_index] = words[word_index][:vowels[1].start()]

                word_index+=1

            if len(word := ' '.join(words)) > 25:
                continue

            items_output[word] = items[item]

        return items_output

g_item_lists = ItemLists()
def item_lists() -> ItemLists:
    return g_item_lists

class ItemAutocomplete:
    item_type: str

    def __init__(self, item_type: str):
        self.item_type = item_type

    async def items(self, cog: MyCog, inter: Interaction, item: str):
        await inter.response.send_autocomplete(
                self._get_same_words(
                    item_lists().items[self.item_type], item
                )
        )
    async def buyable_items(self, cog: MyCog, inter: Interaction, item: str):
        await inter.response.send_autocomplete(
                self._get_same_words(
                    item_lists().buyable_items[self.item_type], item
                )
        )
    async def saleable_items(self, cog: MyCog, inter: Interaction, item: str):
        await inter.response.send_autocomplete(
                self._get_same_words(
                    item_lists().saleable_items[self.item_type], item
                )
        )
    async def items_with_all(self, cog: MyCog, inter: Interaction, item: str):
        await inter.response.send_autocomplete(
                self._get_same_words(
                    item_lists().items_with_all[self.item_type], item
                )
        )
    async def item_groups(self, cog: MyCog, inter: Interaction, group: str):
        await inter.response.send_autocomplete(
                self._get_same_words(
                    item_lists().item_groups[self.item_type], group
                )
        )

    def _get_same_words(self, words: dict[str, str], word: str) -> dict[str, str]:
        word = word.lower()
        words_output = {}
        for same_word in words:
            if word in same_word.lower():
                words_output[same_word] = words[same_word]
            
        return words_output

builds_autocomplete = ItemAutocomplete('builds')
units_autocomplete = ItemAutocomplete('units')


class CogItems(MyCog):
    @slash_command(name='help', description='Помощь с ботом кураторам')
    async def help(self, inter: Interaction):
        self.page
        help_pages = [
            Embed(
                title='Необходимое для покупки', 
                description=(
                    '**Необходимое для покупки** - параметр необходимых для покупки зданий. '
                    'Он должен указываться по форме: `здание: количество`. '
                    'Также поддерживаются специальные параметры: \n'

                    '\n- **Не должно выполняться(знак !)** - если условие обозначенное таким ' 
                    'параметром будет выполняться, то это условие будет ложным \n'

                    '- **Пропорционально количеству предметов(знак \*)** - означает, ' 
                    'что количество необходимых для покупки зданий будет ' 
                    'пропорционально уже купленным предметам||, то есть если у вас уже есть 1 Пехота,  ' 
                    'для которой вам надо иметь 1 Казарму, то чтобы купить вторую надо иметь уже 2 Казармы||. ' 
                    'Ход с которым увеличивается количество необходимых предметов выражен количеством \n'

                    '\n**Параметры указываются перед формой**, вот так: '
                    '`параметр(тут нет пробела)здание: количество`, '
                    'можно также указать несколько параметров. \n')
            ),
            Embed(
                title='Группы необходимых для покупки',
                description=(
                    'Также поддерживаются **группы необходимых для покупки условий**, ' 
                    'они заключаются в (): `(здание: количество, здание: количество, ...)` '
                    'К группам также применимы следующие параметры: \n'

                    '\n- **Не должно выполняться(знак !)** - означает то же самое, '
                    'что и в случае с одиночными условиями, только относится к целой группе \n'

                    '- **Что-либо из этого(знак |)** - означает, что если соблюдается '
                    'хотя бы одно условие, то игрок может купить предмет \n'

                    '\n**Форма примерно такая же как и в случае с одиночными условиями**: '
                    '`параметр(условие, условие, ...)`. **Группы можно вкладывать друг в '
                    'друга**, а также **применять к основной группе**||(в которой вы начинаете писать)|| '
                    'параметры, необходимо ее просто заключить в скобки и написать перед ней параметры')
            )
        ]

        view = Pages(inter.user, help_pages, timeout=300)
        await inter.response.send_message(embed=help_pages[0], view=view)
        view.msg = await inter.original_message()

    


    @slash_command(name='buy')
    async def buy(
            self, inter: Interaction,
            count: int = SlashOption(
                name='количество',
                description='Количество покупаемого предмета',
                required=False,
                default=1
            )
    ):
        pass

    ITEM_NAME = SlashOption(
            name='имя',
            description='Имя покупаемого предмета'
    )
    @MyCog.autocomplete(builds_autocomplete.buyable_items, 'item_name')
    @MyCog.players_perm()
    @MyCog.add_parent_arguments()
    @buy.subcommand(name='build', description='Купить здание')
    async def buy_build(
            self, inter: Interaction,
            item_name: str = ITEM_NAME,
            **kwargs
    ):
        await buy_item(
                inter, self, 'build',
                item_name, kwargs['count']
        )

    @MyCog.autocomplete(units_autocomplete.buyable_items, 'item_name')
    @MyCog.players_perm()
    @MyCog.add_parent_arguments()
    @buy.subcommand(name='unit', description='Купить юнита')
    async def buy_unit(
            self, inter: Interaction,
            item_name: str = ITEM_NAME,
            **kwargs
    ):
        await buy_item(
                inter, self, 'unit',
                item_name, kwargs['count']
        )


    @slash_command(name='sell')
    async def sell(
            self, inter: Interaction,
            customer: Member = SlashOption(
                name='покупатель',
                description='Игрок, который купит ваш предмет'
            ),
            price: float = SlashOption(
                name='цена',
                description='Цена, за которую покупатель купит предмет'
            ),
            count: int = SlashOption(
                name='количество',
                description='Количество, продаваемого предмета',
                required=False,
                default=1
            )
    ):
        pass

    ITEM_NAME = SlashOption(
            name='имя',
            description='Имя продаваемого предмета'
    )
    @MyCog.autocomplete(builds_autocomplete.saleable_items, 'item_name')
    @MyCog.players_perm()
    @MyCog.add_parent_arguments()
    @sell.subcommand(name='build', description='Продать здание')
    async def sell_build(
            self, inter: Interaction,
            item_name: str = ITEM_NAME,
            **kwargs
    ):
        await sell_item(
                inter, self, 'build',
                item_name=item_name, **kwargs
        )

    @MyCog.autocomplete(units_autocomplete.saleable_items, 'item_name')
    @MyCog.players_perm()
    @MyCog.add_parent_arguments()
    @sell.subcommand(name='unit', description='Продать юнита')
    async def sell_unit(
            self, inter: Interaction,
            item_name: str = ITEM_NAME,
            **kwargs
    ):
        await sell_item(
                inter, self, 'unit',
                item_name=item_name, **kwargs
        )


    @slash_command(name='items')
    async def items(self, inter: Interaction):
        pass

    @items.subcommand(name='add')
    async def add(
            self, inter: Interaction,
            name: str = SlashOption(
                name='имя',
                description='Присваивает имя предмету'
            ),
            price: float = SlashOption(
                name='цена',
                description='Цена за которую будет продаваться предмет'
            ),
            description: str = SlashOption(
                name='описание',
                description='Описание, которое должно пояснять игроку о предмете',
                required=False,
                default=None
            ),
            buyability: bool = SlashOption(
                name='возможность-покупки',
                description='Определяет, смогут ли игроки покупать предмет',
                required=False,
                default=None
            ),
            saleability: bool = SlashOption(
                name='возможность-продажи',
                description=('Определяет, смогут ли игроки продавать '
                             'предмет между собой'),
                required=False,
                default=None
            ),
            needed_for_purchase: str = SlashOption(
                name='необходимо-для-покупки',
                description='Смотри в /help',
                required=False,
                default=None
            )
    ):
        pass

    GROUP_NAME = SlashOption(
            name='группа',
            description='Группа предмета',
            required=False,
            default=None
    )
    @MyCog.autocomplete(builds_autocomplete.item_groups, 'group_name')
    @MyCog.curators_perm()
    @MyCog.add_parent_arguments()
    @add.subcommand(name='build', description='Добавить новое здание') 
    async def add_build(
            self, inter: Interaction,
            income: float = SlashOption(
                name='доход',
                description=('Доход, который будет выдаваться ' 
                             'за каждое здание в ход'),
                required=False,
                default=None
            ),
            group_name: str = GROUP_NAME,
            **kwargs
    ):
        await create_item(
                inter, self, 'build', 
                BuildParameters(
                    income=income, 
                    group_name=group_name,
                    **kwargs
                )
        )
        item_lists().update_items('builds')

    @MyCog.autocomplete(units_autocomplete.item_groups, 'group_name')
    @MyCog.curators_perm()
    @MyCog.add_parent_arguments()
    @add.subcommand(name='unit', description='Добавить нового юнита')
    async def add_unit(
            self, inter: Interaction,
            features: str = SlashOption(
                name='характеристики',
                description=('Характеристики юнита, отделенные от описания. '
                             'определенной формы нет'),
                required=False,
                default=None
            ),
            group_name: str = GROUP_NAME,
            **kwargs
    ):
        await create_item(
                inter, self, 'unit',
                UnitParameters(
                    features=features,
                    group_name=group_name,
                    **kwargs
                )
        )
        item_lists().update_items('units')


    @items.subcommand(name='update')
    async def update(
            self, inter: Interaction,
            
            name: str = SlashOption(
                name='имя',
                description='Новое имя',
                required=False,
                default=None
            ),
            price: float = SlashOption(
                name='цена',
                description='Новая цена',
                required=False,
                default=None
            ),
            description: str = SlashOption(
                name='описание',
                description='Новое описание',
                required=False,
                default=None
            ),
            buyability: bool = SlashOption(
                name='возможность-покупки',
                description='Новая возможность покупки',
                required=False,
                default=None
            ),
            saleability: bool = SlashOption(
                name='возможность-продажи',
                description='Новая возможность продажи',
                required=False,
                default=None
            ),
            needed_for_purchase: str = SlashOption(
                name='необходимо-для-покупки',
                description='Новое необходимое для покупки',
                required=False,
                default=None
            )
    ):
        pass


    ITEM_NAME = SlashOption(
            name='имя-предмета',
            description='Имя изменяемого предмета',
            required=False,
            default=None
    )
    ITEMS_GROUP = SlashOption(
            name='группа-предметов',
            description='Группа изменяемых предметов',
            required=False,
            default=None
    )
    GROUP_NAME = SlashOption(
            name='группа',
            description='Новая группа предмета',
            required=False,
            default=None
    )
    @MyCog.autocomplete(builds_autocomplete.items, 'item_name')
    @MyCog.autocomplete(builds_autocomplete.item_groups, 'items_group')
    @MyCog.autocomplete(builds_autocomplete.item_groups, 'group_name')
    @MyCog.curators_perm()
    @MyCog.add_parent_arguments()
    @update.subcommand(name='build', description='Обновить здания')
    async def update_build(
            self, inter: Interaction,
            item_name: str = ITEM_NAME,
            items_group: str = ITEMS_GROUP,
            income: float = SlashOption(
                name='доход',
                description='Новый доход',
                required=False,
                default=None
            ),
            group_name: str = GROUP_NAME,
            **kwargs
    ):
        await update_item(
                inter, self, 'build', 
                CommandItemForm(
                    'build', 
                    item_name, items_group
                ), 
                BuildParameters(
                    income=income,
                    group_name=group_name,
                    **kwargs
                )
        )
        item_lists().update_items('builds')

    @MyCog.autocomplete(units_autocomplete.items, 'item_name')
    @MyCog.autocomplete(units_autocomplete.item_groups, 'items_group')
    @MyCog.autocomplete(units_autocomplete.item_groups, 'group_name')
    @MyCog.curators_perm()
    @MyCog.add_parent_arguments()
    @update.subcommand(name='unit', description='Обновить юнитов')
    async def update_unit(
            self, inter: Interaction,
            item_name: str = ITEM_NAME,
            items_group: str = ITEMS_GROUP,
            features: str = SlashOption(
                name='характеристики',
                description='Новые характеристики',
                required=False,
                default=None
            ),
            group_name: str = GROUP_NAME,
            **kwargs
    ):
        await update_item(
                inter, self, 'unit', 
                CommandItemForm(
                    'unit', 
                    item_name, items_group
                ), 
                UnitParameters(
                    features=features,
                    group_name=group_name,
                    **kwargs
                )
        )
        item_lists().update_items('units')


    @items.subcommand(name='delete')
    async def delete(self, inter: Interaction):
        pass

    ITEM_NAME = SlashOption(
            name='имя-предмета',
            description='Имя предмета, который будет удален',
            required=False,
            default=None
    )
    ITEMS_GROUP = SlashOption(
            name='группа-предметов',
            description='Группа предметов, которые будут удалены',
            required=False,
            default=None
    )
    @MyCog.autocomplete(builds_autocomplete.items_with_all, 'item_name')
    @MyCog.autocomplete(builds_autocomplete.item_groups, 'items_group')
    @delete.subcommand(name='build', description='Удалить здание')
    async def delete_build(
            self, inter: Interaction,
            item_name: str = ITEM_NAME,
            items_group: str = ITEMS_GROUP
    ):
        await delete_item(
                inter, self, 
                'build', 
                CommandItemForm(
                    'build', 
                    item_name, items_group
                )
        )
        item_lists().update_items('builds')

    @MyCog.autocomplete(units_autocomplete.items_with_all, 'item_name')
    @MyCog.autocomplete(units_autocomplete.item_groups, 'items_group')
    @MyCog.add_parent_arguments()
    @delete.subcommand(name='unit', description='Удалить юнита')
    async def delete_unit(
            self, inter: Interaction,
            item_name: str = ITEM_NAME,
            items_group: str = ITEMS_GROUP
    ):
        await delete_item(
                inter, self, 
                'unit', 
                CommandItemForm(
                    'unit', 
                    item_name, items_group
                )
        )
        item_lists().update_items('units')


def setup(bot: Bot):
    bot.add_cog(CogItems(bot))
