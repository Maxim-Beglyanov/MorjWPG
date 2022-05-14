if __name__ == '__main__':
    import sys; sys.path.append('..')

from abc import abstractmethod
from Service.exceptions import ThisCountryNotInAlliance
from default import ALL, MISSING
from Database.Database import database


ALL_COUNTRIES = ALL

class Country:
    """Интерфейс страны 

    Страны должны выдавать информацию о себе для обращения к БД

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
                ('DELETE FROM countries ', self.where)
            )
        )

    @abstractmethod
    def get_alliance(self):
        pass

    def delete_alliance(self):
        database().insert(
                ''.join((
                    'UPDATE countries ',
                    'SET alliance = NULL ',
                    self.where
                ))
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


    def get_alliance(self) -> tuple[str, list[str]]:
        alliance = self.__get_alliance_name()
        alliance_members = []
        if alliance:
            for country in database().select(
                    'SELECT name '
                    'FROM countries '
                    'WHERE alliance = %s',
                    alliance
            ):
                alliance_members.append(country['name'])

        return alliance, alliance_members

    def __get_alliance_name(self) -> str:
        alliance = database().select_one(
                'SELECT alliance '
                'FROM countries '
                'WHERE country_id = %s',
                self.ids[0]
        )['alliance']

        return alliance

    def add_alliance(self, name: str):
        database().insert(
                'UPDATE countries '
                'SET alliance = %s '
                'WHERE country_id = %s',
                name, self.ids[0]
        )


    def get_country(self, name: str) -> Country:
        """Метод для получения страны страной"""
        _, alliance_members = self.get_alliance()

        if name in alliance_members or \
           name == database().select_one(
                   'SELECT name '
                   'FROM countries '
                   'WHERE country_id = %s',
                   self.ids[0]
            ):
               return OneCountry(name)
        else:
            raise ThisCountryNotInAlliance(name)
        

class AllCountries(Country):
    _count: int = ALL_COUNTRIES
    _ids: tuple[int] = MISSING
    _where: str = ''

    def get_alliance(self) -> list[str]:
        alliances = []
        for alliance in database().select(
                'SELECT DISTINCT alliance '
                'FROM countries '
                'WHERE alliance IS NOT NULL'
        ):
            alliances.append(alliance['alliance'])

        return alliances
