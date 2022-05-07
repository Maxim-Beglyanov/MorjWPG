class NoItemsThatName(Exception):
    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return f'Предмета с именем {self.name} нет'

class WrongFormParameter(Exception):
    def __init__(self, parameter: str):
        self.parameter = parameter
    
    def __str__(self) -> str:
        return f'Неправильно задана форма в параметре {self.parameter}'
