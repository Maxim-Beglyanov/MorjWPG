if __name__ == '__main__':
    import sys; sys.path.append('..')
from abc import abstractmethod
import asyncio
from typing import Iterable

from Service.exceptions import CountryNotInAllianceError, GetCountryError
from default import ALL, MISSING
from Database.Database import select, select_one, insert, init


ALL_COUNTRIES = ALL

class Country:
    count: int
    ids: tuple[int]
    where: str

    async def delete(self):
        await insert('DELETE FROM countries '+self.where)

    @abstractmethod
    def get_alliance(self):
        pass

    async def delete_alliance(self):
        await insert(''.join((
                'UPDATE countries ',
                'SET alliance = NULL ',
                self.where
            ))
        )

class Alliance:
    name: str
    members: list[str]

    @classmethod
    async def create(cls, name: str):
        self = Alliance()
        self.name = name
        self.members = await self.__get_members()

        return self

    async def __get_members(self) -> list[str]:
        members = await select(
                'SELECT name '
                'FROM countries '
                'WHERE alliance = $1',
                self.name
        )
        members = [member['name'] for member in members]

        return members


    async def add_country(self, country: Country):
        assert country.count != ALL_COUNTRIES

        await insert(
                'UPDATE countries '
                'SET alliance = $1 '
                'WHERE country_id = ANY($2)',
                self.name, country.ids
        )
        self.members = await self.__get_members()

    async def rename(self, new_name: str):
        await insert(
                'UPDATE countries '
                'SET alliance = $1 '
                'WHERE alliance = $2',
                new_name, self.name
        )
        self.name = new_name

    async def delete(self):
        await insert(
                'UPDATE countries '
                'SET alliance = NULL '
                'WHERE alliance = $1',
                self.name
        )
        self.members = []


class OneCountry(Country):
    count: int = 1
    ids: tuple[int]
    where: str
    
    @classmethod
    async def create(cls, name: str):
        self = OneCountry()
        self.ids = (await self.__get_country_id(name), )
        self.where = f'WHERE country_id = {self.ids[0]}'

        return self
    
    async def __get_country_id(self, name: str) -> int:
        if not (country_id := await select_one(
                'SELECT country_id '
                'FROM countries '
                'WHERE name = $1',
                name
        )):
            country_id = await select_one(
                    'INSERT INTO countries(name) '
                    'VALUES($1) ' 
                    'RETURNING country_id', 
                    name
            )
        
        return country_id

    
    async def get_alliance(self) -> Alliance:
        if alliance := await self.__get_alliance_name():
            alliance = await Alliance.create(alliance)
            return alliance
        else:
            raise CountryNotInAllianceError

    async def __get_alliance_name(self) -> str | None:
        alliance = await select_one(
                'SELECT alliance '
                'FROM countries '
                'WHERE country_id = $1',
                self.ids[0]
        )

        return alliance


    async def get_country(self, name: str) -> Country:
        """Метод для получения страны страной"""
        if await self.__country_is_getting_country(name) or \
           await self.__getting_country_in_alliance(name):
               return await OneCountry.create(name)
        else:
            raise GetCountryError

    async def __country_is_getting_country(self, name: str) -> bool:
        return name == await select_one(
                'SELECT name '
                'FROM countries '
                'WHERE country_id = $1',
                self.ids[0]
        )

    async def __getting_country_in_alliance(self, name: str) -> bool:
        return name in (await self.get_alliance()).members
        

class AllCountries(Country):
    count: int = ALL_COUNTRIES
    ids: None = MISSING
    where: str = ''

    async def get_alliance(self) -> Iterable[Alliance]:
        alliances = []
        for alliance in await select(
                'SELECT DISTINCT alliance '
                'FROM countries '
                'WHERE alliance IS NOT NULL'
        ):
            alliances.append(await Alliance.create(alliance['alliance']))

        return alliances


async def main():
    await init()
    russia = await OneCountry.create('Russia')
    germany = await OneCountry.create('Germany')

    alliance = await Alliance.create('Ja')
    await alliance.add_country(russia)
    await alliance.add_country(germany)

    germany = await russia.get_country('Germany')

if __name__ == '__main__':
    asyncio.run(main())
