from abc import ABC, abstractmethod
from typing import Any

from Database.Database import database
from Service.exceptions import CantTransact


class Transaction(ABC):
    """Класс транзакции, который состоит из 
    проверки возможности транзакции и выполнения транзакции

    """

    def __init__(self, *args):
        conn = database().get_conn()

        try:
            conn.set_isolation_level('READ COMMITTED')
            with conn:
                with conn.cursor() as cur:
                    transact_ability, needed_for_transact = \
                            self._check_transact_ability(cur, *args)

                    if transact_ability:
                        self._transact(cur, *args)
                    else:
                        raise CantTransact(needed_for_transact)
        finally:
            database().put_conn(conn)

    @abstractmethod
    def _check_transact_ability(self, *args) -> tuple[bool, dict[str, Any]]:
        pass

    @abstractmethod
    def _transact(self, *args):
        pass
