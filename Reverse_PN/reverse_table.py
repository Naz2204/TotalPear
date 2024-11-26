from reverse_semantic_consts import SEMANTIC_TYPE
from Lexer.lexer_print import print_table as lexer_print_table

class Syntax_var_table:
    def __init__(self):
        self.__declared_vars: dict[str, SEMANTIC_TYPE] = {}

    def add(self, name: str, var_type: SEMANTIC_TYPE) -> bool:
        '''
        :return: true - on success, false - if var already exists
        '''
        if name in self.__declared_vars: return False

        self.__declared_vars[name] = var_type
        return True

    def get(self, name: str) -> SEMANTIC_TYPE | None:
        try:
            return self.__declared_vars[name]
        except:
            return None

    def get_table(self) -> tuple[tuple[str, str]]:
        return tuple((i[0], i[1].value) for i in self.__declared_vars.items())

class Label_table:
    def __init__(self):
        self.__table: list[list[str | int]] = [] # [[:label1, 70], [:label2, 16]] - list[str, int]
        self.__PREFIX: str = ":label"
        self.__index: int = 0
        self.__UNDEFINED: int = -1

    def make_label(self) -> int:
        self.__table.append([self.__PREFIX + str(self.__index), self.__UNDEFINED])
        old_index = self.__index
        self.__index += 1
        return old_index

    def change(self, index: int, position: int) -> None:
        self.__table[index][1] = position

    def get_label(self, index: int) -> str:
        to_return: str = ""
        try:
            to_return = self.__table[index][0]
        except IndexError: pass
        return to_return

    def get_table(self) -> list[list[str | int]]:
        return self.__table

    def print(self) ->  None:
        lexer_print_table([["Label name", "Position"]] + self.__table)

    def __dict__(self) -> dict[str, int]:
        return dict((x[0], x[1]) for x in self.__table)
