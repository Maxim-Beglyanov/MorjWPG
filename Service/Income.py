if __name__ == '__main__':
    import sys; sys.path.append('..')
from abc import ABC, abstractmethod
from datetime import timezone, timedelta, datetime, time
import threading

from Database.Database import database


offset = timezone(timedelta(hours=3))

class Observer(ABC):
    """
    Класс наблюдателя, нужен, чтобы публикатор(который выдает доход)
    уведомлял наблюдателей об этом
    
    """

    @abstractmethod
    def update(self):
        pass

class Publisher(ABC):
    """Класс публикатора, который уведомляет наблюдателей(о выдаче дохода)"""

    observers: list[Observer]

    def add_observer(self, observer: Observer):
        self.observers.append(observer)

    def remove_observer(self, observer: Observer):
        self.observers.remove(observer)

    def notify(self):
        for i in self.observers:
            i.update()

class Income(Publisher):
    observers: list[Observer]
    income_time: int
    timer: threading.Timer

    def __init__(self):
        self.observers = []

        self.timer = None
        self.start_timer()
    
    def income(self):
        database().insert('SELECT give_out_income()')
        self.notify()

        self.start_timer()


    def start_timer(self):
        self._get_income_time()
        
        if self.timer:
            self.timer.cancel()

        if self.income_time:
            self.timer = threading.Timer(self.income_time, self.income)
            self.timer.start()
    
    def _get_income_time(self):
        self.income_time = database().select_one(
                'SELECT get_next_income_time(%s) AS income_time',
                datetime.now(offset).time())['income_time']
        if self.income_time:
            self.income_time = abs(self._get_total_seconds(self.income_time) - \
                               self._get_total_seconds(datetime.now(offset).time()))
    
    def _get_total_seconds(self, time_: time) -> int:
        return time_.hour*3600+time_.minute*60
    

    def get_income_times(self):
        income_times = []
        for i in database().select(
            'SELECT income_time '
            'FROM income_times '
            'ORDER BY income_time'
            ):
            income_times.append(str(i['income_time']))
        
        return income_times
    
    def add_income_time(self, time_: time):
        database().insert('INSERT INTO income_times '
                          'VALUES(%s)', time_)
        self.start_timer()

    def delete_income_time(self, time_: time):
        database().insert('DELETE FROM income_times '
                          'WHERE income_time = %s',
                          time_)
        self.start_timer()