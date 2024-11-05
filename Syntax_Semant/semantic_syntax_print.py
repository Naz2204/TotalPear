from semantic_syntax_consts import CONSOLE_COLORS, KEYWORDS, TOKEN_TYPES, VALUE_TYPES

def print_console(message: str, message_type: CONSOLE_COLORS = CONSOLE_COLORS.NORMAL):
    print(message_type.value + message + CONSOLE_COLORS.NORMAL.value)


class Syntax_print:
    def __init__(self):
        self.__indentation = 0
        self.__INDENTATION = "│  "
        self.__prepared_print: list[str] = []

    @staticmethod
    def token_to_str(token: TOKEN_TYPES | KEYWORDS | VALUE_TYPES) -> str:
        print(type(token))
        if type(token) in [KEYWORDS, VALUE_TYPES]:
            print(type(token) is VALUE_TYPES, token.value)
            return str(token.value)
        else:
            # print(isinstance(token.value in KEYWORDS_VALUES))
            return token.value[0]

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
            to_print = ("Error -> TP (Syntax): Unexpected element on line " + str(error_line_num) + "\n" +
                        "Found element: " + str(found[0]) + " of type " + self.token_to_type_str(found[1]) + "\n" +
                        "Expected: ")

        for i in range(len(expected) - 1):
            to_print += f"'{self.token_to_str(expected[i])}', "
        to_print += f"'{self.token_to_str(expected[-1])}"

        print_console(to_print, CONSOLE_COLORS.ERROR)


    def print_lexeme_error(self, error_line_num: int):
        """
        :param error_line_num: Line where error occurred
        """
        print_console("Error -> TP (Syntax): Unexpected lexeme on line" + str(error_line_num), CONSOLE_COLORS.ERROR)

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
