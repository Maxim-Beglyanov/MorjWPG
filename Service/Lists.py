if __name__ == '__main__':
    import sys; sys.path.append('..')
from typing import Any

from Database.Database import database
from Service.default import _ALL
from Service.Country import AllCountries, Country, OneCountry
from Service.Items import ItemFabric, Item
from Service.exceptions import OperationOnlyForOneCountry

_ALL_ITEMS = _ALL
_ALL_COUNTRIES = _ALL
class List:
    """Класс списков, которые использует предметы"""
    item: Item

class Shop(List):
    item: Item

    def __init__(self, item: Item):
        self.item = item

    def get_shop(self) -> dict[str, dict[str, Any]]:
        shop = {}
        item_name = f'{self.item.arguments_name}_name'

        for i in database().select(
                'SELECT * '
               f'FROM get_{self.item.table_name}_shop()'
        ):
            shop[i.pop(item_name)] = i
            
        return shop

class Inventory(List):
    item: Item
    country: Country

    def __init__(self, item: Item, country: Country):
        self.item = item
        self.country = country

    def get_inventory(self) -> dict[str, dict[str, Any]]:
        assert self.country.len_ == 1

        inventory = {}

        for i in database().select(
                'SELECT * '
               f'FROM get_{self.item.table_name}_inventory(%s)',
                self.country.id_[0]
               ):
            inventory[i.pop('name')] = i

        return inventory

    def edit_inventory(self, item_id: int, count: int):
        if self.country.len_ == _ALL_COUNTRIES:
            countries = database().select('SELECT country_id '
                                          'FROM countries')
            values = []
            for i in countries:
                values.append(f"({i['country_id']}, {item_id}, {count})")
        
        else:
            values = []
            for i in self.country.id_:
                values.append(f"({i}, {item_id}, {count})")

        values = ',\n'.join(values)
        
        item_inventory = f'{self.item.table_name}_inventory'
        id_ = f'{self.item.arguments_name}_id'

        database().insert(f'INSERT INTO {item_inventory}'
                          f'(country_id, {id_}, count) '
                          f'VALUES{values} '
                          f'ON CONFLICT(country_id, {id_}) DO UPDATE '
                          f'SET count = {item_inventory}.count+%s', count)
    
    def delete_inventory_item(self, item_id: int):
        if self.country.len_ == _ALL_COUNTRIES:
            country_where = True
        else:
            country_where = []
            for id_ in self.country.id_:
                country_where.append(str(id_))

            country_where = ', '.join(country_where)
            country_where = f'country_id IN ({country_where})'

        if item_id == _ALL_ITEMS:
            item_where = True
        else:
            item_where = f'{self.item.arguments_name}_id = {item_id}'

        where = f'WHERE {country_where} AND {item_where}'

        database().insert(f'DELETE FROM {self.item.table_name}_inventory '+ where)


class ListFabric:
    """Класс фабрики создания списков"""

    item_fabric: ItemFabric = ItemFabric()

class ShopFabric(ListFabric):
    def get_shop(self, item: str) -> Shop:
        return Shop(self.item_fabric.get_item(item))

class InventoryFabric(ListFabric):
    def get_inventory(self, country: Country, item: str) -> Inventory:
        return Inventory(self.item_fabric.get_item(item), country)


if __name__ == '__main__':
    country = AllCountries()
    inventory = InventoryFabric().get_inventory(country, 'build')

    inventory.delete_inventory_item(-1)
