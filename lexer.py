import os
import sys
from enum import Enum
import re
from typing import Any


# ==================================================
def print_table(table: list[list[Any]] | list[tuple[Any]]):
    if len(table) == 0:    return
    if len(table[0]) == 0: return

    max_size: list[int] = list(0 for j in range(len(table[0])))

    for i in range(len(table)):
        for j in range(len(table[0])):
            max_size[j] = max(max_size[j], len(str(table[i][j])))

    for i in range(len(max_size)):
        max_size[i] = max_size[i] + 2

    # --------------------------------
    def print_upper(sizes: list[int]):
        print('╭', end='')
        for i in range(len(sizes) - 1):
            print('─' * sizes[i], end='')
            print('┬', end='')
        print('─' * sizes[len(sizes) - 1], end='')
        print('╮')

    def print_middle(sizes: list[int]):
        print('├', end='')
        for i in range(len(sizes) - 1):
            print('─' * sizes[i], end='')
            print('┼', end='')
        print('─' * sizes[len(sizes) - 1], end='')
        print('┤')

    def print_down(sizes: list[int]):
        print('╰', end='')
        for i in range(len(sizes) - 1):
            print('─' * sizes[i], end='')
            print('┴', end='')
        print('─' * sizes[len(sizes) - 1], end='')
        print('╯')

    def print_row(sizes: list[int], row: list[Any]):
        print('│', end='')
        for i in range(len(sizes) - 1):
            print(str(row[i]).center(sizes[i]), end='')
            print('│', end='')
        print(str(row[len(sizes) - 1]).center(sizes[len(sizes) - 1]), end='')
        print('│')
    # --------------------------------
    print_upper(max_size)
    for i in range(len(table) - 1):
        print_row(max_size, table[i])
        print_middle(max_size)
    print_row(max_size, table[len(table) - 1])
    print_down(max_size)


# =====================[CONSTS]=====================

FILE_TYPE: str = ".tp"


class CONSOLE_COLORS(Enum):
    ERROR = '\033[31m',
    WARNING = '\033[93m',
    OK = '\033[32m',
    NORMAL = '\033[0m',


TOKENS_TABLE = {
    # Keywords list
    "float": "keyword", "int": "keyword", "bool": "keyword",
    "print": "keyword", "inputInt": "keyword", "inputFloat": "keyword",
    "inputBool": "keyword", "if": "keyword", "while": "keyword",
    "do": "keyword", "for": "keyword", "elif": "keyword",
    "else": "keyword", "switch": "keyword", "case": "keyword",
    "default": "keyword", "flagIf": "keyword",

    # Math
    "=": "op_assign", "+": "op_plus", "-": "op_minus",
    "*": "op_multi", "/": "op_divide", "^": "op_power",

    # Logical
    "and": "op_and", "or": "op_or", "not": "op_not",

    # Comparison
    "==": "op_equal", "!=": "op_not_equal", ">=": "op_bigger_equal",
    "<=": "op_less_equal", "<": "op_less", ">": "op_bigger",

    # Brackets
    "(": "bracket_l", ")": "bracket_r",
    "{": "curve_l", "}": "curve_r",
    "[": "square_l", "]": "square_r",

    # Spacing
    " ": "space", "\t": "tab", "\n": "newline",

    # Special
    ";": "end_statement", "//": "comment", "#": "flag",
    ":": "colon",         "," : "param_separator"
}

IDENTIFIER_TOKEN = {
    11: "ident"
}

STRING_TOKEN = {
    61: "string"
}

LITERAL_TOKENS_TABLE = {
    22: "integer", 211: "real"
}

IDENT_OR_LITERAL = {
    "true": "boolean", "false": "boolean"
}


class CLASS_ALPHABET(Enum):
    MAIN_LETTER = "mainLetter",
    DIGIT = "digit",
    DOT = "dot",
    WHITE_SPACE = "whiteSpace",
    QUOTE = "quote",
    FORWARD_SLASH = "forwardSlash",
    NEW_LINE = "newLine"
    SPECIAL_SIGN = "specialSign",
    OTHER = "other"


REGEX_TO_CLASS_ALPHABET = {
    r"[a-zA-Z$_]": CLASS_ALPHABET.MAIN_LETTER,
    r"[0-9]": CLASS_ALPHABET.DIGIT,
    r"\.": CLASS_ALPHABET.DOT,
    r"[ \t]": CLASS_ALPHABET.WHITE_SPACE,
    r"\"": CLASS_ALPHABET.QUOTE,
    r"/": CLASS_ALPHABET.FORWARD_SLASH,
    r"\n": CLASS_ALPHABET.NEW_LINE,
    r"[,=()\[\]{}#+\-*=\^:;]": CLASS_ALPHABET.SPECIAL_SIGN,
}

STATE_TRANSITION_TABLE = {
    (0, CLASS_ALPHABET.WHITE_SPACE): 0,

    (0, CLASS_ALPHABET.MAIN_LETTER): 1,
    (1, CLASS_ALPHABET.MAIN_LETTER): 1,
    (1, CLASS_ALPHABET.DIGIT): 1,
    (1, CLASS_ALPHABET.OTHER): 11,

    (0, CLASS_ALPHABET.DIGIT): 2,
    (2, CLASS_ALPHABET.DIGIT): 2,
    (2, CLASS_ALPHABET.DOT): 21,
    (21, CLASS_ALPHABET.DIGIT): 21,
    (21, CLASS_ALPHABET.OTHER): 211,
    (2, CLASS_ALPHABET.OTHER): 22,

    (0, CLASS_ALPHABET.SPECIAL_SIGN): 3,

    (0, CLASS_ALPHABET.FORWARD_SLASH): 4,
    (4, CLASS_ALPHABET.OTHER): 41,
    (4, CLASS_ALPHABET.FORWARD_SLASH): 42,
    (42, CLASS_ALPHABET.OTHER): 42,
    (42, CLASS_ALPHABET.NEW_LINE): 5,

    (0, CLASS_ALPHABET.NEW_LINE): 5,

    (0, CLASS_ALPHABET.QUOTE): 6,
    (6, CLASS_ALPHABET.OTHER): 6,
    (6, CLASS_ALPHABET.QUOTE): 61,

    (0, CLASS_ALPHABET.OTHER): 7
}

STATE_START = 0
STATE_FINISH = (11, 211, 22, 3, 41, 5, 61, 7)
STATE_ERROR = (7,)
STATE_PUTBACK = (11, 211, 22, 41)


# ==================================================


def print_console(message: str, message_type: CONSOLE_COLORS = CONSOLE_COLORS.NORMAL):
    print(message_type.value[0] + message + CONSOLE_COLORS.NORMAL.value[0])


# ==================================================


class Lexer_file:
    usage: str = "to be able take char and put back - stream as std::istream"

    def __init__(self, file_path) -> None:
        with open(file_path, "r") as reader:
            self.text = reader.read()
        self.current_char = 0

    def get_char(self) -> str:
        result = self.text[self.current_char]
        self.current_char += 1
        return result

    def unget_char(self):
        self.current_char -= 1

    def empty(self) -> bool:
        return self.current_char == len(self.text) - 1


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
        return ([("Lexeme", "№ appeared")] if add_tittles else []) + table_as_list



class Lexer_literal_table:

    def __init__(self):
        self.__literal_table: dict[int, (str, str)] = {}

    def add(self, lexeme: str, lexeme_type: str) -> str:
        self.__literal_table[len(self.__literal_table) + 1] = (lexeme, lexeme_type)
        return str(len(self.__literal_table))

    def get_table(self, add_tittles: bool = False) -> list:
        table_as_list: list = []
        for item in self.__literal_table.items():
            table_as_list.append((item[1][0], item[1][1], item[0]))
        return ([("Lexeme", "Type", "№ appeared")] if add_tittles else []) + table_as_list

class Lexer_results_table:

    def __init__(self):
        self.__result_table: list[tuple] = []

    def add(self, line_number: int, lexeme: str, token: str, appearance: str):
        self.__result_table.append((line_number, lexeme, token, appearance))

    def get_table(self, add_tittles: bool = False) -> list[tuple]:
        return ([("Line №", "Lexeme", "Token", "#")] if add_tittles else []) + self.__result_table

class Lexer:
    usage: str = "main class produce results"

    def __init__(self, *, work_file: Lexer_file, id_table: Lexer_ident_table, results_table: Lexer_results_table,
                 literal_table: Lexer_literal_table) -> None:
        self.state = 0
        self.stream = work_file

        self.id_table = id_table
        self.literal_table = literal_table

        self.result_table = results_table
        self.line_counter = 1

    @staticmethod
    def character_to_class(character: str) -> CLASS_ALPHABET:
        for regex in REGEX_TO_CLASS_ALPHABET.keys():
            if re.match(regex, character):
                return REGEX_TO_CLASS_ALPHABET[regex]

        return CLASS_ALPHABET.OTHER

    @staticmethod
    def next_state(state: int, character: str) -> int:
        character_type = Lexer.character_to_class(character)
        # ok
        state_tuple = (state, character_type)
        if state_tuple in STATE_TRANSITION_TABLE:
            return STATE_TRANSITION_TABLE[state_tuple]

        # not found
        other_tuple = (state, CLASS_ALPHABET.OTHER)
        if other_tuple in STATE_TRANSITION_TABLE:
            return STATE_TRANSITION_TABLE[other_tuple]

        # error - unreachable code
        print_console("Error -> TP lexer (Runtime): TP lexer internal error, state dead-end", CONSOLE_COLORS.ERROR)
        exit(2)

    def end_lexeme_processing(self, lexeme):
        # New line state or end of comment lexeme (both should be ignored): state 5
        if self.state == 5:
            self.line_counter += 1
            return

        token_type: str = ''
        id_var: str = ''

        if lexeme in TOKENS_TABLE:
            # SPECIAL TOKEN (not literal) : state 3, 41, part 11
            token_type = TOKENS_TABLE[lexeme]

        elif self.state in LITERAL_TOKENS_TABLE:
            # Literal : state 211, 22
            token_type = LITERAL_TOKENS_TABLE[self.state]
            id_var = self.literal_table.add(lexeme, token_type)

        elif lexeme in IDENT_OR_LITERAL:
            # Literal : part 11
            token_type = IDENT_OR_LITERAL[lexeme]
            id_var = self.literal_table.add(lexeme, token_type)

        elif self.state in IDENTIFIER_TOKEN:
            # Identifier : state 11
            id_var: str | None = self.id_table.find(lexeme)
            if id_var is None: id_var = self.id_table.add(lexeme)
            token_type = IDENTIFIER_TOKEN[self.state]

        elif self.state in STRING_TOKEN:
            # String : state 61
            lexeme = lexeme[1:-1]
            token_type = STRING_TOKEN[self.state]
            id_var = self.literal_table.add(lexeme, token_type)

        else:
            # Error : state 7
            print_console(f"Error -> TP lexer (Runtime): unknown lexeme on line {self.line_counter}: {lexeme}",
                          CONSOLE_COLORS.ERROR)
            exit(1)

        self.result_table.add(self.line_counter, lexeme, token_type, id_var)

    def run(self) -> None:
        # self.state = STATE_START
        lexeme: str = ''

        while not self.stream.empty():
            character = self.stream.get_char()
            self.state = Lexer.next_state(self.state, character)

            if self.state == STATE_START: continue  # do nothing

            if self.state not in STATE_PUTBACK:
                lexeme += character
            else:
                self.stream.unget_char()

            if self.state in STATE_FINISH:
                self.end_lexeme_processing(lexeme)
                self.state = STATE_START
                lexeme = ''

        print_console("Success -> TP lexer (Runtime): lexer finished work correctly", CONSOLE_COLORS.OK)

    def print_results(self):
        LINE_LENGTH = 30
        print_console("Lexical table".center(LINE_LENGTH, '='))
        print_table(self.result_table.get_table(True))
        print_console("Identifier table".center(LINE_LENGTH, '='))
        print_table(self.id_table.get_table(True))
        print_console("Literals table".center(LINE_LENGTH, '='))
        print_table(self.literal_table.get_table(True))


    def print_results_to_file(self):
        pass


def main_lexer():
    # get check amount of params
    startup_args: list[str] = sys.argv
    if len(startup_args) < 2:
        print_console("Error -> TP lexer (Startup): no file was provided", CONSOLE_COLORS.ERROR)
        exit(1)
    if len(startup_args) > 2:
        print_console("Error -> TP lexer (Startup): too many parameters were provided", CONSOLE_COLORS.ERROR)
        exit(1)

    # check if param is absolute or relative
    file_path_param = sys.argv[1]
    if not os.path.isabs(file_path_param):
        file_path_param = os.getcwd() + '\\' + file_path_param

    # check if path exists
    if not os.path.isfile(file_path_param):
        print_console(f"Error -> TP lexer (Startup): no file was found by address {file_path_param}",
                      CONSOLE_COLORS.ERROR)
        exit(1)

    print_console(f"TP lexer (Startup): file was found - {file_path_param}", CONSOLE_COLORS.OK)

    # check file type
    if not file_path_param.endswith(FILE_TYPE):
        print_console("Error -> TP lexer (Startup): incorrect file type", CONSOLE_COLORS.ERROR)
        exit(1)

    # ----------------------------------------------
    # setup lexer
    work_file     = Lexer_file(file_path_param)
    id_table      = Lexer_ident_table()
    results_table = Lexer_results_table()
    literal_table = Lexer_literal_table()
    lexer = Lexer(work_file=work_file, id_table=id_table, results_table=results_table, literal_table=literal_table)
    lexer.run()
    lexer.print_results()


if __name__ == '__main__':
    main_lexer()
