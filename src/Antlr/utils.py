from Antlr.consts import *
from Antlr.tables import Var_table
from Antlr.dijkstra_algo import Dijkstra
import re

def check_assign_type(left_type: VALUE_TYPES, right_type: VALUE_TYPES) -> bool:
    math = left_type in (VALUE_TYPES.FLOAT, VALUE_TYPES.INT) and \
                     right_type in (VALUE_TYPES.FLOAT, VALUE_TYPES.INT)
    bool_ = left_type is VALUE_TYPES.BOOL and right_type is VALUE_TYPES.BOOL
    okay = math or bool_
    return okay

def check_type_expression_is_math(line_op: str, var_table: Var_table) -> bool | str:
    line: str = line_op.replace('(', '').strip()

    math  = re.match(r'^([0-9\-+/*^])', line) is not None
    bool_ = re.match(r'^(true|false|and|or|not)((?=[^\w$]))', line + ' ') is not None
    bool_ = bool_ or line[0] == '|' # for comparison

    if not math and not bool_:
        var_match = re.match(r'^[$a-zA-Z_][$\w]*', line)
        if var_match is None:
            return "Unknown error while processing expression type determination"

        var_match = var_match[0]

        var = var_table.get_type(var_match)
        unknown = var is None
        if unknown:
            return "Unknown identifier"

        math = var in [VALUE_TYPES.INT, VALUE_TYPES.FLOAT]
        # bool = var is VALUE_TYPES.BOOL

    return math

def jump_on_label(dijkstra_worker: Dijkstra, label: str, jump_type: TOKEN_TYPES = TOKEN_TYPES.OP_JMP) -> None:
    if jump_type not in (TOKEN_TYPES.OP_JMP, TOKEN_TYPES.OP_JT, TOKEN_TYPES.OP_JF):
        print("Internal error, wrong type passed as parameter")
    else:
        dijkstra_worker.push(jump_type)
        dijkstra_worker.push(RPN_TYPES.LABEL, label)
        dijkstra_worker.push(TOKEN_TYPES.END_STATEMENT)

def assign_label_position(dijkstra_worker: Dijkstra, label: str) -> None:
    dijkstra_worker.push(RPN_TYPES.LABEL, label)
    dijkstra_worker.push(RPN_TYPES.OP_LABEL_DECLARE, RPN_TYPES.OP_LABEL_DECLARE.value)


# ---

MATH_OPERATOR: tuple[TOKEN_TYPES, ...] = (
    TOKEN_TYPES.OP_PLUS,
    TOKEN_TYPES.OP_MINUS,
    TOKEN_TYPES.OP_POWER,
    TOKEN_TYPES.OP_MULTI,
    TOKEN_TYPES.OP_DIVIDE,
    TOKEN_TYPES.OP_UMINUS
)


COMPARISON_OPERATOR: tuple[TOKEN_TYPES, ...] = (
    TOKEN_TYPES.OP_EQUAL,
    TOKEN_TYPES.OP_NOT_EQUAL,
    TOKEN_TYPES.OP_BIGGER,
    TOKEN_TYPES.OP_BIGGER_EQUAL,
    TOKEN_TYPES.OP_LESS,
    TOKEN_TYPES.OP_LESS_EQUAL
)

COMPARISON_LOGIC_OPERATOR: tuple[TOKEN_TYPES, ...] = (
    TOKEN_TYPES.OP_EQUAL,
    TOKEN_TYPES.OP_NOT_EQUAL
)


LOGICAL_OPERATOR: tuple[TOKEN_TYPES, ...] = (
    TOKEN_TYPES.OP_AND,
    TOKEN_TYPES.OP_OR,
    TOKEN_TYPES.OP_NOT
)

def expression_type_comparison (left: VALUE_TYPES, right: VALUE_TYPES, op: TOKEN_TYPES) -> VALUE_TYPES | str:

    if left is VALUE_TYPES.BOOL and right is not VALUE_TYPES.BOOL:
        return "No logical expression after comparison sign on line"

    elif left is not VALUE_TYPES.BOOL and right is VALUE_TYPES.BOOL:
        return "No math expression after comparison sign on line"

    bool_type = left is VALUE_TYPES.BOOL or right is VALUE_TYPES.BOOL

    if bool_type and (op not in COMPARISON_LOGIC_OPERATOR):
        return "Incorrect type of comparison operator (should be == or != for logical operands)"

    return VALUE_TYPES.BOOL


def expression_type (left: VALUE_TYPES | str, right: VALUE_TYPES | str,
                     op: TOKEN_TYPES) -> VALUE_TYPES | str:
    '''
    :brief:  Unary check is put on syntax cheker
    :return: SEMANTIC_TYPE - on success, str - on error (str is an error message)
    '''
    if type(left) is str: # Monad
        return left
    elif type(right) is str: # Monad
        return right

    # ---

    if op in COMPARISON_OPERATOR:
        return expression_type_comparison(left, right, op)

    # ---

    math_type = left in [VALUE_TYPES.INT, VALUE_TYPES.FLOAT]
    math_type = math_type or (right in [VALUE_TYPES.INT, VALUE_TYPES.FLOAT])

    bool_type = left is VALUE_TYPES.BOOL or right is VALUE_TYPES.BOOL

    # operands type error
    if math_type and bool_type:
        return (
            "Incorrect type of second operand (should be " +
            ("arithmetic" if right is VALUE_TYPES.BOOL else "logical") + ")"
        )

    # operator error - type
    if   bool_type and (op not in LOGICAL_OPERATOR):
        return "Incorrect type of operator (should be logical)"
    elif math_type and (op not in MATH_OPERATOR):
        return "Incorrect type of operator (should be arithmetic)"


    # logical
    if bool_type: # type(op) in (SEMANTIC_LOGICAL_OPERATOR) - is result of bool
        return VALUE_TYPES.BOOL

    # real or int for math operations
    has_real = left is VALUE_TYPES.FLOAT or right is VALUE_TYPES.FLOAT
    if has_real or (op in (TOKEN_TYPES.OP_POWER, TOKEN_TYPES.OP_DIVIDE)):
        return VALUE_TYPES.FLOAT
    else: # both integer and op = {+, -, *}
        return VALUE_TYPES.INT

def expression_type_unary (op: TOKEN_TYPES, right: VALUE_TYPES | str) -> VALUE_TYPES | str:
    if type(right) is str: return right # Monad

    if (op is TOKEN_TYPES.OP_UMINUS) and (right in (VALUE_TYPES.FLOAT, VALUE_TYPES.INT)):
        return right
    elif (op is TOKEN_TYPES.OP_NOT) and (right is VALUE_TYPES.BOOL):
        return right

    # errors
    if op in MATH_OPERATOR: #right is SEMANTIC_TYPE.BOOL
        return f"Incorrect type of operand: \'{op}\', requires arithmetic value"
    else: # right is Math and op is Logical
        return f"Incorrect type of operand: \'{op}\', requires logical value"

