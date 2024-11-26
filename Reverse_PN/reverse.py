import os
import sys

from reverse_semantic_consts import *
from reverse_print import *
from reverse_stream import *
from reverse_syntax_consts import *
from reverse_table import Syntax_var_table


sys.path.append('../Lexer/')
from Lexer.lexer import lexer_run as lexer

# TODO: Переписати flagIf в документації
# TODO: check returns and ungets and exits add identation, update print_consol to some syntax_print

class Syntax:
    def __init__(self, stream: Syntax_input, output: Syntax_print, var_table: Syntax_var_table, label_table: Label_table, rpn_out: RPN_out):
        self.__stream      = stream
        self.__output      = output
        self.__var_table   = var_table
        self.__label_table = label_table
        self.__code_table  = rpn_out

    def run(self):
        self.__statement_list()

    def __check_expected_token(self,
                               expected_tokens: list[KEYWORDS | TOKEN_TYPES | VALUE_TYPES] |
                                                     KEYWORDS | TOKEN_TYPES | VALUE_TYPES) -> tuple[str, TOKEN_TYPES | KEYWORDS | VALUE_TYPES]:
        token = self.__stream.get_token()
        expected_tokens = [expected_tokens] if type(expected_tokens) is not list else expected_tokens

        if token[1] in expected_tokens:
            return token

        self.__output.print_incorrect_found_error(token, expected_tokens, self.__stream.get_line())
        exit(1)

    def __assign_label_position(self, label_id: int) -> None:
        label_position = self.__code_table.add(RPN_TYPES.LABEL, self.__label_table.get_label(label_id))
        self.__code_table.add(RPN_TYPES.OP_LABEL_DECLARE, RPN_TYPES.OP_LABEL_DECLARE.value)
        self.__label_table.change(label_id, label_position)

    def __jump_on_label(self, label_id: int, jump_type: TOKEN_TYPES = TOKEN_TYPES.OP_JMP) -> None:
        if jump_type not in (TOKEN_TYPES.OP_JMP, TOKEN_TYPES.OP_JT, TOKEN_TYPES.OP_JF):
            print_console("Error -> TP postfix (Internal): wrong type passed as parameter", CONSOLE_COLORS.ERROR)
        else:
            self.__code_table.add(RPN_TYPES.LABEL, self.__label_table.get_label(label_id))
            self.__code_table.add(jump_type)
            self.__code_table.add(TOKEN_TYPES.END_STATEMENT)

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

        keyword_type = KEYWORDS_TO_SEMANTIC_TYPE[token[1]] # token either float, int or bool
        var_name = self.__check_expected_token(VALUE_TYPES.IDENTIFIER)[0]

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

        self.__code_table.add(RPN_TYPES.L_VAL, var_name)

        self.__check_expected_token(TOKEN_TYPES.OP_ASSIGN)
        self.__code_table.add(TOKEN_TYPES.OP_ASSIGN)

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
        self.__code_table.add(TOKEN_TYPES.END_STATEMENT)
        self.__output.accept_print_function()
        return True

    #  --------------------- expression ---------------------
    def __expression_next_is_math(self) -> bool:
        start_read = self.__stream.get_current_token_number()

        while self.__stream.get_token()[1] is TOKEN_TYPES.BRACKET_L:
            pass
        self.__stream.unget(1)
        token = self.__stream.get_token()

        is_math: bool = token[1] in [
            VALUE_TYPES.INT,      VALUE_TYPES.FLOAT,
            TOKEN_TYPES.OP_PLUS,  TOKEN_TYPES.OP_MINUS, TOKEN_TYPES.OP_DIVIDE,
            TOKEN_TYPES.OP_MULTI, TOKEN_TYPES.OP_POWER
        ]
        is_math = is_math or self.__var_table.get(token[0]) in [SEMANTIC_TYPE.INT, SEMANTIC_TYPE.FLOAT]

        end_read = self.__stream.get_current_token_number()
        self.__stream.unget(end_read - start_read) # refresh before reading

        return is_math

    def __expression(self) -> SEMANTIC_TYPE:
        # error check is inside
        # end of expression monad
        self.__output.prepare_print_function("expression")

        # choose math or logical expression
        is_math = self.__expression_next_is_math()
        if is_math:
            expression = self.__math_polynomial()
        else:
            expression = self.__logical_expression()

        # check errors
        if not expression[0]: # bool - false (no value in expression)
            # TODO: can be optimized in __expression_next_in_math by checking if the value can be logical or math
            print_console(
                f"Error -> TP syntax (Runtime): no valid expression on line {self.__stream.get_line()}",
                CONSOLE_COLORS.ERROR)
            exit(1)
        elif type(expression[1]) is str: # 0.1
            self.__output.print_semantic_error(self.__stream.get_line(), expression[1])
            exit(1)

        # is correct
        self.__output.accept_print_function()
        return expression[1]

    def __logical_expression_wrapped(self) -> bool:
        logical = self.__logical_expression()
        if logical[0] and (type(logical[1]) is str):
            self.__output.print_semantic_error(self.__stream.get_line(), logical[1])
            exit(1)

        return logical[0]

    def __logical_expression(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("logical_expression")
        logical = self.__logical2()
        if not logical[0]: # inner syntax error
            self.__output.discard_print_function()
            return False, ""

        type = logical[1]

        token = self.__stream.get_token()
        while token[1] == TOKEN_TYPES.OP_OR:
            self.__code_table.add(token[1])
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
            self.__code_table.add(token[1])
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
            self.__code_table.add(token[1])
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
            type = expression_type_unary(TOKEN_TYPES.OP_NOT, type)
        self.__output.accept_print_function()
        return True, type

    def __logical4(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("logical4")

        comparison = self.__comparison()
        if comparison[0]:
            self.__output.accept_print_function()
            return True, comparison[1]

        token = self.__stream.get_token()
        if token[1] == TOKEN_TYPES.BRACKET_L:
            self.__code_table.add(TOKEN_TYPES.BRACKET_L)
            logical = self.__logical_expression()
            if not logical[0]: # syntax inner error
                self.__stream.unget(1)
                self.__output.discard_print_function()
                return False, ""
            self.__check_expected_token(TOKEN_TYPES.BRACKET_R)
            self.__code_table.add(TOKEN_TYPES.BRACKET_R)
            self.__output.accept_print_function()
            return True, logical[1]


        # check var and value
        if token[1] is VALUE_TYPES.IDENTIFIER:
            self.__code_table.add(token[1], RPN_TYPES.R_VAL.value)
            var_type = self.__var_table.get(token[0])
            if var_type is None:
                var_type = "Using of undeclared variable: " + token[0]
            elif var_type is not SEMANTIC_TYPE.BOOL:
                var_type = "Type missmatch: variable \'" + token[0] + "\' type " + var_type.value + ", expected type bool"
            self.__output.accept_print_function()
            return True, var_type # monad control
        elif token[1] is VALUE_TYPES.BOOL:
            self.__code_table.add(token[1], token[0])
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

        # --------------------------------------------------------
        self.__code_table.add(TOKEN_TYPES.BRACKET_L) # left | is the same as (

        left = self.__expression()

        allow_operator = [TOKEN_TYPES.OP_LESS_EQUAL, TOKEN_TYPES.OP_BIGGER_EQUAL, TOKEN_TYPES.OP_BIGGER,
                          TOKEN_TYPES.OP_LESS,       TOKEN_TYPES.OP_EQUAL,        TOKEN_TYPES.OP_NOT_EQUAL]
        if left is SEMANTIC_TYPE.BOOL:
            allow_operator = [TOKEN_TYPES.OP_EQUAL, TOKEN_TYPES.OP_NOT_EQUAL]

        token = self.__check_expected_token(allow_operator)
        self.__code_table.add(token[1])

        right = self.__expression()

        if (left is     SEMANTIC_TYPE.BOOL and right is not SEMANTIC_TYPE.BOOL):
            print_console(f"Error -> TP syntax (Runtime): no logical expression after comparison sign on line {self.__stream.get_line()}",
                          CONSOLE_COLORS.ERROR)
            exit(1)
        elif (left is not SEMANTIC_TYPE.BOOL and right is     SEMANTIC_TYPE.BOOL):
            print_console(f"Error -> TP syntax (Runtime): no math expression after comparison sign on line {self.__stream.get_line()}",
                          CONSOLE_COLORS.ERROR)
            exit(1)

        # --------------------------------------------------------

        self.__check_expected_token(TOKEN_TYPES.COMPARISON_BRACKET)
        self.__code_table.add(TOKEN_TYPES.BRACKET_R) # right | is the same as )
        self.__output.accept_print_function()
        return True, SEMANTIC_TYPE.BOOL

    def __math_polynomial_wrapped(self) -> bool:
        math = self.__math_polynomial()
        if math[0] and (type(math[1]) is str):
            self.__output.print_semantic_error(self.__stream.get_line(), math[1])
            exit(1)

        return math[0]

    def __math_polynomial(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("math_polynomial")
        monomial = self.__math_monomial()
        if not monomial[0]: # syntax error inner
            self.__output.discard_print_function()
            return False, ""

        type = monomial[1]

        token = self.__stream.get_token()
        while token[1] in [TOKEN_TYPES.OP_PLUS, TOKEN_TYPES.OP_MINUS]:
            self.__code_table.add(token[1])
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

    def __check_throw_zero_division(self, operator: TOKEN_TYPES) -> None:
        '''
        no throw - auto exit on error
        uses indirect way of acquiring token
        '''
        if operator != TOKEN_TYPES.OP_DIVIDE: return
        self.__stream.unget(1) # operator number
        value, _ = self.__stream.get_token()
        value = value.split(".")

        value_is_bad_int = all(x == '0' for x in value[0]) # yet undone
        # len(value) == 2 - should be first in checks (at least before value[1])
        value_is_bad_float = len(value) == 2 and value_is_bad_int and all(x == '0' for x in value[1])
        value_is_bad_int = value_is_bad_int and len(value) == 1 
            
        value_is_bad = value_is_bad_float or value_is_bad_int
        if value_is_bad:
            self.__output.print_semantic_error(self.__stream.get_line(), "Zero division")
            exit(1)



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
            self.__code_table.add(token[1])
            primary = self.__math_primary1()
            if not primary[0]: # syntax error absent
                print_console(f"Error -> TP syntax (Runtime): no continuation after {token[1].value} on line {self.__stream.get_line()}",
                              CONSOLE_COLORS.ERROR)
                exit(1)
            type = expression_type(type, primary[1], token[1])
            self.__check_throw_zero_division(token[1])
            token = self.__stream.get_token()

        self.__stream.unget(1)
        self.__output.accept_print_function()
        return True, type

    def __math_primary1(self) -> tuple[bool, str | SEMANTIC_TYPE]:
        self.__output.prepare_print_function("math_primary1")
        token = self.__stream.get_token()
        there_is_minus: bool = False
        while token[1] == TOKEN_TYPES.OP_MINUS:
            self.__code_table.add(TOKEN_TYPES.OP_UMINUS)
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
            type = expression_type_unary(TOKEN_TYPES.OP_MINUS, type)

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
            self.__code_table.add(token[1])
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
            self.__code_table.add(TOKEN_TYPES.BRACKET_L)
            polynomial = self.__math_polynomial()
            if not polynomial[0]: # syntax inner error
                self.__stream.unget(1)
                self.__output.discard_print_function()
                return False, ""
            self.__check_expected_token(TOKEN_TYPES.BRACKET_R)
            self.__code_table.add(TOKEN_TYPES.BRACKET_R)
            self.__output.accept_print_function()
            return True, polynomial[1] # type return

        if token[1] is VALUE_TYPES.IDENTIFIER:
            self.__code_table.add(RPN_TYPES.R_VAL, token[0])
            var_type = self.__var_table.get(token[0])
            if var_type is None:
                var_type = "Using of undeclared variable: " + token[0]
            elif var_type not in [SEMANTIC_TYPE.INT, SEMANTIC_TYPE.FLOAT]:
                var_type = "Type missmatch: variable \'" + token[0] + "\' type " + var_type.value + ", expected type int/float"
            self.__output.accept_print_function()
            return True, var_type
        elif token[1] in [VALUE_TYPES.INT, VALUE_TYPES.FLOAT]:
            self.__code_table.add(token[1], token[0])
            self.__output.accept_print_function()
            return True, SEMANTIC_TYPE(token[1].value)
        else:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False, ""


    #  --------------------- --- ---------------------

    def __assign(self) -> bool:
        self.__output.prepare_print_function("assign")
        if not self.__assign_statement():
            self.__output.discard_print_function()
            return False
        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
        self.__code_table.add(TOKEN_TYPES.END_STATEMENT)
        self.__output.accept_print_function()
        return True

    def __assign_statement(self) -> bool:
        self.__output.prepare_print_function("assign_statement")
        token = self.__stream.get_token()

        if token[1] != VALUE_TYPES.IDENTIFIER:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        self.__code_table.add(RPN_TYPES.L_VAL, token[0])
        self.__check_expected_token(TOKEN_TYPES.OP_ASSIGN)
        self.__code_table.add(TOKEN_TYPES.OP_ASSIGN)

        # check existence of var
        var_type = self.__var_table.get(token[0])
        if var_type is None:
            self.__output.print_semantic_error(self.__stream.get_line(), "Using of undeclared variable: " + token[0])
            exit(1)

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
        self.__code_table.add(TOKEN_TYPES.END_STATEMENT)
        self.__output.accept_print_function()
        return True

    def __print_list(self) -> bool:
        self.__output.prepare_print_function("print_list")
        self.__printable() # error check is inside and code generation

        token = self.__stream.get_token()

        while token[1] == TOKEN_TYPES.PARAM_SEPARATOR:
            self.__code_table.add(TOKEN_TYPES.END_STATEMENT) # analagous for comma
            self.__printable()
            token = self.__stream.get_token()

        # self.__code_table.add(TOKEN_TYPES.END_STATEMENT) # - REDUNDANT

        self.__stream.unget(1)
        self.__output.accept_print_function()
        return True

    def __printable(self) -> bool:
        self.__output.prepare_print_function("printable")
        # error check is inside
        token = self.__stream.get_token()
        if token[1] == VALUE_TYPES.STRING:
            self.__code_table.add(token[1], token[0])
            self.__code_table.add(TOKEN_TYPES.OP_OUT_STR)
            self.__output.accept_print_function()
            return True

        self.__stream.unget(1)
        semantic_type = self.__expression()
        match semantic_type:
            case SEMANTIC_TYPE.INT:
                self.__code_table.add(TOKEN_TYPES.OP_OUT_INT)
            case SEMANTIC_TYPE.FLOAT:
                self.__code_table.add(TOKEN_TYPES.OP_OUT_FLOAT)
            case SEMANTIC_TYPE.BOOL:
                self.__code_table.add(TOKEN_TYPES.OP_OUT_BOOL)
            case _:
                print_console(
                "Error -> TP syntax (Internal): error on print resolution",
                CONSOLE_COLORS.ERROR)
                exit(1)

        self.__output.accept_print_function()
        return True

    def __input_statement(self) -> tuple[bool, SEMANTIC_TYPE]:
        self.__output.prepare_print_function("input_statement")
        token = self.__stream.get_token()
        if token[1] not in [KEYWORDS.INPUT_INT, KEYWORDS.INPUT_FLOAT, KEYWORDS.INPUT_BOOL]:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False, SEMANTIC_TYPE.BOOL # any input is sufficient due to syntax stopping return
        input_token = token[1]

        # syntax ()
        self.__check_expected_token(TOKEN_TYPES.BRACKET_L)
        token = self.__stream.get_token()
        if token[1] != VALUE_TYPES.STRING:
            self.__stream.unget(1)
        self.__check_expected_token(TOKEN_TYPES.BRACKET_R)
        self.__code_table.add(token[1], token[0])
        self.__code_table.add(TOKEN_TYPES.OP_OUT_STR)


        # semantic get type
        input_type: SEMANTIC_TYPE
        match input_token:
            case KEYWORDS.INPUT_INT:
                input_type = SEMANTIC_TYPE.INT
                self.__code_table.add(TOKEN_TYPES.OP_INPUT_INT)
            case KEYWORDS.INPUT_FLOAT:
                input_type = SEMANTIC_TYPE.FLOAT
                self.__code_table.add(TOKEN_TYPES.OP_INPUT_FLOAT)
            case KEYWORDS.INPUT_BOOL:
                input_type = SEMANTIC_TYPE.BOOL
                self.__code_table.add(TOKEN_TYPES.OP_INPUT_BOOL)
            case _:
                print_console(f"Error -> TP syntax (Internal error): should be unreachable input type", CONSOLE_COLORS.ERROR)
                exit(1)

        self.__output.accept_print_function()
        return True, input_type

    def __body(self) -> bool:
        self.__output.prepare_print_function("body")
        # error check is inside
        self.__check_expected_token(TOKEN_TYPES.CURVE_L)
        self.__code_table.add(TOKEN_TYPES.CURVE_L)
        while self.__statement_local(): pass
        self.__check_expected_token(TOKEN_TYPES.CURVE_R)
        self.__code_table.add(TOKEN_TYPES.CURVE_R)
        self.__output.accept_print_function()
        return True

    def __cycle_do(self) -> bool:
        self.__output.prepare_print_function("cycle_do")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.DO:
              self.__stream.unget(1)
              self.__output.discard_print_function()
              return False

        # label to jmp on true
        start_do = self.__label_table.make_label()
        self.__assign_label_position(start_do)

        self.__body()
        self.__check_expected_token(KEYWORDS.WHILE)

        # BOOL
        if not self.__logical_expression_wrapped():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        # jmp - true - redo
        self.__jump_on_label(start_do, TOKEN_TYPES.OP_JT)

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

        # label to jmp on true
        start_while = self.__label_table.make_label()
        self.__assign_label_position(start_while)

        # BOOL
        if not self.__logical_expression_wrapped():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        # jmp - false - end
        end_label = self.__label_table.make_label()
        self.__jump_on_label(end_label, TOKEN_TYPES.OP_JF)

        self.__body()

        # jmp - redo
        self.__jump_on_label(start_while)

        # label to jmp on false
        self.__assign_label_position(end_label)

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
        # ---------

        if not self.__assign_statement():
            # if assign_statement is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)
        self.__code_table.add(TOKEN_TYPES.END_STATEMENT)

        # label: check
        check_label = self.__label_table.make_label()
        self.__assign_label_position(check_label)

        # check
        if not self.__logical_expression_wrapped():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__check_expected_token(TOKEN_TYPES.END_STATEMENT)

        # label: check - false (jmp to the end)
        end_label = self.__label_table.make_label()
        self.__jump_on_label(end_label, TOKEN_TYPES.OP_JF)

        # label: check - true (jmp to body)
        body_label = self.__label_table.make_label()
        self.__jump_on_label(body_label)

        # label: step
        step_label = self.__label_table.make_label()
        self.__assign_label_position(step_label)

        # step
        if not self.__assign_statement():
            # if assign_statement is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        self.__code_table.add(TOKEN_TYPES.END_STATEMENT)

        # label: jmp on check
        self.__jump_on_label(check_label)

        # ---------
        self.__check_expected_token(TOKEN_TYPES.BRACKET_R)

        # label: body
        self.__assign_label_position(body_label)

        self.__body()

        # label: jmp to step
        self.__jump_on_label(step_label)

        # label: end label
        self.__assign_label_position(end_label)

        self.__output.accept_print_function()
        return True

    def __conditional_if(self) -> bool:
        self.__output.prepare_print_function("conditional_if")
        token = self.__stream.get_token()

        if token[1] != KEYWORDS.IF:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        if not self.__logical_expression_wrapped():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        # if - false - next jmp: make
        next_label = self.__label_table.make_label()
        self.__jump_on_label(next_label, TOKEN_TYPES.OP_JF)

        self.__body()

        # if - true - end jmp
        end_label = self.__label_table.make_label()
        self.__jump_on_label(end_label)

        # if - false - next jmp: jmp
        self.__assign_label_position(next_label)

        # false when no first keyword (elif/else) - error checker after this is strict
        while self.__elif(end_label): pass
        self.__else()

        # end label for jmp
        self.__assign_label_position(end_label)

        self.__output.accept_print_function()
        return True

    def __elif(self, end_label) -> bool:
        self.__output.prepare_print_function("conditional_elif")

        if self.__stream.is_empty():
            self.__output.discard_print_function()
            return False

        token = self.__stream.get_token()
        if token[1] != KEYWORDS.ELIF:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        if not self.__logical_expression_wrapped():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        # elif - false
        next_label = self.__label_table.make_label()
        self.__jump_on_label(next_label, TOKEN_TYPES.OP_JF)

        self.__body()

        # elif - true
        self.__jump_on_label(end_label)

        # elif - false
        self.__assign_label_position(next_label)

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


    def __conditional_switch_compare_table(self, cmp_table_lable: int, match_var: str, cases_list: list[str],
                                           type_list: list[VALUE_TYPES], local_label_list: list[int], default_label: int | None) -> None:
        # Label: cmp_table - assign
        self.__assign_label_position(cmp_table_lable)

        for i in range(len(cases_list)):
            self.__code_table.add(RPN_TYPES.R_VAL, match_var)
            self.__code_table.add(TOKEN_TYPES.OP_EQUAL)
            self.__code_table.add(type_list[i], cases_list[i])
            self.__code_table.add(TOKEN_TYPES.END_STATEMENT)

            self.__jump_on_label(local_label_list[i], TOKEN_TYPES.OP_JT)

        if default_label is not None:
            self.__jump_on_label(default_label)


    def __conditional_switch(self) -> bool:
        self.__output.prepare_print_function("conditional_switch")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.SWITCH:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        # if not self.__math_polynomial_wrapped():
        #     # if math_expression is false - then first value was incorrect
        #     self.__output.print_lexeme_error(self.__stream.get_line())
        #     exit(1)
        # TODO Змінити в синтаксисі мови з виразу на ідентифікатор якщо все проканає

        match_var, _ = self.__check_expected_token(VALUE_TYPES.IDENTIFIER)
        if self.__var_table.get(match_var) not in [SEMANTIC_TYPE.INT, SEMANTIC_TYPE.FLOAT]:
            self.__output.print_semantic_error(self.__stream.get_line(), "switch statement expect variable of one of types: int, float")
            exit(1)

        # label: end, compare table
        end_label = self.__label_table.make_label()
        cmp_table_lable = self.__label_table.make_label()
        self.__jump_on_label(cmp_table_lable)

        self.__check_expected_token(TOKEN_TYPES.CURVE_L)
        cases_list: list[str] = []
        type_list: list[VALUE_TYPES] = []
        local_label_list: list[int] = []
        at_least_once: bool = self.__case(cases_list, type_list, local_label_list, end_label)
        if not at_least_once:
            print_console(f"Error -> TP syntax (Runtime): no case in switch, on line {self.__stream.get_line()}", CONSOLE_COLORS.ERROR)
            exit(1)

        while self.__case(cases_list, type_list, local_label_list, end_label): pass

        default_label: int | None = self.__default(end_label)[1] # false == None

        self.__check_expected_token(TOKEN_TYPES.CURVE_R)

        # Compare table
        self.__conditional_switch_compare_table(cmp_table_lable, match_var, cases_list, type_list, local_label_list, default_label)

        # Label: end - assign
        self.__assign_label_position(end_label)

        self.__output.accept_print_function()
        return True


    def __case(self, cases_list: list[str], type_list:list[VALUE_TYPES], local_label_l:list[int], end_label: int) -> bool:
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
        has_uminus = token[1] == TOKEN_TYPES.OP_MINUS

        if not has_uminus:
            self.__stream.unget(1)

        key, value_type = self.__check_expected_token([VALUE_TYPES.INT, VALUE_TYPES.FLOAT])
        if has_uminus:
            key = '-' + key

        self.__check_expected_token(TOKEN_TYPES.COLON)

        # Label: case label
        case_label = self.__label_table.make_label()
        self.__assign_label_position(case_label)

        self.__body()

        # Label: break case
        self.__jump_on_label(end_label)

        self.__output.accept_print_function()

        # check uniquness of case
        if key in cases_list:
            print_console(f"WARNING: Duplicated case {key}, on line {self.__stream.get_line()}",
                          CONSOLE_COLORS.WARNING)
        else:
            cases_list.append(key)
            type_list.append(value_type)
            local_label_l.append(case_label)

        return True


    def __default(self, end_label: int) -> tuple[bool, int|None]:
        self.__output.prepare_print_function("default")
        if self.__stream.is_empty():
            self.__output.discard_print_function()
            return False, None
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.DEFAULT:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False, None

        self.__check_expected_token(TOKEN_TYPES.COLON)

        # Label: default label
        default_label = self.__label_table.make_label()
        self.__assign_label_position(default_label)

        self.__body()

        # Label: case break
        self.__jump_on_label(end_label)

        self.__output.accept_print_function()
        return True, default_label


    def __conditional_flags(self) -> bool:
        self.__output.prepare_print_function("conditional_flags")
        token = self.__stream.get_token()
        if token[1] != KEYWORDS.FLAG_IF:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False

        # Label: end of flagIf
        end_label = self.__label_table.make_label()

        flags_list: list[str] = []
        dict_flag_labels: dict[str, tuple[int, int]] = self.__flag_list(flags_list)[1]

        # Label: jump to end, on end of flag chooser
        self.__jump_on_label(end_label)

        at_least_once: bool = self.__flag_body(flags_list, dict_flag_labels)
        if not at_least_once:
            print_console(f"Error -> TP syntax (Runtime): no flag body in flagIf, on line {self.__stream.get_line()}", CONSOLE_COLORS.ERROR)
            exit(1)

        while self.__flag_body(flags_list, dict_flag_labels): pass

        # check all flags was implemented
        if len(flags_list) != 0:
            flags_list = list("#" + x for x in flags_list)
            flags_list = str(flags_list)[1:-1]
            self.__output.print_semantic_error(self.__stream.get_line(), f"Unimplemented flags in flagIf statement: {flags_list} - ")
            exit(1)

        # Label: end of flagIf
        self.__assign_label_position(end_label)

        self.__output.accept_print_function()
        return True


    def __flag_list(self, list_to_fill: list[str]) -> tuple[bool, dict[str, tuple[int, int]]]:
        """
        :return (is_ok, {"user flag": (label, return to flag list check label)}
        """
        self.__output.prepare_print_function("flag_list")
        # error check is inside
        self.__check_expected_token(TOKEN_TYPES.SQUARE_L)

        result_dict: dict[str, tuple[int, int]] = {}

        at_least_once, flag_check_block  = self.__flag_declare(list_to_fill)
        if not at_least_once:
            print_console(f"Error -> TP syntax (Runtime): no flag declaration in flagIf, on line {self.__stream.get_line()}",
                          CONSOLE_COLORS.ERROR)
            exit(1)

        result_dict[flag_check_block[0]] = flag_check_block[1]

        token = self.__stream.get_token()


        while token[1] == TOKEN_TYPES.PARAM_SEPARATOR:
            is_ok, flag_check_block = self.__flag_declare(list_to_fill)
            if not is_ok:
                print_console(
                    f"Error -> TP syntax (Runtime): no flag declaration after coma, on line {self.__stream.get_line()}",
                    CONSOLE_COLORS.ERROR)
                exit(1)

            result_dict[flag_check_block[0]] = flag_check_block[1]
            token = self.__stream.get_token()


        self.__stream.unget(1)

        self.__check_expected_token(TOKEN_TYPES.SQUARE_R)
        self.__output.accept_print_function()
        return True, result_dict



    def __flag_declare(self, list_to_append: list[str]) -> tuple[bool, tuple[str, tuple[int, int]]] :
        """
        :return (is_ok, ("user flag name": (label for flag, label to get back to label list check)))
        """
        self.__output.prepare_print_function("flag_declare")
        flag = self.__flag()
        if not flag[0]:
            self.__output.discard_print_function()
            return False, ()
        self.__check_expected_token(TOKEN_TYPES.COLON)
        if not self.__logical_expression_wrapped():
            # if logical_expression is false - then first value was incorrect
            self.__output.print_lexeme_error(self.__stream.get_line())
            exit(1)

        # check semantic of existence of flag
        if flag[1] in list_to_append:
            self.__output.print_semantic_error(self.__stream.get_line(), f"Duplication of flag {flag[1]} in flag declaration list")
            exit(1)
        else:
            list_to_append.append(flag[1])

        # Code generating
        self.__code_table.add(TOKEN_TYPES.END_STATEMENT) # flush operands for logical evaluation
        this_flag_body = self.__label_table.make_label()
        self.__jump_on_label(this_flag_body, TOKEN_TYPES.OP_JT)
        this_flag_end = self.__label_table.make_label()
        self.__assign_label_position(this_flag_end)

        self.__output.accept_print_function()
        return True, (flag[1], (this_flag_body, this_flag_end))

    def __flag(self) -> tuple[bool, str]:
        self.__output.prepare_print_function("flag")
        token = self.__stream.get_token()
        if token[1] != TOKEN_TYPES.FLAG:
            self.__stream.unget(1)
            self.__output.discard_print_function()
            return False, ""

        flag_id = self.__check_expected_token(VALUE_TYPES.IDENTIFIER)[0]
        self.__output.accept_print_function()
        return True, flag_id


    def __flag_body(self, list_of_unchecked_flags: list[str], dict_flag_labels: dict[str, tuple[int, int]]) -> bool:
        """
        :parameter dict_flag_labels - {"user flag": (label, return to flag list check label)}
        """

        self.__output.prepare_print_function("flag_body")
        flag = self.__flag()
        if not flag[0]:
            self.__output.discard_print_function()
            return False
        self.__check_expected_token(TOKEN_TYPES.COLON)

        # Label: body start
        label_body_start, returt_to = dict_flag_labels[flag[1]]
        self.__assign_label_position(label_body_start)

        self.__body()

        # Label: return to flag chooser
        self.__jump_on_label(returt_to)

        # check semantic
        if flag[1] not in list_of_unchecked_flags:
            self.__output.print_semantic_error(self.__stream.get_line(), f"{flag[1]} is undeclared or duplicates existing flag of flag-body")
            exit(1)
        else:
            list_of_unchecked_flags.remove(flag[1])

        self.__output.accept_print_function()
        return True


def process_start_args() -> tuple[str, bool] | None:
    """
    :return: file path
    """

    # get check amount of params
    startup_args: list[str] = sys.argv
    if len(startup_args) < 2:
        print_console("Error -> TP syntax (Startup): no file was provided", CONSOLE_COLORS.ERROR)
        return None
    if len(startup_args) > 2 and startup_args[2] != "-v":
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

    return file_path_param, len(startup_args) == 3


def main_revers():
    args: tuple[str, bool] | None = process_start_args()
    if args is None: exit(1)

    file_path: str   = args[0]
    is_verbose: bool = args[1]

    # ----------------------------------------------
    lexer_result: tuple[dict, dict, list] = lexer(file_path)
    syntax_stream = Syntax_input(lexer_result)
    syntax_output = Syntax_print(False)
    syntax_var_table = Syntax_var_table()
    label_table = Label_table()
    rpn_out = RPN_out(is_verbose)
    syntax = Syntax(syntax_stream, syntax_output, syntax_var_table, label_table, rpn_out)
    syntax.run()
    rpn_out.write_to_file(os.path.dirname(file_path), os.path.basename(file_path).rsplit('.', 1)[0],
                          syntax_var_table, label_table)

if __name__ == '__main__':
    main_revers()
