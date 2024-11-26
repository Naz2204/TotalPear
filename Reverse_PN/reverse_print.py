import json
from reverse_table import Syntax_var_table, Label_table
from reverse_syntax_consts import CONSOLE_COLORS, KEYWORDS, TOKEN_TYPES, VALUE_TYPES, RPN_TYPES
from Lexer.lexer_print import print_table as lexer_print_table

FILE_TYPE_OUT = ".postfix"


def print_console(message: str, message_type: CONSOLE_COLORS = CONSOLE_COLORS.NORMAL):
    print(message_type.value + message + CONSOLE_COLORS.NORMAL.value)

class Syntax_print:
    def __init__(self, is_verbose: bool):
        self.__indentation = 0
        self.__INDENTATION = "│  "
        self.__prepared_print: list[str] = []

        if not is_verbose:
            Syntax_print.prepare_print_function = lambda obj, text : None
            Syntax_print.discard_print_function = lambda obj       : None
            Syntax_print.accept_print_function  = lambda obj       : None

    @staticmethod
    def token_to_str(token: TOKEN_TYPES | KEYWORDS | VALUE_TYPES) -> str:
        if type(token) in [KEYWORDS, VALUE_TYPES]:
            return str(token.value)
        else:
            return token.value[1]

    @staticmethod
    def token_to_type_str(token: TOKEN_TYPES | KEYWORDS | VALUE_TYPES) -> str:
        if type(token) in [KEYWORDS, VALUE_TYPES]:
            return str(token.value)
        else:
            return token.value[1]

    def prepare_print_function(self, function_name: str) -> None:
        self.__prepared_print.append((self.__INDENTATION * self.__indentation) + function_name + "():")
        self.increase_indentation()

    def discard_print_function(self) -> None:
        self.__prepared_print.pop()
        self.decrease_indentation()

    def accept_print_function(self) -> None:
        self.decrease_indentation()
        for x in self.__prepared_print:
            print_console(x)

        self.__prepared_print.clear()


    def print_lexeme(self, line: str, value: str, token_type: TOKEN_TYPES | KEYWORDS | VALUE_TYPES) -> None:
        print_console((self.__INDENTATION * self.__indentation) + f"line {line} - {value} of type {self.token_to_type_str(token_type)}")

    def increase_indentation(self):
        self.__indentation += 1

    def decrease_indentation(self):
        if self.__indentation == 0:
            print_console("Error -> TP (Internal): Broken indentations - possible incorrect behavior", CONSOLE_COLORS.ERROR)
            exit(1)

        self.__indentation -= 1

    def print_incorrect_found_error(self,
                                    found: tuple[str, TOKEN_TYPES | KEYWORDS | VALUE_TYPES],
                                    expected: list[TOKEN_TYPES | KEYWORDS | VALUE_TYPES],
                                    error_line_num: int):

        if found[1] == TOKEN_TYPES.EOF:
            to_print = "Error -> TP (Syntax): Unexpected EOF\nExpected: "
        else:
            found_str1 = str(found[0])
            found_str2 = self.token_to_type_str(found[1])

            found_str = found_str1 + " of type " + found_str2 if found_str1 != found_str2 else found_str1

            to_print = ("Error -> TP (Syntax): Unexpected element on line " + str(error_line_num) + "\n" +
                        "Found element: '" + found_str + "'\n" +
                        "Expected: ")

        for i in range(len(expected) - 1):
            to_print += f"'{self.token_to_str(expected[i])}', "
        to_print += (f"'{self.token_to_str(expected[-1])}'")

        print_console(to_print, CONSOLE_COLORS.ERROR)


    def print_lexeme_error(self, error_line_num: int):
        """
        :param error_line_num: Line where error occurred
        """
        print_console("Error -> TP (Syntax): Unexpected lexeme on line " + str(error_line_num), CONSOLE_COLORS.ERROR)

    def print_no_token_error(self, error_line_num: int):
        """
        :param error_line_num: Line where error occurred
        """
        print_console("Error -> TP (Syntax): Token missing on line " + str(error_line_num), CONSOLE_COLORS.ERROR)


    def print_semantic_error(self, error_line_num: int, error_text: str):
        """
        :param error_line_num: Line where error occurred
        """
        print_console("Error -> TP (Semantic): " + error_text + " on line " + str(error_line_num), CONSOLE_COLORS.ERROR)

# ----------------------------------------------------------------

class RPN_out:
    def __init__(self, is_verbose: bool):
        self.__RPN_table: list[tuple[str, str]] = []
        self.__operators_buffer: list[tuple[TOKEN_TYPES, int]] = []
        self.__last_index = 0

        # якщо пріоритет токену на вході більше ніж у буфері - то більший вибиває менше
        # менше число не може вибити більше
        # більше число вибиває менше

        # таким чином більший пріоритет обрахунку = менше число-пріоритет

        # 1 + 2 ^ 3 -> +: 2, ^: 1
        # 1 2 3 ^ +       stack: +,     in: ^

        self.__priority_dict: dict[TOKEN_TYPES, int] = {
            TOKEN_TYPES.OP_POWER:   1,

            TOKEN_TYPES.OP_UMINUS:  2,
            TOKEN_TYPES.OP_NOT:     2,

            TOKEN_TYPES.OP_MULTI:   3,
            TOKEN_TYPES.OP_DIVIDE:  3,
            TOKEN_TYPES.OP_AND:     3,

            TOKEN_TYPES.OP_PLUS:    4,
            TOKEN_TYPES.OP_MINUS:   4,
            TOKEN_TYPES.OP_OR:      4,

            TOKEN_TYPES.OP_BIGGER:       5,
            TOKEN_TYPES.OP_BIGGER_EQUAL: 5,
            TOKEN_TYPES.OP_LESS:         5,
            TOKEN_TYPES.OP_LESS_EQUAL:   5,
            TOKEN_TYPES.OP_EQUAL:        5,
            TOKEN_TYPES.OP_NOT_EQUAL:    5,

            TOKEN_TYPES.BRACKET_R:       6,
            TOKEN_TYPES.BRACKET_L:       7,

            TOKEN_TYPES.OP_OUT_STR:   20,
            TOKEN_TYPES.OP_OUT_INT:   20,
            TOKEN_TYPES.OP_OUT_FLOAT: 20,
            TOKEN_TYPES.OP_OUT_BOOL:  20,

            TOKEN_TYPES.OP_INPUT_INT:   21,
            TOKEN_TYPES.OP_INPUT_FLOAT: 21,
            TOKEN_TYPES.OP_INPUT_BOOL:  21,

            # TOKEN_TYPES.OP_CAST_FLOAT_TO_INT: 30,
            # TOKEN_TYPES.OP_CAST_INT_TO_FLOAT: 30,

            TOKEN_TYPES.OP_ASSIGN: 50,

            TOKEN_TYPES.OP_JMP: 60,
            TOKEN_TYPES.OP_JF: 60,
            TOKEN_TYPES.OP_JT: 60,

            TOKEN_TYPES.END_STATEMENT: 100,

            TOKEN_TYPES.CURVE_R: 199,
            TOKEN_TYPES.CURVE_L: 200,
        }


        if not is_verbose:
            RPN_out.print_to_console = lambda obj : None

    def __del__(self):
        self.print_to_console()

    def add(self, token_type: RPN_TYPES | TOKEN_TYPES | VALUE_TYPES, lexeme: str | None = None) -> int:
        """
        :param lexeme: lexeme to add to RPN table
        :param token_type: type of the token
        :return: index af added lexeme
        """
        # print(token_type.value, lexeme)
        if token_type in TOKEN_TYPES:
            if token_type not in [TOKEN_TYPES.END_STATEMENT, TOKEN_TYPES.CURVE_L, TOKEN_TYPES.CURVE_R]:
                priority = self.__priority_dict[token_type]
                if token_type is TOKEN_TYPES.BRACKET_L:
                    self.__operators_buffer.append((token_type, priority))
                else:
                    while len(self.__operators_buffer) > 0 and self.__operators_buffer[-1][1] < priority:
                        lexeme = self.__operators_buffer.pop(-1)[0]
                        self.__RPN_table.append((lexeme.value[1], lexeme.value[0]))
                        self.__last_index += 1

                    if  token_type is TOKEN_TYPES.BRACKET_R and \
                        self.__operators_buffer[-1][0] is TOKEN_TYPES.BRACKET_L:
                        self.__operators_buffer.pop(-1)
                    else:
                        self.__operators_buffer.append((token_type, priority))
            else:
                while len(self.__operators_buffer) > 0:
                    buf = self.__operators_buffer.pop(-1)[0]
                    self.__RPN_table.append((buf.value[1], buf.value[0]))
                    self.__last_index += 1

        else:
            self.__RPN_table.append((lexeme, token_type.value))
            self.__last_index += 1

        return self.__last_index - 1

    def print_to_console(self) -> None:
        temp_table = []
        for i, value in enumerate(self.__RPN_table):
            temp_table.append((i, value))
        lexer_print_table([["№", "postfixCode"]] + temp_table)

    def write_to_file(self, dir_path: str, file_name: str, var_table: Syntax_var_table, label_table: Label_table) -> None:
        to_write: dict[str, list] = {
            "var_table": var_table.get_table(),
            "label_table": label_table.get_table(),
            "code": self.__RPN_table
        }
        try:
            with open("Stack_machine" + "/" + file_name + FILE_TYPE_OUT, "w") as file:
                json.dump(to_write, file, indent=4)
        except:
            print_console("Error -> TP Syntax (Finishing): error occurred while writing code to file",
                          CONSOLE_COLORS.ERROR)
            exit(1)
        print_console("Success -> code successfully written to file ", CONSOLE_COLORS.OK)
