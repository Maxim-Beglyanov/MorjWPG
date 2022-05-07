from typing import Any
from abc import ABC, abstractproperty, abstractmethod

from Database.Database import database


class AbstractConfig(ABC):
    @abstractproperty
    def curator_role(self) -> int:
        pass
    @abstractproperty
    def player_role(self) -> int:
        pass
    @abstractproperty
    def publisher_channel(self) -> int:
        pass
    @abstractproperty
    def country_prefix(self) -> str:
        pass

    @abstractmethod
    def set_curator_role_id(self, id: int):
        pass
    @abstractmethod
    def set_player_role_id(self, id: int):
        pass
    @abstractmethod
    def set_publisher_channel_id(self, id: int):
        pass
    @abstractmethod
    def set_country_prefix(self, prefix: str):
        pass

class ConcreteConfig(AbstractConfig):
    _curator_role_id: int
    _player_role_id: int
    _publisher_channel_id: int
    _country_prefix: str

    def __init__(self):
        self._curator_role_id = self._get_id('curator_role')
        self._player_role_id = self._get_id('player_role')
        self._publisher_channel_id = self._get_id('publisher_channel')
        self._country_prefix = self._get_info('country_prefix')
    
    def _get_info(self, column: str) -> Any|None:
        if data := database().select_one(
            f'SELECT {column} '
             'FROM config'
        ):
             return data[column]

    def _get_id(self, column: str) -> int:
        if id_ := self._get_info(column):
            return int(id_)

    @property
    def curator_role(self) -> int:
        return self._get_id('curator_role')
    @property
    def player_role(self) -> int:
        return self._get_id('player_role')   
    @property
    def publisher_channel(self) -> int:
        return self._get_id('publisher_channel')
    @property
    def country_prefix(self) -> str:
        return self._get_info('country_prefix')

    def set_curator_role_id(self, id: int):
        self._curator_role_id = id
        self._change_id(id, 'curator_role')
    def set_player_role_id(self, id: int):
        self._curator_role_id = id
        self._change_id(id, 'player_role')
    def set_publisher_channel_id(self, id: int):
        self._curator_role_id = id
        self._change_id(id, 'publisher_channel')
    def set_country_prefix(self, prefix: str):
        self._country_prefix = prefix
        self._change_config(prefix, 'country_prefix')
        
    def _change_config(self, value, column: str):
        database().insert(
            'UPDATE config '
           f'SET {column} = %s',
            value
        )    

    def _change_id(self, value: int, column: str):
        self._change_config(str(value), column)

conf = ConcreteConfig()

def Config() -> AbstractConfig:
    return conf
