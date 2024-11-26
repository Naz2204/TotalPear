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

KEYWORDS_VALUES = tuple(x.value for x in KEYWORDS)

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
    COMPARISON_BRACKET = "conditional_bracket", "|"

    # Special
    END_STATEMENT = "end_statement", ";"
    FLAG = "flag", "#"
    COLON = "colon", ":"
    PARAM_SEPARATOR = "param_separator", ","
    EOF = "eof", ""

    # RPN tokens
    OP_UMINUS            = "op_uminus",            "uminus"
    OP_INPUT_INT         = "op_input_int",          "input_int"
    OP_INPUT_FLOAT       = "op_input_float",       "input_float"
    OP_INPUT_BOOL        = "op_input_bool",        "input_bool"
    OP_OUT_STR           = "op_out_str",           "out_str"
    OP_OUT_INT           = "op_out_int",           "out_int"
    OP_OUT_FLOAT         = "op_out_float",         "out_float"
    OP_OUT_BOOL          = "op_out_bool",          "out_bool"
    OP_JMP               = "op_jmp",               "jmp"
    OP_JT                = "op_jt",                "jt"
    OP_JF                = "op_jf",                "jf"
    # OP_CAST_INT_TO_FLOAT = "op_cast_int_to_float", "int2float"
    # OP_CAST_FLOAT_TO_INT = "op_cast_float_to_int", "float2int"


class VALUE_TYPES(Enum):
    IDENTIFIER = "ident"
    INT = "integer"
    FLOAT = "real"
    BOOL = "boolean"
    STRING = "string"

VALUE_TYPES_VALUES = tuple(x.value for x in VALUE_TYPES)

class RPN_TYPES(Enum):
    L_VAL = "l-value"
    R_VAL = "r-value"
    LABEL = "label"
    OP_LABEL_DECLARE = "label_declare"

