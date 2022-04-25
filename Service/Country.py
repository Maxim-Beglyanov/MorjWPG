if __name__ == '__main__':
    import sys; sys.path.append('..')

from default import ALL
from Database.Database import database


ALL_COUNTRIES = ALL

class Country:
    """
    Интерфейс страны, страны должны выдавать
    информацию о себе для обращения к БД
    
    """

    _count: int
    _ids: tuple[int]
    _where: str

    @property
    def count(self) -> int:
        return self._count
    @property
    def ids(self) -> tuple[int]:
        return self._ids
    @property
    def where(self) -> str:
        return self._where

    def delete(self):
        database().insert(
            ''.join(
                ('DELETE FROM countries ',self.where)
            )
        )


class OneCountry(Country):
    _count: int = 1
    _ids: tuple[int]
    _where: str

    def __init__(self, name: str):
        if not (country_ids := database().select_one(
                'SELECT country_id '
                'FROM countries '
                'WHERE name = %s',
                name
        )):
            country_ids = database().select_one(
                    'INSERT INTO countries(name) '
                    'VALUES(%s) ' 
                    'RETURNING country_id', 
                    name
            )

        self._ids = (country_ids['country_id'], )
        self._where = f'WHERE country_id = {self.ids[0]}'

class AllCountries(Country):
    _count: int = ALL_COUNTRIES
    _ids: tuple[int] = None
    _where: str = ''
