from typing import Any

from Database.Database import get_conn, put_conn
from Service.exceptions import TransactError


class Transaction:
    """Класс транзакции, который состоит из 
    проверки возможности транзакции и выполнения транзакции

    """

    @classmethod
    async def create(cls, self, *args):
        conn = await get_conn()
        try:
            async with conn.transaction(isolation='read_committed'):
                transact_ability, needed_for_transact = \
                        await self._check_transact_ability(conn, *args)

                if transact_ability:
                    await self._transact(conn, *args)
                else:
                    raise TransactError(needed_for_transact)
        finally:
            await put_conn(conn)

    transact_ability = bool
    needed_for_transact = dict[str, Any]
    async def _check_transact_ability(self, *args) -> (transact_ability, needed_for_transact):
        raise NotImplementedError

    async def _transact(self, *args):
        raise NotImplementedError
