from enum import Enum

class TOKEN_TYPES(Enum):
    # Math
    OP_ASSIGN = "="
    OP_PLUS = "+"
    OP_MINUS = "-"
    OP_MULTI = "*"
    OP_DIVIDE = "/"
    OP_POWER = "^"

    # Logical
    OP_AND = "and"
    OP_OR = "or"
    OP_NOT = "not"

    # Comparison
    OP_EQUAL = "=="
    OP_NOT_EQUAL = "!="
    OP_BIGGER_EQUAL = ">="
    OP_LESS_EQUAL = "<="
    OP_LESS = "<"
    OP_BIGGER = ">"

    # Brackets
    BRACKET_L = "("
    BRACKET_R = ")"
    CURVE_L = "{"
    CURVE_R = "}"
    SQUARE_L = "["
    SQUARE_R = "]"
    COMPARISON_BRACKET = "|"

    # Special
    END_STATEMENT = ";"
    # FLAG = "#"
    # COLON = ":"
    # PARAM_SEPARATOR = ","
    # EOF = ""

    # RPN tokens
    OP_UMINUS            = "uminus"
    OP_INPUT_INT         = "input_int"
    OP_INPUT_FLOAT       = "input_float"
    OP_INPUT_BOOL        = "input_bool"
    OP_OUT_STR           = "out_str"
    OP_OUT_INT           = "out_int"
    OP_OUT_FLOAT         = "out_float"
    OP_OUT_BOOL          = "out_bool"
    OP_JMP               = "jmp"
    OP_JT                = "jt"
    OP_JF                = "jf"

class RPN_TYPES(Enum):
    L_VAL = "l-value"
    R_VAL = "r-value"
    LABEL = "label"
    OP_LABEL_DECLARE = "label_declare"

class VALUE_TYPES(Enum):
    IDENTIFIER = "ident"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STRING = "string"