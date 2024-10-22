from Lexer.lexer   import lexer_run as lexer
from syntax_stream import *
from syntax_print  import *
from syntax_consts import *
import sys
import os

# TODO: check returns and ungets and exits add identation, update print_consol to some syntax_print

class Syntax:
    def __init__(self, stream: Syntax_input, output: Syntax_print):
        self.__stream = stream
        self.__output = output

    def run(self):
        self.__statement_list()

    def __check_expected_token(self, expected_tokens: list[KEYWORDS | TOKEN_TYPES | VALUE_TYPES] | KEYWORDS | TOKEN_TYPES | VALUE_TYPES) -> bool:
        token = self.__stream.get_token()
        if token is None:
            self.__output.print_incorrect_found_error(None, expected_tokens, self.__stream.get_line())
            exit(1)

        if token[1] in expected_tokens:
            return True
        self.__output.print_incorrect_found_error(token, expected_tokens, self.__stream.get_line())
        exit(1)

    #  --------------------- statements ---------------------
    def __statement_list(self) -> bool:
        self.__output.print_parse_function("statement_list():")
        at_least_one: bool = self.__statement_line()
        if not at_least_one:
            print_console("Error -> TP syntax (Runtime): empty program", CONSOLE_COLORS.ERROR)
            exit(1)

        while self.__statement_line():
            pass

        return True

    def __statement_line(self) -> bool:
        self.__output.print_parse_function("statement_line():")

        if self.__statement_local() or self.__init_declare():
            return True

        if self.__stream.is_empty():
            return True

        # file not empty
        self.__output.print_incorrect_found_error(self.__stream.get_token(),  [
            KEYWORDS.FLOAT,       KEYWORDS.INT,        KEYWORDS.BOOL, KEYWORDS.PRINT, KEYWORDS.INPUT_INT,
            KEYWORDS.INPUT_FLOAT, KEYWORDS.INPUT_BOOL, KEYWORDS.IF,   KEYWORDS.WHILE, KEYWORDS.DO,
            KEYWORDS.FOR,         KEYWORDS.SWITCH,     KEYWORDS.FLAG_IF,
            VALUE_TYPES.IDENTIFIER
        ], self.__stream.get_line())
        exit(1)

    def __statement_local(self) -> bool:
        self.__output.print_parse_function("statement_local():")

        return (self.__assign()            or  self.__print()               or
                self.__cycle_do()          or  self.__cycle_for()           or
                self.__cycle_while()       or  self.__conditional_if()      or
                self.__conditional_flags() or  self.__conditional_switch())

    #  --------------------- variable ---------------------

    def __init_declare(self) -> bool:
        self.__output.print_parse_function("init_declare():")
        token = self.__stream.get_token()
        if token[1] not in (KEYWORDS.FLOAT, KEYWORDS.INT, KEYWORDS.BOOL):
            self.__stream.unget(1)
            return False

        self.__check_expected_token(VALUE_TYPES.IDENTIFIER)

        # -- check declaration
        token = self.__stream.get_token()
        if token[1] == TOKEN_TYPES.END_STATEMENT:
            return True  # declaration
        self.__stream.unget(1)

        self.__check_expected_token(TOKEN_TYPES.OP_ASSIGN)

        if self.__input_statement():
            self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
            return True

        if not self.__expression():
            # if expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())

        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
        return True

    def __expression(self) -> bool:
        self.__output.print_parse_function("expression():")

    def __logical_expression(self) -> bool:
        self.__output.print_parse_function("logical_expression():")

    def __math_expression(self) -> bool:
        self.__output.print_parse_function("math_expression():")

    def __assign(self) -> bool:
        if not self.__assign_statement():
            return False
        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
        return True

    def __assign_statement(self) -> bool:
        self.__output.print_parse_function("assign():")
        token = self.__stream.get_token()
        if token[1] != VALUE_TYPES.IDENTIFIER:
            self.__stream.unget(1)
            return False

        self.__check_expected_token(TOKEN_TYPES.OP_ASSIGN)

        if self.__input_statement():
            self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
            return True

        elif not self.__expression():
            # if expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)
        return True

    def __print(self) -> bool:
        self.__output.print_parse_function("print():")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.PRINT:
            self.__stream.unget(1)
            return False
        self.__check_expected_token(TOKEN_TYPES.BRACKET_L)
        if not self.__print_list():
            # if print list is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__check_expected_token(TOKEN_TYPES.BRACKET_R)
        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
        return True

    def __print_list(self) -> bool:
        self.__output.print_parse_function("print_list():")
        self.__printable() # error check is inside

        token = self.__stream.get_token()
        while token == TOKEN_TYPES.PARAM_SEPARATOR:
            self.__printable()
            token = self.__stream.get_token()
        self.__stream.unget(1)
        return True

    def __printable(self) -> bool:
        # error check is inside
        token = self.__stream.get_token()
        if token[1] == VALUE_TYPES.STRING:
            return True

        self.__stream.unget(1)
        if not self.__expression():
            # if expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)
        return True

    def __input_statement(self) -> bool:
        self.__output.print_parse_function("input_statement():")
        token = self.__stream.get_token()
        if token not in [KEYWORDS.INPUT_INT, KEYWORDS.INPUT_FLOAT, KEYWORDS.INPUT_BOOL]:
            self.__stream.unget(1)
            return False

        self.__check_expected_token(TOKEN_TYPES.BRACKET_L)
        token = self.__stream.get_token()
        if token != VALUE_TYPES.STRING:
            self.__stream.unget(1)
        self.__check_expected_token(TOKEN_TYPES.BRACKET_R)

        return True

    def __body(self) -> bool:
        # error check is inside
        self.__check_expected_token(TOKEN_TYPES.CURVE_L)
        while self.__statement_local(): pass
        self.__check_expected_token(TOKEN_TYPES.CURVE_R)
        return True

    def __cycle_do(self) -> bool:
        self.__output.print_parse_function("cycle_do():")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.DO:
              self.__stream.unget(1)
              return False
        self.__body()
        self.__check_expected_token(KEYWORDS.WHILE)

        if not self.__logical_expression():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
        return True

    def __cycle_while(self) -> bool:
        self.__output.print_parse_function("cycle_while():")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.WHILE:
            self.__stream.unget(1)
            return False

        if not self.__logical_expression():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__body()
        return True

    def __cycle_for(self) -> bool:
        self.__output.print_parse_function("cycle_for():")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.FOR:
            self.__stream.unget(1)
            return False

        self.__check_expected_token(TOKEN_TYPES.BRACKET_L)
        if not self.__assign_statement():
            # if assign_statement is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
        if not self.__logical_expression():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)

        if not self.__assign_statement():
            # if assign_statement is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__check_expected_token(TOKEN_TYPES.BRACKET_R)

        self.__body()
        return True

    def __conditional_if(self) -> bool:
        self.__output.print_parse_function("conditional_if():")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.IF:
            self.__stream.unget(1)
            return False

        if not self.__logical_expression():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__body()

        # false when no first keyword (elif/else) - error checker after this is strict
        while self.__elif(): pass
        self.__else()
        return True

    def __elif(self) -> bool:
        self.__output.print_parse_function("conditional_elif():")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.ELIF:
            self.__stream.unget(1)
            return False

        if not self.__logical_expression():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__body()
        return True

    def __else(self) -> bool:
        self.__output.print_parse_function("conditional_else():")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.ELSE:
            self.__stream.unget(1)
            return False

        self.__body()
        return True

    def __conditional_switch(self) -> bool:
        self.__output.print_parse_function("conditional_switch():")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.SWITCH:
            self.__stream.unget(1)
            return False

        if not self.__math_expression():
            # if math_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__check_expected_token(TOKEN_TYPES.CURVE_L)

        at_least_once: bool = self.__case()
        if not at_least_once:
            print_console(f"Error -> TP syntax (Runtime): no case in switch, on line {self.__stream.get_line()}", CONSOLE_COLORS.ERROR)
            exit(1)

        while self.__case(): pass

        self.__default()

        self.__check_expected_token(TOKEN_TYPES.CURVE_R)

        return True

    def __case(self) -> bool:
        self.__output.print_parse_function("case():")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.CASE:
            self.__stream.unget(1)
            return False

        token = self.__stream.get_token()
        if token[1] != TOKEN_TYPES.OP_MINUS:
            self.__stream.unget(1)

        self.__check_expected_token([VALUE_TYPES.INT, VALUE_TYPES.FLOAT])
        self.__check_expected_token(TOKEN_TYPES.COLON)

        self.__body()
        return True

    def __default(self) -> bool:
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.DEFAULT:
            self.__stream.unget(1)
            return False

        self.__check_expected_token(TOKEN_TYPES.COLON)

        self.__body()
        return True

    def __conditional_flags(self) -> bool:
        self.__output.print_parse_function("conditional_flags():")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.FLAG_IF:
            self.__stream.unget(1)
            return False


        return True

    def __flag_list(self) -> bool:
        self.__check_expected_token(TOKEN_TYPES.SQUARE_L)
        at_least_once: bool = self.__flag_declare()
        if not at_least_once:
            print_console(f"Error -> TP syntax (Runtime): no flag declaration in flagIf, on line {self.__stream.get_line()}",
                          CONSOLE_COLORS.ERROR)
            exit(1)

        token = self.__stream.get_token()
        while token == TOKEN_TYPES.PARAM_SEPARATOR:
            if not self.__flag_declare():
                print_console()

            token = self.__stream.get_token()
        self.__stream.unget(1)

        self.__check_expected_token(TOKEN_TYPES.SQUARE_R)

    def __flag_declare(self) -> bool:
        if not self.__flag():
            return False
        self.__check_expected_token(TOKEN_TYPES.COLON)
        if not self.__logical_expression():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        return True

    def __flag(self) -> bool:
        token = self.__stream.get_token()
        if token[1] != TOKEN_TYPES.FLAG:
            self.__stream.unget(1)
            return False

        self.__check_expected_token(VALUE_TYPES.IDENTIFIER)
        return True


    def __conditional_body(self) -> bool:
        pass


def process_start_args() -> str | None:
    """
    :return: file path
    """

    # get check amount of params
    startup_args: list[str] = sys.argv
    if len(startup_args) < 1:
        print_console("Error -> TP syntax (Startup): no file was provided", CONSOLE_COLORS.ERROR)
        return None
    if len(startup_args) > 1:
        print_console("Error -> TP syntax (Startup): too many parameters were provided", CONSOLE_COLORS.ERROR)
        return None

    # check if param is absolute or relative
    file_path_param = sys.argv[1]
    if not os.path.isabs(file_path_param):
        file_path_param = os.getcwd() + '\\' + file_path_param

    # check if path exists
    if not os.path.isfile(file_path_param):
        print_console(f"Error -> TP syntax (Startup): no file was found by address {file_path_param}",
                      CONSOLE_COLORS.ERROR)
        return None

    print_console(f"TP syntax (Startup): file was found - {file_path_param}", CONSOLE_COLORS.OK)

    # check file type
    if not file_path_param.endswith(FILE_TYPE_IN):
        print_console("Error -> TP syntax (Startup): incorrect file type", CONSOLE_COLORS.ERROR)
        return None

    return file_path_param


def main_syntax():
    file_path: str | None = process_start_args()
    if file_path is None:
        exit(1)

    # ----------------------------------------------
    lexer_result: tuple[dict, dict, list] = lexer(file_path)
    syntax_stream = Syntax_input(lexer_result)
    syntax_output = Syntax_print()
    syntax = Syntax(syntax_stream, syntax_output)
    syntax.run()


if __name__ == '__main__':
    try:
        main_syntax()
    except:
        pass