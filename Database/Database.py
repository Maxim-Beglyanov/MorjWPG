if __name__ == '__main__':
    import sys; sys.path.append('..')
import os
import asyncio
from typing import Any, Mapping

import asyncpg
from asyncpg import Pool, create_pool


connection = asyncpg.connection.Connection
cursor = asyncpg.cursor.Cursor

_CURENT_DATABASE_VERSION = 1.4

global pool
pool: Pool

async def get_conn() -> connection:
    return await pool.acquire()
    
async def put_conn(conn: connection):
    await pool.release(conn)


async def insert(sql: str, *values):
    await pool.execute(sql, *values)

async def select(sql: str, *values) -> list[Mapping[str, Any]]:
    return await pool.fetch(sql, *values)

async def select_one(sql: str, *values) -> Any:
    return await pool.fetchval(sql, *values)


async def check_db_exists():
    if not await select(
            'SELECT * '
            'FROM information_schema.tables '
            'WHERE table_name = $1',
            'countries'
    ):
        await _init_db()

async def _init_db():
    with open('Database/create_db.sql', 'r') as r:
        sql = r.read()

    await insert(sql)
    await insert(
        'INSERT INTO config(database_version) '
        'VALUES($1)',
        _CURENT_DATABASE_VERSION
    )


async def check_db_updates():
    database_version = await select_one(
            'SELECT database_version '
            'FROM config '
            'LIMIT 1'
    )

    if database_version < _CURENT_DATABASE_VERSION:
        await _update_db(database_version)

async def _update_db(database_version: float):
    for version in _get_range_versions(database_version):
        with open(f'Database/Versions/{version}.sql') as r:
            sql = r.read()
        
        await insert(sql)

    await insert(
        'UPDATE config '
        'SET database_version = $1',
        _CURENT_DATABASE_VERSION
    )

def _get_range_versions(database_version: float):
    for version in range(int(database_version*10+1), int(_CURENT_DATABASE_VERSION*10+1)):
        yield version/10


async def init():
    global pool
    url = os.environ['DATABASE_URL']
    pool = await create_pool(url, max_size=20)

    await check_db_exists()
    await check_db_updates()
