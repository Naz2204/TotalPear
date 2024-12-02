class Lexer_ident_table:
    # "to make table of id"

    def __init__(self):
        self.__ident_table: dict[str, int] = {}

    def add(self, lexeme: str) -> str:
        if lexeme in self.__ident_table:
            return str(self.__ident_table[lexeme])

        self.__ident_table[lexeme] = len(self.__ident_table) + 1
        return str(len(self.__ident_table))

    def find(self, lexeme: str) -> str | None:
        if lexeme in self.__ident_table:
            return str(self.__ident_table[lexeme])
        else:
            return None

    def get_table(self, add_tittles: bool = False) -> list:
        table_as_list: list = []
        for item in self.__ident_table.items():
            table_as_list.append(item)
        return ([("Lexeme", "#")] if add_tittles else []) + table_as_list

    def get_dict(self) -> dict:
        return  self.__ident_table


class Lexer_literal_table:

    def __init__(self):
        self.__literal_table: dict[int, tuple[str, str]] = {}
        self.__literal_to_id: dict[str, int] = {}
   
    def add(self, lexeme: str, lexeme_type: str) -> str:
        self.__literal_table[len(self.__literal_table) + 1] = (lexeme, lexeme_type)
        self.__literal_to_id[lexeme] = len(self.__literal_table)
        return str(len(self.__literal_table))

    def find(self, lexeme: str) -> str | None:
        if lexeme in self.__literal_to_id:
            return str(self.__literal_to_id[lexeme])
        else:
            return None

    def get_table(self, add_tittles: bool = False) -> list:
        table_as_list: list = []
        for item in self.__literal_table.items():
            table_as_list.append((item[1][0], item[1][1], item[0]))
        return ([("Lexeme", "Type", "#")] if add_tittles else []) + table_as_list

    def get_dict(self) -> dict:
        return self.__literal_table

class Lexer_results_table:
    
    def __init__(self):
        self.__result_table: list[tuple] = []

    def add(self, line_number: int, lexeme: str, token: str, appearance: str):
        self.__result_table.append((line_number, lexeme, token, appearance))

    def get_table(self, add_tittles: bool = False) -> list[tuple]:
        return ([("Line", "Lexeme", "Token", "#")] if add_tittles else []) + self.__result_table