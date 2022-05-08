if __name__ == '__main__':
    import sys; sys.path.append('..')
from typing import Any

from Database.Database import database
from default import ALL
from Service.Country import Country
from Service.Items import ItemFabric, Item


class List:
    """Класс списков, которые использует предметы"""
    item: Item

class Shop(List):
    item: Item

    def __init__(self, item: Item):
        self.item = item

    def get_shop(self) -> dict[str, dict[str, Any]]:
        shop = {}

        for item in database().select(
                'SELECT * '
               f'FROM get_{self.item.table_name}_shop()'
        ):
            shop[item.pop('name')] = item
            
        return shop


ALL_ITEMS = ALL
ALL_COUNTRIES = ALL

class Inventory(List):
    item: Item
    country: Country

    def __init__(self, item: Item, country: Country):
        self.item = item
        self.country = country

    def get_inventory(self) -> dict[str, dict[str, Any]]:
        assert self.country.count == 1

        inventory = {}
        for i in database().select(
                'SELECT * '
               f'FROM get_{self.item.table_name}_inventory(%s)',
                self.country.ids[0]
        ):
            inventory[i.pop('name')] = i

        return inventory

    def edit_inventory(self, item_id: int, count: int):
        if self.country.count != ALL_COUNTRIES:
            countries = self.country.ids
        else:
            all_countries = database().select(
                    'SELECT country_id '
                    'FROM countries'
            )
            countries = [country['country_id'] for country in all_countries]

        values = [f'({country}, {item_id}, {count})' for country in countries]
        values = ',\n'.join(values)

        database().insert(
                f'INSERT INTO {self.item.table_name}_inventory'
                f'(country_id, {self.item.arguments_name}_id, count) '
                f'VALUES{values} '
                f'ON CONFLICT(country_id, {self.item.arguments_name}_id) DO UPDATE '
                f'SET count = {self.item.table_name}_inventory.count+%s', 
                count
        )
    
    def delete_inventory_item(self, item_id: int):
        if self.country.count != ALL_COUNTRIES:
            country_where = [str(country_id) for country_id in self.country.ids]
            country_where = ', '.join(country_where)
            country_where = f'country_id IN ({country_where})'

        else:
            country_where = True
            
        if item_id != ALL_ITEMS:
            item_where = f'{self.item.arguments_name}_id = {item_id}'
        else:
            item_where = True
            
        where = f'WHERE {country_where} AND {item_where}'
        database().insert(
                f'DELETE FROM {self.item.table_name}_inventory '+where
        )


class ListFabric:
    """Класс фабрики создания списков"""

    item_fabric: ItemFabric = ItemFabric()

class ShopFabric(ListFabric):
    def get_shop(self, item: str) -> Shop:
        return Shop(self.item_fabric.get_item(item))

class InventoryFabric(ListFabric):
    def get_inventory(self, country: Country, item: str) -> Inventory:
        return Inventory(self.item_fabric.get_item(item), country)
