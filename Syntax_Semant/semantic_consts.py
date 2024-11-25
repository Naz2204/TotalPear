from enum import Enum
from semantic_syntax_consts import TOKEN_TYPES, KEYWORDS

class SEMANTIC_TYPE(Enum):
    INT    = "integer"
    FLOAT  = "real"
    BOOL   = "bool"

KEYWORDS_TO_SEMANTIC_TYPE: dict[KEYWORDS, SEMANTIC_TYPE] = {
    KEYWORDS.INT:   SEMANTIC_TYPE.INT,
    KEYWORDS.FLOAT: SEMANTIC_TYPE.FLOAT,
    KEYWORDS.BOOL:  SEMANTIC_TYPE.BOOL
}

class SEMANTIC_MATH_OPERATOR(Enum):
    PLUS   = "+"
    MINUS  = "-"
    MULTI  = "*"
    DIVIDE = "/"
    POWER  = "^"

SEMANTIC_MATH_OPERATOR_VALUES = tuple(x.value for x in SEMANTIC_MATH_OPERATOR)

class SEMANTIC_LOGICAL_OPERATOR(Enum):
    AND    = "and"
    OR     = "or"
    NOT    = "not"

SEMANTIC_LOGICAL_OPERATOR_VALUES = tuple(x.value for x in SEMANTIC_LOGICAL_OPERATOR)

class SEMANTIC_COMPARISON_OPERATOR(Enum):
    OP_EQUAL        = "=="
    OP_NOT_EQUAL    = "!="
    OP_BIGGER_EQUAL = ">="
    OP_LESS_EQUAL   = "<="
    OP_LESS         = "<"
    OP_BIGGER       = ">"

SEMANTIC_COMPARISON_OPERATOR_VALUES = tuple(x.value for x in SEMANTIC_COMPARISON_OPERATOR)
SEMANTIC_COMPARISON_OPERATOR_VALUES_NON_LOGIC = (
    SEMANTIC_COMPARISON_OPERATOR.OP_BIGGER_EQUAL,
    SEMANTIC_COMPARISON_OPERATOR.OP_LESS_EQUAL,
    SEMANTIC_COMPARISON_OPERATOR.OP_BIGGER,
    SEMANTIC_COMPARISON_OPERATOR.OP_LESS
)

SEMANTIC_COMPARISON_OPERATOR_VALUES_LOGIC = (
    SEMANTIC_COMPARISON_OPERATOR.OP_EQUAL,
    SEMANTIC_COMPARISON_OPERATOR.OP_NOT_EQUAL
)

def TOKEN_TYPE_TO_SEMANTIC_OPERATION(token_type: TOKEN_TYPES) -> SEMANTIC_MATH_OPERATOR       \
  | SEMANTIC_LOGICAL_OPERATOR | SEMANTIC_COMPARISON_OPERATOR | None:
    token_value = token_type.value[1]
    if token_value in SEMANTIC_MATH_OPERATOR_VALUES:
        return SEMANTIC_MATH_OPERATOR(token_value)
    elif token_value in SEMANTIC_COMPARISON_OPERATOR_VALUES:
        return SEMANTIC_COMPARISON_OPERATOR(token_value)
    elif token_value in SEMANTIC_LOGICAL_OPERATOR_VALUES:
        return SEMANTIC_LOGICAL_OPERATOR(token_value)

    return None

def expression_type (left: SEMANTIC_TYPE | str, right: SEMANTIC_TYPE | str,
                     op: TOKEN_TYPES) -> SEMANTIC_TYPE | str:
    '''
    :brief:  Unary check is put on syntax cheker
    :return: SEMANTIC_TYPE - on success, str - on error (str is an error message)
    '''
    if type(left) is str: # Monad
        return left
    elif type(right) is str: # Monad
        return right

    op = TOKEN_TYPE_TO_SEMANTIC_OPERATION(op)

    math_type = left in [SEMANTIC_TYPE.INT, SEMANTIC_TYPE.FLOAT]
    math_type = math_type or (right in [SEMANTIC_TYPE.INT, SEMANTIC_TYPE.FLOAT])

    bool_type = left is SEMANTIC_TYPE.BOOL or right is SEMANTIC_TYPE.BOOL

    # operands type error
    if math_type and bool_type:
        return (
            "Incorrect type of second operand (should be " +
            ("arithmetic" if right is SEMANTIC_TYPE.BOOL else "logical") + ")"
        )

    # operator error - type
    if   bool_type and (type(op) is not SEMANTIC_LOGICAL_OPERATOR):
        return "Incorrect type of operator (should be logical)"
    elif math_type and (type(op) is not SEMANTIC_MATH_OPERATOR):
        return "Incorrect type of operator (should be arithmetic)"
    elif bool_type and (op in SEMANTIC_COMPARISON_OPERATOR_VALUES_NON_LOGIC):
        return "Incorrect type of comparison operator (should be == or != for logical operands)"


    # comp | logical
    if bool_type: # type(op) in (SEMANTIC_COMPARISON_OPERATOR, SEMANTIC_LOGICAL_OPERATOR) - is result of bool
        return SEMANTIC_TYPE.BOOL

    # real or int for math operations
    has_real = left is SEMANTIC_TYPE.FLOAT or right is SEMANTIC_TYPE.FLOAT
    if has_real or (op in (SEMANTIC_MATH_OPERATOR.POWER, SEMANTIC_MATH_OPERATOR.DIVIDE)):
        return SEMANTIC_TYPE.FLOAT
    else: # both integer and op = {+, -, *}
        return SEMANTIC_TYPE.INT

def expression_type_unary (op: TOKEN_TYPES, right: SEMANTIC_TYPE | str) -> SEMANTIC_TYPE | str:
    if type(right) is str: return right # Monad

    op = TOKEN_TYPE_TO_SEMANTIC_OPERATION(op)

    if (type(op) is SEMANTIC_MATH_OPERATOR) and (right in (SEMANTIC_TYPE.FLOAT, SEMANTIC_TYPE.INT)):
        return right
    elif (type(op) is SEMANTIC_LOGICAL_OPERATOR) and (right is SEMANTIC_TYPE.BOOL):
        return right

    # errors
    if type(op) is SEMANTIC_MATH_OPERATOR: #right is SEMANTIC_TYPE.BOOL
        return f"Incorrect type of operand: \'{op}\', requires arithmetic value"
    else: # right is Math and op is Logical
        return f"Incorrect type of operand: \'{op}\', requires logical value"
