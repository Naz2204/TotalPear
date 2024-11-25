from reverse_print import print_console
from reverse_syntax_consts import *

class Syntax_input:
    def __init__(self, lexer_result: tuple[dict, dict, list]):
        self.__lexer_id: dict       = lexer_result[0]
        self.__lexer_literals: dict = lexer_result[1]
        self.__lexer_table: list    = lexer_result[2]

        self.__table_iterator: int = 0
        self.__line: int           = 0

    def get_token(self) -> tuple[str, TOKEN_TYPES | KEYWORDS | VALUE_TYPES]:
        """
        :return: (token, type) or None on EOF
        """
        if self.__table_iterator >= len(self.__lexer_table):
            # self.__table_iterator = len(self.__lexer_table) - unget should be called
            self.__table_iterator += 1
            return "eof", TOKEN_TYPES.EOF

        next_value = self.__lexer_table[self.__table_iterator]
        self.__table_iterator += 1

        self.__line = next_value[0]
        value = next_value[1]
        token_type = next_value[2]
        try:
            if token_type == "keyword":
                return value, KEYWORDS(value)
            elif token_type in VALUE_TYPES_VALUES:
                return value, VALUE_TYPES(token_type)
            else:
            # FIXME fix if value errors start to raise too often
                return value, TOKEN_TYPES(token_type, value)
        except ValueError:
            print_console("Error -> TP (Syntax): Unknown token, incorrect lexer results", CONSOLE_COLORS.ERROR)
            exit(1)

    def unget(self, amount: int) -> None:
        # FIXME update line counter
        if self.__table_iterator - amount >= 0:
            self.__table_iterator -= amount
            return
        print_console("Error -> TP (Internal): Broken token stream - incorrect behaviour", CONSOLE_COLORS.ERROR)
        exit(1)

    def get_current_token_number(self) -> int:
        return self.__table_iterator

    def get_line (self) -> int:
        return self.__line

    def is_empty(self) -> bool:
        return self.__table_iterator >= len(self.__lexer_table)