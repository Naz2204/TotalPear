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
        expected_tokens = [expected_tokens] if expected_tokens is not list else expected_tokens

        if token[1] in expected_tokens:
            return True
        self.__output.print_incorrect_found_error(token, expected_tokens, self.__stream.get_line())
        exit(1)



    #  --------------------- statements ---------------------
    def __statement_list(self) -> bool:
        self.__output.prepare_print_function("statement_list")
        at_least_one: bool = self.__statement_line()
        if not at_least_one:
            print_console("Error -> TP syntax (Runtime): empty program", CONSOLE_COLORS.ERROR)
            exit(1)

        while self.__statement_line(): pass


        self.__output.accept_print_function()
        return True

    def __statement_line(self) -> bool:
        self.__output.prepare_print_function("statement_line")

        if self.__stream.is_empty():
            # TODO: check for remove?

            self.__output.discard_print_function()
            return False

        if self.__statement_local() or self.__init_declare():

            self.__output.accept_print_function()
            return True

        # file not empty
        self.__output.print_incorrect_found_error(self.__stream.get_token(),  [
            KEYWORDS.FLOAT,       KEYWORDS.INT,        KEYWORDS.BOOL, KEYWORDS.PRINT, KEYWORDS.INPUT_INT,
            KEYWORDS.INPUT_FLOAT, KEYWORDS.INPUT_BOOL, KEYWORDS.IF,   KEYWORDS.WHILE, KEYWORDS.DO,
            KEYWORDS.FOR,         KEYWORDS.SWITCH,     KEYWORDS.FLAG_IF,
            VALUE_TYPES.IDENTIFIER
        ], self.__stream.get_line())
        exit(1)
        # self.__output.discard_print_function()()
        # return False

    def __statement_local(self) -> bool:
        self.__output.prepare_print_function("statement_local")

        is_ok =  (self.__assign()            or  self.__print()               or
                  self.__cycle_do()          or  self.__cycle_for()           or
                  self.__cycle_while()       or  self.__conditional_if()      or
                  self.__conditional_flags() or  self.__conditional_switch())
        if is_ok:
            self.__output.accept_print_function()
        else:
            self.__output.discard_print_function()

        return is_ok

    #  --------------------- variable ---------------------

    def __init_declare(self) -> bool:
        self.__output.prepare_print_function("init_declare")
        token = self.__stream.get_token()
        if token[1] not in (KEYWORDS.FLOAT, KEYWORDS.INT, KEYWORDS.BOOL):
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False


        self.__check_expected_token(VALUE_TYPES.IDENTIFIER)

        # -- check declaration
        token = self.__stream.get_token()
        if token[1] == TOKEN_TYPES.END_STATEMENT:
            self.__output.accept_print_function()
            return True  # declaration
        self.__stream.unget(1)

        self.__check_expected_token(TOKEN_TYPES.OP_ASSIGN)

        if self.__input_statement():
            self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
            self.__output.accept_print_function()
            return True

        self.__expression()

        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
        self.__output.accept_print_function()
        return True

    #  --------------------- expression ---------------------
    def __expression(self) -> bool:
        # error check is inside
        self.__output.prepare_print_function("expression")

        start_read = self.__stream.get_current_token_number()

        if self.__math_polynomial():
            token = self.__stream.get_token()
            if token[1] not in [TOKEN_TYPES.OP_EQUAL, TOKEN_TYPES.OP_NOT_EQUAL, TOKEN_TYPES.OP_BIGGER_EQUAL,
                                TOKEN_TYPES.OP_LESS_EQUAL, TOKEN_TYPES.OP_LESS, TOKEN_TYPES.OP_BIGGER]:
                self.__stream.unget(1)
                self.__output.accept_print_function()
                return True

        end_read = self.__stream.get_current_token_number()
        self.__stream.unget(end_read - start_read) # refresh before reading math_polynomial
        if not self.__logical_expression():
            print_console(
                f"Error -> TP syntax (Runtime): no expression on line {self.__stream.get_line()}",
                CONSOLE_COLORS.ERROR)
            exit(1)
        self.__output.accept_print_function()
        return True

    def __logical_expression(self) -> bool:
        self.__output.prepare_print_function("logical_expression")
        if not self.__logical2():
            self.__output.discard_print_function()
            return False


        token = self.__stream.get_token()
        while token[1] == TOKEN_TYPES.OP_OR:
            if not self.__logical2():
                print_console(f"Error -> TP syntax (Runtime): no logical expression after or operator on line {self.__stream.get_line()}",
                              CONSOLE_COLORS.ERROR)
                exit(1)
        self.__stream.unget(1)
        self.__output.accept_print_function()
        return True

    def __logical2(self) -> bool:
        self.__output.prepare_print_function("logical2")
        if not self.__logical3():
            self.__output.discard_print_function()
            return False

        token = self.__stream.get_token()
        while token[1] == TOKEN_TYPES.OP_AND:
            if not self.__logical3():
                print_console(f"Error -> TP syntax (Runtime): no logical expression after and operator on line {self.__stream.get_line()}",
                              CONSOLE_COLORS.ERROR)
                exit(1)
        self.__stream.unget(1)

        self.__output.accept_print_function()
        return True

    def __logical3(self) -> bool:
        self.__output.prepare_print_function("logical3")
        token = self.__stream.get_token()
        there_is_not: bool = False
        while token[1] == TOKEN_TYPES.OP_NOT:
            there_is_not = True
            token = self.__stream.get_token()
        self.__stream.unget(1)

        is_value_ok = self.__logical4()
        if not is_value_ok and not there_is_not:
            self.__output.discard_print_function()
            return False

        if not is_value_ok and there_is_not:
            print_console(
                f"Error -> TP syntax (Runtime): no correct continuation after not operator on line {self.__stream.get_line()}",
                CONSOLE_COLORS.ERROR)
            exit(1)

        self.__output.accept_print_function()
        return True

    def __logical4(self) -> bool:
        self.__output.prepare_print_function("logical4")
        # FIX: ADD Comparison
        # if self.__comparison(): # must be before bracket and logical value - because it can be start of it
        #     self.__output.accept_print_function(()
        #     return True

        token = self.__stream.get_token()
        if token[1] == TOKEN_TYPES.BRACKET_L:
            if not self.__logical_expression():
                self.__stream.unget(1)
                self.__output.discard_print_function()
                return False
            self.__check_expected_token(TOKEN_TYPES.BRACKET_R)
            self.__output.accept_print_function()
            return True

        if token[1] in [VALUE_TYPES.BOOL, VALUE_TYPES.IDENTIFIER]:
            self.__output.accept_print_function()
            return True
        else:
            self.__stream.unget(1)
        
        self.__output.discard_print_function()
        return False

    def __comparison(self) -> bool: pass
    # b = if == true
    #a and b == true

    def __math_polynomial(self) -> bool:
        self.__output.prepare_print_function("math_polynomial")
        if not self.__math_monomial():
            self.__output.discard_print_function()
            return False

        token = self.__stream.get_token()
        while token[1] in [TOKEN_TYPES.OP_PLUS, TOKEN_TYPES.OP_MINUS]:
            if not self.__math_monomial():
                print_console(f"Error -> TP syntax (Runtime): no monomial after {token[1].value} on line {self.__stream.get_line()}",
                              CONSOLE_COLORS.ERROR)
                exit(1)
            token = self.__stream.get_token()

        self.__stream.unget(1)
        self.__output.accept_print_function()
        return True

    def __math_monomial(self) -> bool:
        # ceil error checker for other math that is lower in recursion
        self.__output.prepare_print_function("math_monomial")
        if not self.__math_primary1():
            self.__output.discard_print_function()
            return False

        token = self.__stream.get_token()
        while token[1] in [TOKEN_TYPES.OP_MULTI, TOKEN_TYPES.OP_DIVIDE]:
            if not self.__math_primary1():
                print_console(f"Error -> TP syntax (Runtime): no continuation after {token[1].value} on line {self.__stream.get_line()}",
                              CONSOLE_COLORS.ERROR)
                exit(1)
            token = self.__stream.get_token()
        self.__stream.unget(1)
        self.__output.accept_print_function()
        return True

    def __math_primary1(self) -> bool:
        self.__output.prepare_print_function("math_primary1")
        token = self.__stream.get_token()
        there_is_minus: bool = False
        while token[1] == TOKEN_TYPES.OP_MINUS:
            there_is_minus = True
            token = self.__stream.get_token()
        self.__stream.unget(1)

        is_value_ok = self.__math_primary2()

        if not is_value_ok and not there_is_minus:
            self.__output.discard_print_function()
            return False

        if not is_value_ok and there_is_minus:
            print_console(
                f"Error -> TP syntax (Runtime): no continuation after unary minus on line {self.__stream.get_line()}",
                CONSOLE_COLORS.ERROR)
            exit(1)

        self.__output.accept_print_function()
        return True

    def __math_primary2(self) -> bool:
        self.__output.prepare_print_function("math_primary2")
        if not self.__math_primary3():
            self.__output.discard_print_function()
            return False

        token = self.__stream.get_token()
        if token[1] == TOKEN_TYPES.OP_POWER:

            if not self.__math_primary1():
                print_console(
                    f"Error -> TP syntax (Runtime): no correct continuation after power operator on line {self.__stream.get_line()}",
                    CONSOLE_COLORS.ERROR)
                exit(1)
        else: # not power
            self.__stream.unget(1)

        self.__output.accept_print_function()
        return True

    def __math_primary3(self) -> bool:
        self.__output.prepare_print_function("math_primary3")

        token = self.__stream.get_token()
        if token[1] == TOKEN_TYPES.BRACKET_L:
            if not self.__math_polynomial():
                self.__stream.unget(1)
                self.__output.discard_print_function()
                return False
            self.__check_expected_token(TOKEN_TYPES.BRACKET_R)
            self.__output.accept_print_function()
            return True

        if token[1] not in [VALUE_TYPES.INT, VALUE_TYPES.FLOAT, VALUE_TYPES.IDENTIFIER]:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        self.__output.accept_print_function()
        return True



    #  --------------------- --- ---------------------

    def __assign(self) -> bool:
        self.__output.prepare_print_function("assign")
        if not self.__assign_statement():
            self.__output.discard_print_function()
            return False
        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
        self.__output.accept_print_function()
        return True

    def __assign_statement(self) -> bool:
        self.__output.prepare_print_function("assign_statement")
        token = self.__stream.get_token()

        if token[1] != VALUE_TYPES.IDENTIFIER:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        self.__check_expected_token(TOKEN_TYPES.OP_ASSIGN)

        if self.__input_statement():
            self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
            self.__output.accept_print_function()
            return True
        else:
            self.__expression()
        self.__output.accept_print_function()
        return True

    def __print(self) -> bool:
        self.__output.prepare_print_function("print")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.PRINT:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False
        self.__check_expected_token(TOKEN_TYPES.BRACKET_L)
        if not self.__print_list():
            # if print list is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__check_expected_token(TOKEN_TYPES.BRACKET_R)
        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
        self.__output.accept_print_function()
        return True

    def __print_list(self) -> bool:
        self.__output.prepare_print_function("print_list")
        self.__printable() # error check is inside

        token = self.__stream.get_token()

        while token[1] == TOKEN_TYPES.PARAM_SEPARATOR:
            self.__printable()
            token = self.__stream.get_token()
        self.__stream.unget(1)
        self.__output.accept_print_function()
        return True

    def __printable(self) -> bool:
        self.__output.prepare_print_function("printable")
        # error check is inside
        token = self.__stream.get_token()
        if token[1] == VALUE_TYPES.STRING:
            self.__output.accept_print_function()
            return True

        self.__stream.unget(1)
        self.__expression()
        self.__output.accept_print_function()
        return True

    def __input_statement(self) -> bool:
        self.__output.prepare_print_function("input_statement")
        token = self.__stream.get_token()
        if token not in [KEYWORDS.INPUT_INT, KEYWORDS.INPUT_FLOAT, KEYWORDS.INPUT_BOOL]:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        self.__check_expected_token(TOKEN_TYPES.BRACKET_L)
        token = self.__stream.get_token()
        if token != VALUE_TYPES.STRING:
            self.__stream.unget(1)
        self.__check_expected_token(TOKEN_TYPES.BRACKET_R)

        self.__output.accept_print_function()
        return True

    def __body(self) -> bool:
        self.__output.prepare_print_function("body")
        # error check is inside
        self.__check_expected_token(TOKEN_TYPES.CURVE_L)
        while self.__statement_local(): pass
        self.__check_expected_token(TOKEN_TYPES.CURVE_R)
        self.__output.accept_print_function()
        return True

    def __cycle_do(self) -> bool:
        self.__output.prepare_print_function("cycle_do")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.DO:
              self.__stream.unget(1)
              self.__output.discard_print_function()
              return False
        self.__body()
        self.__check_expected_token(KEYWORDS.WHILE)

        if not self.__logical_expression():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
        self.__output.accept_print_function()
        return True

    def __cycle_while(self) -> bool:
        self.__output.prepare_print_function("cycle_while")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.WHILE:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        if not self.__logical_expression():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__body()
        self.__output.accept_print_function()
        return True

    def __cycle_for(self) -> bool:
        self.__output.prepare_print_function("cycle_for")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.FOR:
            self.__stream.unget(1)
            self.__output.discard_print_function()
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
        self.__output.accept_print_function()
        return True

    def __conditional_if(self) -> bool:
        self.__output.prepare_print_function("conditional_if")
        token = self.__stream.get_token()

        if token[1] != KEYWORDS.IF:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        if not self.__logical_expression():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__body()

        # false when no first keyword (elif/else) - error checker after this is strict
        while self.__elif(): pass
        self.__else()
        self.__output.accept_print_function()
        return True

    def __elif(self) -> bool:
        self.__output.prepare_print_function("conditional_elif")

        if self.__stream.is_empty():
            self.__output.discard_print_function()
            return False

        token = self.__stream.get_token()
        if token[1] != KEYWORDS.ELIF:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        if not self.__logical_expression():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__body()
        self.__output.accept_print_function()
        return True

    def __else(self) -> bool:
        self.__output.prepare_print_function("conditional_else")

        if self.__stream.is_empty():
            self.__output.discard_print_function()
            return False

        token = self.__stream.get_token()
        if token[1] != KEYWORDS.ELSE:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        self.__body()
        self.__output.accept_print_function()
        return True

    def __conditional_switch(self) -> bool:
        self.__output.prepare_print_function("conditional_switch")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.SWITCH:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        if not self.__math_polynomial():
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

        self.__output.accept_print_function()
        return True

    def __case(self) -> bool:
        self.__output.prepare_print_function("case")
        if self.__stream.is_empty():
            self.__output.discard_print_function()
            return False
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.CASE:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        token = self.__stream.get_token()
        if token[1] != TOKEN_TYPES.OP_MINUS:
            self.__stream.unget(1)

        self.__check_expected_token([VALUE_TYPES.INT, VALUE_TYPES.FLOAT])
        self.__check_expected_token(TOKEN_TYPES.COLON)

        self.__body()
        self.__output.accept_print_function()
        return True

    def __default(self) -> bool:
        self.__output.prepare_print_function("default")
        if self.__stream.is_empty():
            self.__output.discard_print_function()
            return False
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.DEFAULT:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        self.__check_expected_token(TOKEN_TYPES.COLON)

        self.__body()
        self.__output.accept_print_function()
        return True

    def __conditional_flags(self) -> bool:
        self.__output.prepare_print_function("conditional_flags")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.FLAG_IF:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        self.__flag_list()

        at_least_once: bool = self.__flag_body()
        if not at_least_once:
            print_console(f"Error -> TP syntax (Runtime): no flag body in flagIf, on line {self.__stream.get_line()}", CONSOLE_COLORS.ERROR)
            exit(1)

        while not self.__stream.is_empty() and self.__flag_body(): pass

        self.__output.accept_print_function()
        return True

    def __flag_list(self) -> bool:
        self.__output.prepare_print_function("flag_list")
        # error check is inside
        self.__check_expected_token(TOKEN_TYPES.SQUARE_L)
        at_least_once: bool = self.__flag_declare()
        if not at_least_once:
            print_console(f"Error -> TP syntax (Runtime): no flag declaration in flagIf, on line {self.__stream.get_line()}",
                          CONSOLE_COLORS.ERROR)
            exit(1)

        token = self.__stream.get_token()

        while token[1] == TOKEN_TYPES.PARAM_SEPARATOR:
            if not self.__flag_declare():
                print_console(
                    f"Error -> TP syntax (Runtime): no flag declaration after coma, on line {self.__stream.get_line()}",
                    CONSOLE_COLORS.ERROR)
                exit(1)

            token = self.__stream.get_token()


        self.__stream.unget(1)

        self.__check_expected_token(TOKEN_TYPES.SQUARE_R)
        self.__output.accept_print_function()
        return True

    def __flag_declare(self) -> bool:
        self.__output.prepare_print_function("flag_declare")
        if not self.__flag():
            self.__output.discard_print_function()
            return False
        self.__check_expected_token(TOKEN_TYPES.COLON)
        if not self.__logical_expression():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__output.accept_print_function()
        return True

    def __flag(self) -> bool:
        self.__output.prepare_print_function("flag")
        token = self.__stream.get_token()
        if token[1] != TOKEN_TYPES.FLAG:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        self.__check_expected_token(VALUE_TYPES.IDENTIFIER)
        self.__output.accept_print_function()
        return True

    def __flag_body(self) -> bool:
        self.__output.prepare_print_function("flag_body")
        if not self.__flag():
            self.__output.discard_print_function()
            return False
        self.__check_expected_token(TOKEN_TYPES.COLON)

        self.__body()

        self.__output.accept_print_function()
        return True


def process_start_args() -> str | None:
    """
    :return: file path
    """

    # get check amount of params
    startup_args: list[str] = sys.argv
    if len(startup_args) < 2:
        print_console("Error -> TP syntax (Startup): no file was provided", CONSOLE_COLORS.ERROR)
        return None
    if len(startup_args) > 2:
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

    main_syntax()
