if __name__ == '__main__':
    import sys; sys.path.append('..')

from Service.default import _ALL
from Database.Database import database


_ALL_COUNTRIES = _ALL

class Country:
    """
    Интерфейс страны, страны должны выдавать
    информацию о себе для обращения к БД
    
    """
    len_: int
    id_: tuple[int]
    where: str

    def delete(self):
        database().insert(
            'DELETE FROM countries '+self.where
        )


class OneCountry(Country):
    len_: int = 1
    id_: tuple[int]
    where: str

    def __init__(self, name: str):
        self.id_ = database().select_one('SELECT country_id '
                                         'FROM countries '
                                         'WHERE name = %s', name)
        if not self.id_:
            self.id_ = database().select_one('INSERT INTO countries(name)'
                                             'VALUES(%s) RETURNING country_id', 
                                             name)

        self.id_ = (self.id_['country_id'], )
        self.where = f'WHERE country_id = {self.id_[0]}'

class AllCountries(Country):
    len_: int = _ALL_COUNTRIES
    id_: tuple[int] = None
    where: str = ''
