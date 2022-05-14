if __name__ == '__main__':
    import sys; sys.path.append('..')
from typing import Any
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod

from psycopg2._psycopg import cursor

from default import ALL, MISSING
from Database.Database import database
from Service.Transaction import Transaction
from Service.Country import Country
from Service.exceptions import NoImportantParameter, NoItem, ParametersError


ALL_ITEMS = ALL

class Form:
    def asdict(self) -> dict[str, Any]:
        parameters = asdict(self)
        output_parameters = {}

        for parameter in parameters:
            if parameters[parameter] != MISSING: 
                output_parameters[parameter] = parameters[parameter]

        return output_parameters
    
    def keys(self) -> list[str]:
        return list(self.asdict().keys())
    def values(self) -> list[Any]:
        return list(self.asdict().values())

@dataclass
class NeededForPurchaseGroupParameters(Form):
    should_not_be: bool = MISSING
    type: str = MISSING

@dataclass
class NeededForPurchaseForm(Form):
    needed_build_id: int
    count: float|int

    should_not_be: bool = MISSING
    proportionally_items: bool = MISSING

@dataclass
class NeededForPurchaseGroupForm(Form):
    parameters: NeededForPurchaseGroupParameters = NeededForPurchaseGroupParameters()
    needed_for_purchases: list[NeededForPurchaseForm] = field(default_factory=list)
    needed_for_purchase_groups: list = field(default_factory=list)

@dataclass
class ItemParameters(Form):
    name: str
    price: float = MISSING
    description: str = MISSING
    group_name: str = MISSING
    buyability: bool = MISSING
    saleability: bool = MISSING
    needed_for_purchase: NeededForPurchaseGroupForm = MISSING

    def __init__(
            self, name: str, price: float = MISSING,
            description: str = MISSING, group_name: str = MISSING, 
            buyability: bool = MISSING, saleability: bool = MISSING, 
            needed_for_purchase: NeededForPurchaseGroupForm = MISSING,
            *args, **kwargs
    ):
        self.name = name
        self.price = price
        self.description = description
        self.group_name = group_name
        self.buyability = buyability
        self.saleability = saleability
        self.needed_for_purchase = needed_for_purchase
    
    def asdict(self) -> dict[str, Any]:
        parameters = super().asdict()
        if 'needed_for_purchase' in parameters:
            del(parameters['needed_for_purchase'])

        return parameters

@dataclass
class ItemForm(Form):
    """Класс предмета или группы предметов для их изменения"""
    item_id: int = MISSING
    group: str = MISSING

    def __post_init__(self):
        if not any((self.item_id, self.group)):
            raise NoImportantParameter('Предмет')


class Item(ABC):
    """Интерфейс предмета

    Предмет должен предоставлять имя своей таблицы и имя для аргументов.
    А также определять специальные способы покупки или продажи предмета
    
    """

    table_name: str
    arguments_name: str
    
    def insert(self, parameters: ItemParameters):
        """Создание одного предмета в базе данных"""

        columns = self._get_insert_columns(parameters.keys())
        values = self._get_insert_values(parameters.values())

        item_id = database().select_one(
                f'INSERT INTO {self.table_name}{columns} '
                f'VALUES({values}) '
                f'RETURNING {self.arguments_name}_id AS id', 
                *parameters.values()
        )['id']

        self._insert_needed_for_purchase_item(
                item_id, parameters.needed_for_purchase
        )


    @staticmethod                
    def _item_form(func):
        """Декоратор для команд, 
        которые могут получать и id предмета и имя группы

        """

        def decorator(self, item_form: ItemForm, *args, **kwargs):
            if item_form.item_id:
                func(self, item_form.item_id, *args, **kwargs)
            elif item_form.group:
                for item in database().select(
                        f'SELECT {self.arguments_name}_id AS id '
                        f'FROM {self.table_name} '
                         'WHERE group_name = %s',
                         item_form.group
                ):
                    func(self, item['id'], *args, **kwargs)
            else:
                raise ParametersError

        return decorator

    @_item_form
    def update(self, item: ItemForm, parameters: ItemParameters):
        """Обновление одного предмета"""

        if parameters.needed_for_purchase != MISSING:
            database().insert(
                    f'DELETE FROM {self.table_name}_needed_for_purchase '
                    f'WHERE {self.arguments_name}_id = %s; '
                    f'DELETE FROM {self.table_name}_groups_needed_for_purchase '
                    f'WHERE {self.arguments_name}_id = %s',
                    item, item
            )

            self._insert_needed_for_purchase_item(
                    item, parameters.needed_for_purchase
            )

        if columns := self._get_update_values(parameters.keys()):
            database().insert(
                    f'UPDATE {self.table_name} '
                    f'SET {columns} '
                    f'WHERE {self.arguments_name}_id = %s', 
                    *parameters.values(), item
            )

    def _insert_needed_for_purchase_item(
            self, item_id: int, 
            needed_for_purchase: NeededForPurchaseGroupForm
    ):
        """Записывает необходимое для покупки здания предмету"""

        if needed_for_purchase:
            needed_for_purchase_parameters = needed_for_purchase.parameters
            group_needed_for_purchases = needed_for_purchase.needed_for_purchases
            needed_for_purchase_groups = needed_for_purchase.needed_for_purchase_groups

            self._add_needed_for_purchase_group(
                    MISSING, item_id, 
                    needed_for_purchase_parameters,
                    group_needed_for_purchases, 
                    needed_for_purchase_groups
            )

    def _add_needed_for_purchase_group(
            self, group_parent_id: int, item_id: int, 
            parameters: NeededForPurchaseGroupParameters,
            needed_for_purchases: list[NeededForPurchaseForm],
            needed_for_purchase_groups: list[NeededForPurchaseGroupForm]
    ):
        """Добавляет группу необходимых для покупки зданий предмету"""

        group_columns = self._get_needed_for_purchase_parameters(parameters)
        group_values = self._get_needed_for_purchase_values(parameters)

        group_id = database().select_one(
                f'INSERT INTO {self.table_name}_groups_needed_for_purchase{group_columns} '
                f'VALUES({group_values}) '
                f'RETURNING {self.arguments_name}_group_id AS id',
                *parameters.values(), item_id
        )['id']

        if group_parent_id:
            database().insert(
                    f'INSERT INTO {self.table_name}_groups_groups '
                     'VALUES(%s, %s)',
                     group_parent_id, group_id
            )

        self._insert_needed_for_purchase(group_id, item_id, needed_for_purchases)
        if needed_for_purchase_groups:
            for group in needed_for_purchase_groups:
                self._add_needed_for_purchase_group(
                        group_id, item_id,
                        group.parameters, 
                        group.needed_for_purchases,
                        group.needed_for_purchase_groups
                )

    def _insert_needed_for_purchase(
            self, group_id: int, item_id: int,
            needed_for_purchases: list[NeededForPurchaseForm]
    ):
        """Записывает необходимые для покупки здания в группу"""

        for needed_for_purchase in needed_for_purchases:
            needed_for_purchase_columns = \
                    self._get_needed_for_purchase_parameters(needed_for_purchase)
            needed_for_purchase_values = \
                    self._get_needed_for_purchase_values(needed_for_purchase)

            needed_for_purchase_id = database().select_one(
                    f'INSERT INTO {self.table_name}_needed_for_purchase'
                    f'{needed_for_purchase_columns} '
                    f'VALUES({needed_for_purchase_values}) '
                    f'RETURNING {self.arguments_name}_needed_for_purchase_id AS id',
                    *needed_for_purchase.values(), item_id
            )['id']

            database().insert(
                    f'INSERT INTO {self.table_name}_needed_for_purchase_groups '
                     'VALUES(%s, %s) ',
                     group_id, needed_for_purchase_id
            )

    def _get_needed_for_purchase_parameters(
            self, needed_for_purchase: NeededForPurchaseForm|
                                       NeededForPurchaseGroupParameters
    ):
        columns = needed_for_purchase.keys()
        # Добавляю в столбцы поле id, чтобы связать 
        # необходимое для покупки с предметами
        columns.append(f'{self.arguments_name}_id')
        return self._get_insert_columns(columns)

    def _get_needed_for_purchase_values(
            self, needed_for_purchase: NeededForPurchaseForm|
                                       NeededForPurchaseGroupParameters
    ):
        values = needed_for_purchase.values()
        # Добавляю в значения еще одно место для id
        values.append(f'{self.arguments_name}_id')
        return self._get_insert_values(values)
    

    @_item_form
    def delete(self, item: ItemForm):
        """Удалить предмет по id или целую группу по имени"""

        if item != ALL_ITEMS:
            database().insert(
                    f'DELETE FROM {self.table_name} '
                    f'WHERE {self.arguments_name}_id = %s', 
                    item
            )
        else:
            database().insert(
                    f'TRUNCATE TABLE {self.table_name} RESTART IDENTITY CASCADE'
            )

            
    def get_id_by_name(self, name: str) -> dict[str, int]:
        items = {}
        for item in database().select(
                'SELECT name, id '
               f'FROM get_{self.arguments_name}_id_by_name(%s)',
                name
        ):
            items[item['name']] = item['id']

        return items

    def get_id_by_concrete_name(self, name: str) -> int:
        return database().select_one(
                f'SELECT {self.arguments_name}_id AS id '
                f'FROM {self.table_name} '
                 'WHERE name = %s',
                 name
        )['id']

    def get_all_items(self) -> list[str]:
        return self._get_item_names_with_id()
    def get_buyable_items(self) -> list[str]:
        return self._get_item_names_with_id('WHERE buyability = True')
    def get_saleable_items(self) -> list[str]:
        return self._get_item_names_with_id('WHERE saleability = True')

    def _get_item_names_with_id(self, where: str='') -> list[str]:
        items = []
        for item in database().select(
                f'SELECT name '
                f'FROM {self.table_name} '+
                where
        ):
            items.append(item['name'])

        return items

    def get_groups_name(self) -> list[str]:
        groups = []
        for group in database().select(
                f'SELECT DISTINCT group_name AS group '
                f'FROM {self.table_name} '
                 'WHERE group_name IS NOT NULL'
        ):
            groups.append(group['group'])

        return groups
    

    @abstractmethod
    def buy(self, country: Country, item_id: int, count: int):
        pass

    @abstractmethod
    def sell(
            self, country_seller: Country, country_customer: Country,
            item_id: int, count: int, price: float
    ):
        pass


    def _get_insert_columns(self, columns: list[str]) -> str:
        """Создает строку `(column1, column2, ...)` 
        для указания записываемых колонок в БД

        """

        columns_output = '('+', '.join(columns)+')'

        return columns_output

    def _get_insert_values(self, values: list[Any]) -> str:
        """Создает строку `%s, %s, ...` для записи в БД"""

        values_output = ', '.join(('%s', )*len(values))

        return values_output


    def _get_update_values(self, columns: list[str]) -> str:
        """Создает строку `column = %s, column = %s, ...` 
        для обновления записи в БД

        """

        columns = [f'{column} = %s' for column in columns]
        return ', '.join(columns)


class Component(ABC):
    item: Item
    item_id: int
    should_not_be: bool

    @abstractmethod
    def check_buy(self, country: Country, count: int) -> tuple[bool, str]:
        """Проверка на возможность покупки,
        должен передавать на вывод возможность покупки
        и информацию о проверке, чтобы ее вывести в случае неудачи

        """

        pass

    def add_component(self, component):
        pass

    def remove_component(self, component):
        pass

class GroupBehavior(ABC):
    @abstractmethod
    def check_buy(
            self, country: Country, count: int, 
            components: list[Component], should_not_be: bool
    ) -> tuple[bool, str]:
        pass
    
    def _check_components(
            self, country: Country, count: int, 
            components: list[Component], should_not_be: bool
    ):
        for component in components:
            buy_ability, cant_buy_reason = component.check_buy(
                    country, count
            )
            if should_not_be:
                buy_ability = not buy_ability

            yield buy_ability, cant_buy_reason


class NeededForPurchase(Component):
    item: Item
    item_id: int
    needed_build_id: int
    count: int
    should_not_be: bool
    proportionally_items: bool

    def __init__(self, item: Item, needed_for_purchase_id: int):
        needed_for_purchase_info = database().select_one(
               f'SELECT {item.arguments_name}_id, needed_build_id, '
                'count, should_not_be, proportionally_items '
               f'FROM {item.table_name}_needed_for_purchase '
               f'WHERE {item.arguments_name}_needed_for_purchase_id = %s',
                needed_for_purchase_id
        )
        self.item = item
        self.item_id = needed_for_purchase_info[f'{item.arguments_name}_id']
        self.needed_build_id = needed_for_purchase_info['needed_build_id']
        self.count = needed_for_purchase_info['count']
        self.should_not_be = needed_for_purchase_info['should_not_be']
        self.proportionally_items = needed_for_purchase_info[f'proportionally_items']

    def check_buy(self, country: Country, count: int) -> tuple[bool, str]:
        needed_build_count = self._get_needed_build_count(country, count)

        buy_ability = self._check_buy_ability(needed_build_count)
        cant_buy_reason = self._get_cant_buy_reason(needed_build_count)
        
        return buy_ability, cant_buy_reason


    def _get_needed_build_count(self, country: Country, count: int):
        if not self.proportionally_items:
            needed_build_count = self.count
        else:
            country_item_count = database().select_one(
                    f'SELECT get_country_{self.item.arguments_name}_count'
                     '(%s, %s) AS count',
                     country.ids[0], self.item_id
            )['count']
            needed_build_count = (count+country_item_count)*self.count

        needed_build_count = database().select_one(
                'SELECT FLOOR(get_country_build_count(%s, %s)-%s) AS needed_build_count',
                country.ids[0], self.needed_build_id, needed_build_count
        )['needed_build_count']

        # Если у страны не должны иметься эти здания, то количество 
        # становится отрицательным если они имелись и положительным если нет
        if not self.should_not_be:
            return needed_build_count
        else:
            return needed_build_count*-1

    def _check_buy_ability(self, needed_build_count: int) -> bool:
        if not self.should_not_be:
            return needed_build_count>=0
        else:
            return needed_build_count>0

    def _get_cant_buy_reason(self, needed_build_count: int) -> str:
        """Возвращает информацию о проверки, 
        чтобы вывести ее в случае неудачи

        """

        build_name = database().select_one(
                'SELECT name '
                'FROM builds '
                'WHERE build_id = %s',
                self.needed_build_id
        )['name']

        if not self.should_not_be:
            return f'{build_name}: {abs(needed_build_count)}, '
        else:
            return f'{build_name}: {needed_build_count}'


class AllGroupBehavior(GroupBehavior):
    def check_buy(
            self, country: Country, count: int, 
            components: list[Component], should_not_be: bool
    ) -> tuple[bool, str]:
        buy_ability = True
        cant_buy_reason = ''
        for component_buy_ability, component_cant_buy_reason in self._check_components(
                country, count, components, should_not_be
        ):
            if not component_buy_ability:
                buy_ability = False
                cant_buy_reason+=component_cant_buy_reason

        cant_buy_reason = self._get_cant_buy_reason(
                should_not_be, cant_buy_reason
        )
        
        return buy_ability, cant_buy_reason
    
    def _get_cant_buy_reason(
            self, should_not_be: bool, cant_buy_reason: str
    ) -> str:
        if not should_not_be:
            return 'Должны выполняться условия: '+cant_buy_reason
        else:
            return 'Не должны выполняться условия: '+cant_buy_reason
                
class AnyGroupBehavior(GroupBehavior):
    def check_buy(
            self, country: Country, count: int,
            components: list[Component], should_not_be: bool
    ) -> tuple[bool, str]:
        buy_ability = False
        cant_buy_reason = ''
        for component_buy_ability, component_cant_buy_reason in self._check_components(
                country, count, components, should_not_be
        ):
            if component_buy_ability:
                buy_ability = True
                break
            else:
                cant_buy_reason+=component_cant_buy_reason

        cant_buy_reason = self._get_cant_buy_reason(
                should_not_be, cant_buy_reason
        )
        
        return buy_ability, cant_buy_reason
    
    def _get_cant_buy_reason(
            self, should_not_be: bool, cant_buy_reason: str
    ) -> str:
        if not should_not_be:
            return 'Должно выполняться какое либо из условий: '+cant_buy_reason
        else:
            return 'Не должно выполняться какое либо из условий: '+cant_buy_reason


class GroupNeededForPurchase(Component):
    """Класс представляющий группу необходимых для покупки предмета зданий"""

    item: Item
    should_not_be: bool
    type: GroupBehavior
    components: list[Component]

    def __init__(self, item: Item, group_id: int):
        self.components = []

        self._get_group_parameters(item, group_id)
        self._get_group_needed_for_purchases(item, group_id)
        self._get_group_needed_for_purchase_groups(item, group_id)

    def _get_group_parameters(self, item: Item, group_id: int):
        group_info = database().select_one(
                'SELECT should_not_be, type '
               f'FROM {item.table_name}_groups_needed_for_purchase '
               f'WHERE {item.arguments_name}_group_id = %s',
                group_id
        )

        self.should_not_be = group_info['should_not_be']

        match group_info['type']:
            case 'All':
                self.type = AllGroupBehavior()
            case 'Any':
                self.type = AnyGroupBehavior()

    def _get_group_needed_for_purchases(self, item: Item, group_id: int):
        needed_for_purchases = database().select(
               f'SELECT {item.arguments_name}_needed_for_purchase_id AS id '
               f'FROM {item.table_name}_needed_for_purchase_groups '
               f'WHERE {item.arguments_name}_group_id = %s',
                group_id
        )

        for needed_for_purchase in needed_for_purchases:
            self.add_component(NeededForPurchase(item, needed_for_purchase['id']))
    
    def _get_group_needed_for_purchase_groups(self, item: Item, group_id: int):
        needed_for_purchase_groups = database().select(
               f'SELECT included_{item.arguments_name}_group_id AS id '
               f'FROM {item.table_name}_groups_groups '
               f'WHERE {item.arguments_name}_group_id = %s',
                group_id
        )
        for group in needed_for_purchase_groups:
            self.add_component(GroupNeededForPurchase(item, group['id']))


    def check_buy(self, country: Country, count: int) -> tuple[bool, str]:
        buy_ability, cant_buy_reason = self.type.check_buy(
                country, count, self.components, self.should_not_be
        )

        return buy_ability, cant_buy_reason

    def add_component(self, component: Component):
        self.components.append(component)

    def remove_component(self, component: Component):
        self.components.remove(component)

    
class BuyItem(Transaction):
    """Класс покупки предмета"""

    __buy_ability: bool
    __needed_for_buy: dict[str, Any]

    __new_money: float

    def __init__(self, country: Country, item: Item, item_id: int, count: int):
        super().__init__(country, item, item_id, count)

    def _check_transact_ability(
            self, cur: cursor, 
            country: Country, 
            item: Item, item_id: int, count: int
    ):
        assert country.count == 1

        self.__buy_ability = True
        self.__needed_for_buy = {}
                
        if not self.__check_buyability(cur, item, item_id): return
        self.__check_money(cur, country, item, item_id, count)
        self.__check_needed_for_purchase(cur, country, item, item_id, count)

        return self.__buy_ability, self.__needed_for_buy
    
    def __check_buyability(self, cur: cursor, item: Item, item_id: int) -> bool:
        cur.execute(
                'SELECT buyability '
               f'FROM {item.table_name} '
               f'WHERE {item.arguments_name}_id = %s',
                (item_id, )
        )

        return cur.fetchone()[0]

    def __check_money(
        self, cur: cursor, country: Country, item: Item, item_id: int, count: int
    ):
        cur.execute(
                f'SELECT get_needed_price_for_{item.arguments_name}'
                 '(%s, %s, %s) AS money',
                (country.ids[0], item_id, count)
        )
        self.__new_money = cur.fetchone()[0]
        
        if self.__new_money < 0:
            self.__buy_ability = False
            self.__needed_for_buy['money'] = self.__new_money

    def __check_needed_for_purchase(
        self, cur: cursor, country: Country, item: Item, item_id: int, count: int
    ):
        cur.execute(
                f'SELECT {item.arguments_name}_group_id '
                f'FROM {item.table_name}_groups_needed_for_purchase '
                f'WHERE {item.arguments_name}_id = %s',
                 (item_id, )
        )
        if group_id := cur.fetchone():
            group = GroupNeededForPurchase(item, group_id[0])
            group_buy_ability, group_cant_buy_reason = group.check_buy(country, count)

            if not group_buy_ability:
                self.__buy_ability = False
                self.__needed_for_buy['builds'] = group_cant_buy_reason


    def _transact(
        self, cur: cursor, country: Country, item: Item, item_id: int, count: int
    ):
        self.__add_item_to_inventory(cur, country, item, item_id, count)
        self.__write_off_money(cur, country)
        
    def __add_item_to_inventory(
        self, cur: cursor, country: Country, item: Item, item_id: int, count: int
    ):
        cur.execute(
                f'INSERT INTO {item.table_name}_inventory'
                f'(country_id, {item.arguments_name}_id, count) '
                 'VALUES(%s, %s, %s) ' 
                f'ON CONFLICT (country_id, {item.arguments_name}_id) DO UPDATE '
                f'SET count = {item.table_name}_inventory.count + %s',
                (country.ids[0], item_id, count, count)
        )

    def __write_off_money(self, cur: cursor, country: Country):
        cur.execute(
                'UPDATE countries '
                'SET money = %s'
                'WHERE country_id = %s;',
                (self.__new_money, country.ids[0])
        )


class SellItem(Transaction):
    """Класс продажи предмета"""

    __sell_ability: bool
    __needed_for_sell: dict[str, Any]

    __new_seller_item_count: int
    __new_customer_money: float

    def __init__(
            self, country_seller: Country, country_customer: Country, 
            item: Item, item_id: int, count: int, 
            price: float|int
    ):
        super().__init__(
                    country_seller, country_customer, 
                    item, item_id, count, 
                    price
        )

    def _check_transact_ability(
            self, cur: cursor, 
            country_seller: Country, country_customer: Country,
            item: Item, item_id: int, count: int, 
            price: int
    ):
        assert country_seller.count == 1 and country_customer.count == 1

        self.__sell_ability = True
        self.__needed_for_sell = {}

        if not self.__check_saleability(cur, item, item_id): return
        self.__check_seller_item_count(cur, country_seller, item, item_id, count)
        self.__check_customer_money(cur, country_customer, price)

        return self.__sell_ability, self.__needed_for_sell

    def __check_saleability(self, cur: cursor, item: Item, item_id: int) -> bool:
        cur.execute(
                'SELECT saleability '
               f'FROM {item.table_name} '
               f'WHERE {item.arguments_name}_id = %s',
                (item_id, )
        )

        saleability = cur.fetchone()[0]
        if not saleability:
            self.__sell_ability = False
            self.__needed_for_sell['saleability'] = False

        return saleability

    def __check_seller_item_count(
            self, cur: cursor, 
            country_seller: Country, 
            item: Item, item_id: int, count: int
    ):
        cur.execute(
                f'SELECT get_country_{item.arguments_name}_count(%s, %s)-%s',
                 (country_seller.ids[0], item_id, count)
        )

        self.__new_seller_item_count = cur.fetchone()[0]
        if self.__new_seller_item_count < 0:
            self.__sell_ability = False
            self.__needed_for_sell['item'] = self.__new_seller_item_count

    def __check_customer_money(
            self, cur: cursor, 
            country_customer: Country, 
            price: float
    ):
        cur.execute(
                f'SELECT get_needed_money(%s, %s)', 
                (country_customer.ids[0], price)
        )

        self.__new_customer_money = cur.fetchone()[0]
        if self.__new_customer_money < 0.0:
            self.__sell_ability = False
            self.__needed_for_sell['money'] = self.__new_customer_money


    def _transact(
            self, cur: cursor,
            country_seller: Country, country_customer: Country,
            item: Item, item_id: int, count: int, 
            price: int
    ):
        self.__take_away_seller_item(cur, country_seller, item, item_id)
        self.__write_off_customer_money(cur, country_customer)
        
        self.__give_customer_item(cur, country_customer, item, item_id, count)
        self.__give_seller_money(cur, country_seller, price)
        
    def __take_away_seller_item(
            self, cur: cursor, 
            country_seller: Country, 
            item: Item, item_id: int
    ):
        if self.__new_seller_item_count > 0:
            cur.execute(
                    f'UPDATE {item.table_name}_inventory '
                    f'SET count = %s '
                    f'WHERE country_id = %s AND {item.arguments_name}_id = %s',
                    (self.__new_seller_item_count, country_seller.ids[0], item_id)
            )
        else:
            cur.execute(
                    f'DELETE FROM {item.table_name}_inventory '
                    f'WHERE country_id = %s AND {item.arguments_name}_id = %s',
                    (country_seller.ids[0], item_id)
            )

    def __write_off_customer_money(
            self, cur: cursor,
            country_customer: Country
    ):
        cur.execute(
                'UPDATE countries '
                'SET money = %s '
                'WHERE country_id = %s',
                (self.__new_customer_money, country_customer.ids[0])
        )


    def __give_customer_item(
            self, cur: cursor,
            country_customer: Country,
            item: Item, item_id: int, count: int
    ):
        cur.execute(
                f'INSERT INTO {item.table_name}_inventory'
                f'(country_id, {item.arguments_name}_id, count) '
                 'VALUES(%s, %s, %s) ' 
                f'ON CONFLICT (country_id, {item.arguments_name}_id) DO UPDATE '
                f'SET count = {item.table_name}_inventory.count + %s',
                 (country_customer.ids[0], item_id, count, count)
        )

    def __give_seller_money(
            self, cur: cursor,
            country_seller: Country,
            price: float
    ):
        cur.execute(
                'UPDATE countries '
                'SET money = countries.money + %s '
                'WHERE country_id = %s',
                (price, country_seller.ids[0])
        )
       

@dataclass
class BuildParameters(ItemParameters):
    income: float|int = MISSING

    def __init__(
            self, name: str, price: float = MISSING, income: float|int = MISSING,
            description: str = MISSING, group_name: str = MISSING, 
            buyability: bool = MISSING, saleability: bool = MISSING, 
            needed_for_purchase: NeededForPurchaseGroupForm = MISSING, 
            *args, **kwargs
    ):
        super().__init__(
                name, price, 
                description, group_name, 
                buyability, saleability, 
                needed_for_purchase, 
                *args, **kwargs
        )
        self.income = income

class Build(Item):
    table_name: str = 'builds'
    arguments_name: str = 'build'

    def buy(self, country: Country, item_id: int, count: int):
        BuyItem(country, self, item_id, count)
    
    def sell(
            self, country_seller: Country, country_customer: Country,
            item_id: int, count: int, 
            price: int|float
    ):
        SellItem(country_seller, country_customer, self, item_id, count, price)


@dataclass
class UnitParameters(ItemParameters):
    features: str = MISSING
    expenses: float = MISSING

    def __init__(
            self, name: str, price: float = MISSING, features: str = MISSING,
            expenses: float = MISSING, description: str = MISSING, 
            group_name: str = MISSING, 
            buyability: bool = MISSING, saleability: bool = MISSING, 
            needed_for_purchase: NeededForPurchaseGroupForm = MISSING, 
            *args, **kwargs
    ):
        super().__init__(
                name, price, 
                description, group_name, 
                buyability, saleability, 
                needed_for_purchase, 
                *args, **kwargs
        )
        self.features = features
        self.expenses = expenses

class Unit(Item):
    table_name: str = 'units'
    arguments_name: str = 'unit'

    def buy(self, country: Country, item_id: int, count: int):
        BuyItem(country, self, item_id, count)

    def sell(
            self, country_seller: Country, country_customer: Country,
            item_id: int, count: int, 
            price: int|float
    ):
        SellItem(country_seller, country_customer, self, item_id, count, price)


class ItemFabric:
    def get_item(self, item: str) -> Item:
        if item in ('bu', 'build', 'builds'):
            return Build()
        elif item in ('un', 'unit', 'units'):
            return Unit()
        else:
            raise NoItem
