if __name__ == '__main__':
    import sys; sys.path.append('..')
from typing import Any

from psycopg2._psycopg import cursor

from Database.Database import database
from Service.Country import Country
from Service.Transaction import Transaction


class Pay(Transaction):
    """
    Операция перевода денег одной страны другой

    """

    def __init__(
        self, 
        country_transfer: Country, country_payee: Country, 
        money: int|float
    ):
        super().__init__(country_transfer, country_payee, money)


    def _check_transact_ability(
        self, cur: cursor, 
        country_transfer: Country, country_payee: Country, 
        money: int|float
    ) -> tuple[bool, dict[str, Any]]:
        assert country_transfer.count == 1 and country_payee.count == 1

        self.pay_ability = True
        self.needed_for_pay = {}

        self.__check_money(cur, country_transfer, money)

        return self.pay_ability, self.needed_for_pay
       
    def __check_money(
            self, cur: cursor, 
            checking_country: Country, 
            money: int|float
    ):
        cur.execute(
                'SELECT get_needed_money(%s, %s)',
                (checking_country.ids[0], money)
        )
                
        needed_money = cur.fetchone()[0]
        if needed_money < 0:
            self.pay_ability = False
            self.needed_for_pay['money'] = needed_money


    def _transact(
        self, cur: cursor, 
        country_transfer: Country, country_payee: Country, 
        money: int|float
    ):
        self.__update_country_transfer_money(cur, country_transfer, money)
        self.__update_country_payee_money(cur, country_payee, money)
        
    def __update_country_transfer_money(
        self, cur: cursor, 
        country_transfer: Country,
        money: int|float
    ):
        cur.execute(
                'UPDATE countries '
                'SET money = money - %s '
                'WHERE country_id = %s',
                (money, country_transfer.ids[0])
        )

    def __update_country_payee_money(
        self, cur: cursor,
        country_payee: Country,
        money: int|float
    ):
        cur.execute(
                'UPDATE countries '
                'SET money = money + %s '
                'WHERE country_id = %s',
                (money, country_payee.ids[0])
        )


class Economy:
    """Класс экономики страны"""

    country: Country

    def __init__(self, country: Country):
        self.country = country

    @property
    def money(self) -> float:
        assert self.country.count == 1

        return database().select_one(
            'SELECT money '
            'FROM countries '
           f'{self.country.where}'
        )['money']

    @property
    def income(self) -> float:
        assert self.country.count == 1

        return database().select_one(
            'SELECT COALESCE(get_income_country(%s), 0) AS income',
            self.country.ids[0]
        )['income']


    def pay(self, country_payee: Country, money: int|float):
        Pay(self.country, country_payee, money)

    def edit_money(self, money: int|float):
        database().insert(
            'UPDATE countries '
            'SET money = money + %s '
           f'{self.country.where}', 
            money
        )

    def delete_money(self):
        database().insert(
            'UPDATE countries '
            'SET money = 0 '
           f'{self.country.where}'
        )
