from typing import Any


class NoImportantParameter(Exception):
    pass

class NoItem(Exception):
    pass

class CantTransact(Exception):
    def __init__(self, reasons: dict[str, Any]):
        self.reasons = reasons

    def __str__(self) -> str:
        output = []
        for reason in self.reasons:
            if reason == 'builds':
                output.append(self.reasons[reason]) 
            elif reason == 'item':
                output.append('Нехватка предмета: {}'.format(abs(self.reasons['item'])))
            elif reason == 'money':
                output.append('Нехватка денег: {}'.format(abs(int(self.reasons['money']))))
            elif reason == 'buyability':
                output.append('Нельзя купить предмет, его может выдать только куратор')
            elif reason == 'saleability':
                output.append('Нельзя продавать предмет')

        return 'Нельзя совершить транзакцию '+', '.join(output)

class ParametersError(Exception):
    parameter: str

    def __init__(self, parameter: str):
        self.parameter = parameter
    
    def __str__(self) -> str:
        return f'Ошибка параметров: {self.parameter}'

class ThisCountryNotInAlliance(Exception):
    name: str

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return f'Страна {self.name} не состоит в вашем альянсе'
