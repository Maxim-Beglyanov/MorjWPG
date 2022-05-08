if __name__ == '__main__':
    import sys; sys.path.append('..')
from abc import ABC, abstractmethod
from datetime import time, timezone, timedelta, datetime
import threading

from default import MISSING
from Database.Database import database


offset = timezone(timedelta(hours=3))

class Observer(ABC):
    """Класс наблюдателя, 
    Нужен, чтобы публикатор(который выдает доход) уведомлял наблюдателей об этом
    
    """

    @abstractmethod
    def update(self):
        pass

class Publisher(ABC):
    """Класс публикатора, который уведомляет наблюдателей(о выдаче дохода)"""

    _observers: list[Observer]

    def add_observer(self, observer: Observer):
        self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update()

class Income(Publisher):
    _observers: list[Observer]

    __income_time: int
    __timer: threading.Timer

    def __init__(self):
        self._observers = []

        self.__timer = MISSING
        self.__start_timer()
    
    def income(self):
        database().insert('SELECT give_out_income()')
        self.notify()

        self.__start_timer()


    def __start_timer(self):
        self.__get_income_time()
        
        if self.__timer:
            self.__timer.cancel()

        if self.__income_time:
            self.__timer = threading.Timer(self.__income_time, self.income)
            self.__timer.start()
    
    def __get_income_time(self):
        now_datetime = datetime.now(offset)
        self.__income_time = database().select_one(
                'SELECT get_next_income_time(%s) AS income_time',
                (now_datetime+timedelta(minutes=1)).time()
        )['income_time']

        if self.__income_time:
            now_time = time(hour=now_datetime.hour, minute=now_datetime.minute)
            income_datetime = datetime(
                year=now_datetime.year, 
                month=now_datetime.month, 
                day=now_datetime.day,
                hour=self.__income_time.hour,
                minute=self.__income_time.minute,
                tzinfo=offset
            )
            if now_time>self.__income_time:
                income_datetime+=timedelta(days=1)

            self.__income_time = (income_datetime-now_datetime).seconds


    def get_income_times(self):
        income_times = []
        for time in database().select(
                'SELECT income_time '
                'FROM income_times '
                'ORDER BY income_time'
        ):
            income_times.append(str(time['income_time']))
        
        return income_times
    
    def add_income_time(self, time_: time):
        database().insert(
                'INSERT INTO income_times '
                'VALUES(%s)', 
                time_
        )
        self.__start_timer()

    def delete_income_time(self, time_: time):
        database().insert(
                'DELETE FROM income_times '
                'WHERE income_time = %s',
                time_
        )
        self.__start_timer()
