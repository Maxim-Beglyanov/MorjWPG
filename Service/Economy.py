if __name__ == '__main__':
    import sys; sys.path.append('..')
import asyncio
from typing import Any

from Database.Database import init, insert, select, select_one, connection
from Service.Country import AllCountries, Country, OneCountry
from Service.Transaction import Transaction


async def money(country: Country) -> float:
    assert country.count == 1

    money = await select_one(
            'SELECT money '
            'FROM countries '
            'WHERE country_id = $1',
            country.ids[0]
    )
    return money

async def income(country: Country) -> float:
    assert country.count == 1

    income = await select_one(
            'SELECT COALESCE(get_income_country(%s), 0)',
            country.ids[0]
    )
    return income


class Pay(Transaction):
    pay_ability: bool
    needed_for_pay: dict[str, Any]

    @classmethod
    async def create(
            cls, country_transfer: Country, country_payee: Country,
            money: int | float
    ):
        self = Pay()
        await super().create(self, country_transfer, country_payee, money)

    transact_ability = bool
    needed_for_transact = dict[str, Any]
    async def _check_transact_ability(
            self, conn: connection, 
            country_transfer: Country, country_payee: Country, 
            money: int | float
    ) -> (transact_ability, needed_for_transact):
        assert country_transfer.count == 1 and country_payee.count == 1
        assert money > 0

        self.__pay_ability = True
        self.__needed_for_pay = {}

        await self.__check_money(conn, country_transfer, money)

        return self.__pay_ability, self.__needed_for_pay
       
    async def __check_money(
            self, conn: connection, 
            country_transfer: Country, 
            money: int | float
    ):
        transfer_money = await conn.fetchval(
                'SELECT money '
                'FROM countries '
                'WHERE country_id = $1',
                country_transfer.ids[0]
        )
                
        if transfer_money < money:
            self.__pay_ability = False
            self.__needed_for_pay['money'] = transfer_money-money


    async def _transact(
            self, conn: connection, 
            country_transfer: Country, country_payee: Country, 
            money: int | float
    ):
        await self.__write_off_transfer_money(conn, country_transfer, money)
        await self.__give_payee_money(conn, country_payee, money)
        
    async def __write_off_transfer_money(
            self, conn: connection, country_transfer: Country, money: int | float
    ):
        await conn.execute(
                'UPDATE countries '
                'SET money = money - $1 '
                'WHERE country_id = $2',
                money, country_transfer.ids[0]
        )

    async def __give_payee_money(
            self, conn: connection, country_payee: Country, money: int | float
    ):
        await conn.execute(
                'UPDATE countries '
                'SET money = money + $1 '
                'WHERE country_id = $2',
                money, country_payee.ids[0]
        )

async def pay(
        country_transfer: Country, country_payee: Country, 
        money: int | float
):
    await Pay.create(country_transfer, country_payee, money)


async def edit_money(country: Country, money: int | float):
    await insert(
            'UPDATE countries '
            'SET money = money + $1 '
           f'{country.where}', 
            money
    )

async def delete_money(country: Country):
    await insert(
            'UPDATE countries '
            'SET money = 0 '
           f'{country.where}'
    )


async def main():
    await init()

if __name__ == '__main__':
    asyncio.run(main())
