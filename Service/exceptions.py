from typing import Any


class NoItemError(Exception):
    pass

class TransactError(Exception):
    def __init__(self, reasons: dict[str, Any]):
        self.reasons = reasons

    def __str__(self) -> str:
        output = []
        for reason in self.reasons:
            match reason:
                case 'builds':
                    output.append(self.reasons[reason])
                case 'item':
                    output.append('Нехватка предмета: {}'.format(abs(self.reasons['item'])))

                case 'money':
                    output.append('Нехватка денег: {}'.format(abs(int(self.reasons['money']))))

                case 'buyability':
                    output.append('Нельзя купить предмет')
                case 'saleability':
                    output.append('Нельзя продавать предмет')

        return 'Нельзя совершить транзакцию '+', '.join(output)

class ParametersError(Exception):
    parameter: str

    def __init__(self, parameter: str):
        self.parameter = parameter
    
    def __str__(self) -> str:
        return f'Ошибка параметров: {self.parameter}'


class CountryNotInAllianceError(Exception):
    pass

class GetCountryError(Exception):
    pass
