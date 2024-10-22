from enum import Enum

class CONSOLE_COLORS(Enum):
    ERROR   = '\033[31m'
    WARNING = '\033[93m'
    OK      = '\033[32m'
    NORMAL  = '\033[0m'


FILE_TYPE_IN:  str = ".tp"
FILE_TYPE_OUT: str = ".tpsynt"

class KEYWORDS(Enum):
    FLOAT        = "float"
    INT          = "int"
    BOOL         = "bool"
    PRINT        = "print"
    INPUT_INT    = "inputInt"
    INPUT_FLOAT  = "inputFloat"
    INPUT_BOOL   = "inputBool"
    IF           = "if"
    WHILE        = "while"
    DO           = "do"
    FOR          = "for"
    ELIF         = "elif"
    ELSE         = "else"
    SWITCH       = "switch"
    CASE         = "case"
    DEFAULT      = "default"
    FLAG_IF      = "flagIf"

KEYWORDS_VALUES = [x.value for x in KEYWORDS]

class TOKEN_TYPES(Enum):
    # Math
    OP_ASSIGN = "op_assign", "="
    OP_PLUS = "op_plus", "+"
    OP_MINUS = "op_minus", "-"
    OP_MULTI = "op_multi", "*"
    OP_DIVIDE = "op_divide", "/"
    OP_POWER = "op_power", "^"

    # Logical
    OP_AND = "op_and", "and"
    OP_OR = "op_or", "or"
    OP_NOT = "op_not", "not"

    # Comparison
    OP_EQUAL = "op_equal", "=="
    OP_NOT_EQUAL = "op_not_equal", "!="
    OP_BIGGER_EQUAL = "op_bigger_equal", ">="
    OP_LESS_EQUAL = "op_less_equal", "<="
    OP_LESS = "op_less", "<"
    OP_BIGGER = "op_bigger", ">"

    # Brackets
    BRACKET_L = "bracket_l", "("
    BRACKET_R = "bracket_r", ")"
    CURVE_L = "curve_l", "{"
    CURVE_R = "curve_r", "}"
    SQUARE_L = "square_l", "["
    SQUARE_R = "square_r", "]"

    # Special
    END_STATEMENT = "end_statement", ";"
    FLAG = "flag", "#"
    COLON = "colon", ":"
    PARAM_SEPARATOR = "param_separator", ";"

class VALUE_TYPES(Enum):
    IDENTIFIER = "ident"
    INT = "integer"
    FLOAT = "real"
    BOOL = "boolean"
    STRING = "string"

VALUE_TYPES_VALUES = [x.value for x in VALUE_TYPES]

