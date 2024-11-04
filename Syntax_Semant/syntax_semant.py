from tkinter.ttk import setup_master

from Syntax_Semant.syntax_var_table import Syntax_var_table
from syntax_stream   import *
from syntax_print    import *
from syntax_consts   import *
from semantic_consts import *
import sys
import os

sys.path.append('../Lexer/')
from Lexer.lexer   import lexer_run as lexer


# TODO: check returns and ungets and exits add identation, update print_consol to some syntax_print

class Syntax:
    def __init__(self, stream: Syntax_input, output: Syntax_print, var_table: Syntax_var_table):
        self.__stream = stream
        self.__output = output
        self.__var_table = var_table

    def run(self):
        self.__statement_list()

    def __check_expected_token(self,
                               expected_tokens: list[KEYWORDS | TOKEN_TYPES | VALUE_TYPES] |
                                                     KEYWORDS | TOKEN_TYPES | VALUE_TYPES) -> str:
        token = self.__stream.get_token()
        expected_tokens = [expected_tokens] if type(expected_tokens) is not list else expected_tokens

        if token[1] in expected_tokens:
            return token[0]
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
        print_console("Success -> TP syntax (Result): Success syntax", CONSOLE_COLORS.OK)


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
        keyword_type = SEMANTIC_TYPE(token[1].value) # token either float, int or bool

        var_name = self.__check_expected_token(VALUE_TYPES.IDENTIFIER)

        # -- check declaration
        token = self.__stream.get_token()
        if token[1] == TOKEN_TYPES.END_STATEMENT:
            self.__output.accept_print_function()
            success_add = self.__var_table.add(var_name, keyword_type)
            if not success_add:
                self.__output.print_semantic_error(self.__stream.get_line(), "Redeclaration of variable: " + var_name)
                exit(1)
            return True # declaration

        self.__stream.unget(1)

        self.__check_expected_token(TOKEN_TYPES.OP_ASSIGN)

        semantic_type: SEMANTIC_TYPE
        input_ok = self.__input_statement()
        if input_ok[0]:
            semantic_type = input_ok[1]
        else:
            semantic_type = self.__expression()

        # semantic check
        math_cast_init = keyword_type in (SEMANTIC_TYPE.FLOAT, SEMANTIC_TYPE.INT) and semantic_type in (SEMANTIC_TYPE.FLOAT, SEMANTIC_TYPE.INT)
        bool_init = keyword_type is SEMANTIC_TYPE.BOOL and semantic_type is SEMANTIC_TYPE.BOOL
        okay_init = math_cast_init or bool_init
        if not okay_init:
            error_text = ("Initialization, type missmatch: variable type -> " + keyword_type.value +
                          ", expression type -> " + semantic_type.value)
            self.__output.print_semantic_error(self.__stream.get_line(), error_text)
            exit(1)

        # redeclaration check - and saving var
        success_add = self.__var_table.add(var_name, keyword_type)
        if not success_add:
            self.__output.print_semantic_error(self.__stream.get_line(), "Redeclaration of variable: " + var_name)
            exit(1)

        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
        self.__output.accept_print_function()
        return True

    #  --------------------- expression ---------------------
    def __expression(self) -> SEMANTIC_TYPE:
        # error check is inside
        # end of expression monad
        self.__output.prepare_print_function("expression")

        start_read = self.__stream.get_current_token_number()

        polynomial = self.__math_polynomial()
        if polynomial[0]:
            token = self.__stream.get_token()
            if token[1] not in [TOKEN_TYPES.OP_EQUAL, TOKEN_TYPES.OP_NOT_EQUAL, TOKEN_TYPES.OP_BIGGER_EQUAL,
                                TOKEN_TYPES.OP_LESS_EQUAL, TOKEN_TYPES.OP_LESS, TOKEN_TYPES.OP_BIGGER]:
                self.__stream.unget(1)
                self.__output.accept_print_function()
                if type(polynomial[1]) == str: # end of math-end branch of monads
                    self.__output.print_semantic_error(self.__stream.get_line(), polynomial[1])
                    exit(1)

                return polynomial[1]

        end_read = self.__stream.get_current_token_number()
        self.__stream.unget(end_read - start_read) # refresh before reading math_polynomial

        logical = self.__logical_expression()
        if not logical[0]:
            print_console(
                f"Error -> TP syntax (Runtime): no expression on line {self.__stream.get_line()}",
                CONSOLE_COLORS.ERROR)
            exit(1)
        self.__output.accept_print_function()
        if type(logical[1]) == str: # end of logical-end branch of monads
            self.__output.print_semantic_error(self.__stream.get_line(), logical[1])
            exit(1)
        return logical[1]

    def __logical_expression(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("logical_expression")
        logical = self.__logical2()
        if not logical[0]: # inner syntax error
            self.__output.discard_print_function()
            return False, ""

        type = logical[1]

        token = self.__stream.get_token()
        while token[1] == TOKEN_TYPES.OP_OR:
            logical = self.__logical2()
            if not logical[0]:
                print_console(f"Error -> TP syntax (Runtime): no logical expression after or operator on line {self.__stream.get_line()}",
                              CONSOLE_COLORS.ERROR)
                exit(1)
            type = expression_type(type, logical[1], token[1])
            token = self.__stream.get_token()
        self.__stream.unget(1)
        self.__output.accept_print_function()
        return True, type

    def __logical2(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("logical2")
        logical = self.__logical3()
        if not logical[0]: # syntax inner error
            self.__output.discard_print_function()
            return False, ""
        type = logical[1]

        token = self.__stream.get_token()
        while token[1] == TOKEN_TYPES.OP_AND:
            logical = self.__logical3()
            if not logical[0]: # syntax absence error
                print_console(f"Error -> TP syntax (Runtime): no logical expression after and operator on line {self.__stream.get_line()}",
                              CONSOLE_COLORS.ERROR)
                exit(1)
            type = expression_type(type, logical[1], token[1])
            token = self.__stream.get_token()

        self.__stream.unget(1)

        self.__output.accept_print_function()
        return True, type

    def __logical3(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("logical3")
        token = self.__stream.get_token()
        there_is_not: bool = False
        while token[1] == TOKEN_TYPES.OP_NOT:
            there_is_not = True
            token = self.__stream.get_token()
        self.__stream.unget(1)

        logical = self.__logical4()
        is_value_ok = logical[0]
        if not is_value_ok and not there_is_not: # syntax error inner
            self.__output.discard_print_function()
            return False, ""

        if not is_value_ok and there_is_not: #syntax error absence
            print_console(
                f"Error -> TP syntax (Runtime): no correct continuation after not operator on line {self.__stream.get_line()}",
                CONSOLE_COLORS.ERROR)
            exit(1)

        type = logical[1]
        if there_is_not:
            type = expression_type(token[1], type)
        self.__output.accept_print_function()
        return True, type

    def __logical4(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        raise "implement"

        self.__output.prepare_print_function("logical4")

        comparison = self.__comparison()
        if comparison[0]:
            self.__output.accept_print_function()
            return True, comparison[1]

        token = self.__stream.get_token()
        if token[1] == TOKEN_TYPES.BRACKET_L:
            logical = self.__logical_expression()
            if not logical[0]: # syntax inner error
                self.__stream.unget(1)
                self.__output.discard_print_function()
                return False, ""
            self.__check_expected_token(TOKEN_TYPES.BRACKET_R)
            self.__output.accept_print_function()
            return True, logical[1]


        # check var and value
        if token[1] is VALUE_TYPES.IDENTIFIER:
            var_type = self.__var_table.get(token[0])
            if var_type is None:
                var_type = "Using of undeclared variable: " + token[0]
            elif var_type is not SEMANTIC_TYPE.BOOL:
                var_type = "Type missmatch: variable " + token[0] + "type " + token[1].value + ", expected type bool"
            self.__output.accept_print_function()
            return True, var_type # monad control
        elif token[1] is VALUE_TYPE.BOOL:
            self.__output.accept_print_function()
            return True, SEMANTIC_TYPE.BOOL
        else: # bad var and value
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False, ""

    def __comparison(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("comparison")
        token = self.__stream.get_token()
        if token[1] != TOKEN_TYPES.COMPARISON_BRACKET: # syntax incorrect path
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False, ""

        math    = self.__math_comparison()
        logical = self.__logical_expression()
        if not math[0] and not logical[0]: # syntax absence error
            print_console(
                f"Error -> TP syntax (Runtime): nothing to compare inside compare brackets on line {self.__stream.get_line()}",
                CONSOLE_COLORS.ERROR)
            exit(1)

        type = logical[1] # assume logical[0]
        if math[0]: # then not logical[0]
            type = math[1]

        self.__check_expected_token(TOKEN_TYPES.COMPARISON_BRACKET)
        self.__output.accept_print_function()
        return True, type

    def __math_comparison(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("math_comparison")
        polynomial = self.__math_polynomial()
        if not polynomial[0]: # syntaxis inner error
            self.__output.discard_print_function()
            return False, ""

        type = polynomial[1]

        self.__check_expected_token([TOKEN_TYPES.OP_LESS_EQUAL, TOKEN_TYPES.OP_BIGGER_EQUAL ,TOKEN_TYPES.OP_BIGGER ,
                                     TOKEN_TYPES.OP_LESS ,TOKEN_TYPES.OP_EQUAL ,TOKEN_TYPES.OP_NOT_EQUAL])

        polynomial = self.__math_polynomial()
        if not polynomial[0]: # syntax absence error
            print_console(
                f"Error -> TP syntax (Runtime): no math expression after comparison sign on line {self.__stream.get_line()}",
                CONSOLE_COLORS.ERROR)
            exit(1)

        type = expression_type(type, polynomial[1], TOKEN_TYPES.OP_EQUAL) # all comparisons for math comparison are
                                                                          # similar for semantic

        self.__output.accept_print_function()
        return True, type

    def __logical_comparison(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("logical_comparison")

        logical = self.__logical_expression()
        if not logical[0]: # syntax inner error
            self.__output.discard_print_function()
            return False, ""
        type = logical[1]
        self.__check_expected_token([TOKEN_TYPES.OP_EQUAL, TOKEN_TYPES.OP_NOT_EQUAL])

        logical = self.__logical_expression()
        if not logical[0]: # syntax absence error
            print_console(
                f"Error -> TP syntax (Runtime): no logical expression after comparison sign on line {self.__stream.get_line()}",
                CONSOLE_COLORS.ERROR)
            exit(1)
        type = expression_type(type, logical[1], TOKEN_TYPES.OP_EQUAL) # both comparison operators are
                                                                       # similar for semantic

        self.__output.accept_print_function()
        return True, type


    def __math_polynomial(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("math_polynomial")
        monomial = self.__math_monomial()
        if not monomial[0]: # syntax error inner
            self.__output.discard_print_function()
            return False, ""

        type = monomial[1]

        token = self.__stream.get_token()
        while token[1] in [TOKEN_TYPES.OP_PLUS, TOKEN_TYPES.OP_MINUS]:
            monomial = self.__math_monomial()
            if not monomial[0]: # syntax error absence
                print_console(f"Error -> TP syntax (Runtime): no monomial after {token[1].value} on line {self.__stream.get_line()}",
                              CONSOLE_COLORS.ERROR)
                exit(1)

            type = expression_type(type, monomial[1], token[1])
            token = self.__stream.get_token()

        self.__stream.unget(1)
        self.__output.accept_print_function()
        return True, type

    def __math_monomial(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        # ceil error checker for other math that is lower in recursion
        self.__output.prepare_print_function("math_monomial")
        primary = self.__math_primary1()
        if not primary[0]: # syntax error inner
            self.__output.discard_print_function()
            return False, ""
        type = primary[1]

        token = self.__stream.get_token()
        while token[1] in [TOKEN_TYPES.OP_MULTI, TOKEN_TYPES.OP_DIVIDE]:
            primary = self.__math_primary1()
            if not primary[0]: # syntax error absent
                print_console(f"Error -> TP syntax (Runtime): no continuation after {token[1].value} on line {self.__stream.get_line()}",
                              CONSOLE_COLORS.ERROR)
                exit(1)
            type = expression_type(type, primary[1], token[1])
            token = self.__stream.get_token()
        self.__stream.unget(1)
        self.__output.accept_print_function()
        return True, type

    def __math_primary1(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("math_primary1")
        token = self.__stream.get_token()
        there_is_minus: bool = False
        while token[1] == TOKEN_TYPES.OP_MINUS:
            there_is_minus = True
            token = self.__stream.get_token()
        self.__stream.unget(1)

        primary = self.__math_primary2()
        is_value_ok = primary[0]

        if not is_value_ok and not there_is_minus: # error syntax inner
            self.__output.discard_print_function()
            return False, ""

        if not is_value_ok and there_is_minus: # error syntax absent
            print_console(
                f"Error -> TP syntax (Runtime): no continuation after unary minus on line {self.__stream.get_line()}",
                CONSOLE_COLORS.ERROR)
            exit(1)

        type = primary[1]
        if there_is_minus:
            type = expression_type(token[1], type)

        self.__output.accept_print_function()
        return True, type

    def __math_primary2(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("math_primary2")
        primary = self.__math_primary3()
        if not primary[0]: # syntax error inner
            self.__output.discard_print_function()
            return False, ""
        type = primary[1]

        token = self.__stream.get_token()
        if token[1] == TOKEN_TYPES.OP_POWER:
            primary = self.__math_primary1()
            type = expression_type(type, primary[1], token[1])
            if not primary[0]: # syntax error absent
                print_console(
                    f"Error -> TP syntax (Runtime): no correct continuation after power operator on line {self.__stream.get_line()}",
                    CONSOLE_COLORS.ERROR)
                exit(1)
        else: # not power
            self.__stream.unget(1)

        self.__output.accept_print_function()
        return True, type

    def __math_primary3(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("math_primary3")
        token = self.__stream.get_token()
        if token[1] == TOKEN_TYPES.BRACKET_L:
            polynomial = self.__math_polynomial()
            if not polynomial[0]: # syntax inner error
                self.__stream.unget(1)
                self.__output.discard_print_function()
                return False, ""
            self.__check_expected_token(TOKEN_TYPES.BRACKET_R)
            self.__output.accept_print_function()
            return True, polynomial[1] # type return

        if token[1] not in [VALUE_TYPES.INT, VALUE_TYPES.FLOAT, VALUE_TYPES.IDENTIFIER]:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False, ""

        self.__output.accept_print_function()

        raise "unimplemented type check"
        return True, "to implement"



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

        # check existence of var
        var_type = self.__var_table.get(token[0])
        if var_type is None:
            self.__output.print_semantic_error(self.__stream.get_line(), "Using of undeclared variable: " + token[0])

        # check expression
        expession_type: SEMANTIC_TYPE
        input_ok = self.__input_statement()
        if input_ok[0]:
            expession_type = input_ok[1]
        else:
            expession_type = self.__expression()

        # check semantic
        math_cast_assign = var_type in (SEMANTIC_TYPE.FLOAT, SEMANTIC_TYPE.INT) and expession_type in (SEMANTIC_TYPE.FLOAT, SEMANTIC_TYPE.INT)
        bool_assign = var_type is SEMANTIC_TYPE.BOOL and expession_type is SEMANTIC_TYPE.BOOL
        okay_assign = math_cast_assign or bool_assign
        if not okay_assign:
            error_text = ("Initialization, type missmatch: variable type -> " + var_type.value +
                          ", expression type -> " + expession_type.value)
            self.__output.print_semantic_error(self.__stream.get_line(), error_text)
            exit(1)

        # end
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

    def __input_statement(self) -> tuple[bool, SEMANTIC_TYPE]:
        self.__output.prepare_print_function("input_statement")
        token = self.__stream.get_token()
        if token[1] not in [KEYWORDS.INPUT_INT, KEYWORDS.INPUT_FLOAT, KEYWORDS.INPUT_BOOL]:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False, KEYWORDS.INPUT_BOOL # any input is sufficient due to syntax stopping return
        input_token = token[1]

        # syntax ()
        self.__check_expected_token(TOKEN_TYPES.BRACKET_L)
        token = self.__stream.get_token()
        if token[1] != VALUE_TYPES.STRING:
            self.__stream.unget(1)
        self.__check_expected_token(TOKEN_TYPES.BRACKET_R)

        # semantic get type
        input_type: SEMANTIC_TYPE
        match input_token:
            case KEYWORDS.INPUT_INT:
                input_type = SEMANTIC_TYPE.INT
            case KEYWORDS.INPUT_FLOAT:
                input_type = SEMANTIC_TYPE.FLOAT
            case KEYWORDS.INPUT_BOOL:
                input_type = SEMANTIC_TYPE.BOOL
            case _:
                print_console(f"Error -> TP syntax (Internal error): should be unreachable input type", CONSOLE_COLORS.ERROR)
                exit(1)

        self.__output.accept_print_function()
        return True, input_type

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
    syntax_var_table = Syntax_var_table()
    syntax = Syntax(syntax_stream, syntax_output, syntax_var_table)
    syntax.run()


if __name__ == '__main__':

    main_syntax()
