from enum import Enum

FILE_TYPE_IN:  str = ".tp"
FILE_TYPE_OUT: str = ".tplex"


class CONSOLE_COLORS(Enum):
    ERROR   = '\033[31m'
    WARNING = '\033[93m'
    OK      = '\033[32m'
    NORMAL  = '\033[0m'


TOKENS_TABLE = {
    # Keywords list
    "float": "keyword", "int": "keyword", "bool": "keyword",
    "print": "keyword", "inputInt": "keyword", "inputFloat": "keyword",
    "inputBool": "keyword", "if": "keyword", "while": "keyword",
    "do": "keyword", "for": "keyword", "elif": "keyword",
    "else": "keyword", "switch": "keyword", "case": "keyword",
    "default": "keyword", "flagIf": "keyword",

    # Math
    "=": "op_assign", "+": "op_plus", "-": "op_minus",
    "*": "op_multi", "/": "op_divide", "^": "op_power",

    # Logical
    "and": "op_and", "or": "op_or", "not": "op_not",

    # Comparison
    "==": "op_equal", "!=": "op_not_equal", ">=": "op_bigger_equal",
    "<=": "op_less_equal", "<": "op_less", ">": "op_bigger",

    # Brackets
    "(": "bracket_l", ")": "bracket_r",
    "{": "curve_l", "}": "curve_r",
    "[": "square_l", "]": "square_r",
    "|": "conditional_bracket",

    # Spacing
    " ": "space", "\t": "tab", "\n": "newline",

    # Special
    ";": "end_statement", "//": "comment", "#": "flag",
    ":": "colon",         "," : "param_separator"
}

IDENTIFIER_TOKEN = {
    11: "ident"
}

STRING_TOKEN = {
    61: "string"
}

LITERAL_TOKENS_TABLE = {
    22: "integer", 211: "real"
}

IDENT_OR_LITERAL = {
    "true": "boolean", "false": "boolean"
}


class CLASS_ALPHABET(Enum):
    MAIN_LETTER         = "mainLetter"
    DIGIT               = "digit"
    DOT                 = "dot"
    WHITE_SPACE         = "whiteSpace"
    QUOTE               = "quote"
    FORWARD_SLASH       = "forwardSlash"
    NEW_LINE            = "newLine"
    SPECIAL_SIGN_SINGLE = "specialSignSingle"
    LESS_MORE           = "lessMore"
    EQUAL_SIGN          = "equalSign"
    EXCLAMATION_MARK    = "exclamationMark"
    STR_LINE            = "str"
    OTHER               = "other"


class CLASS_ERROR(Enum):
    UNKNOWN_LEXEME     = "Unknown lexeme"
    NEW_LINE_IN_QUOTES = "Multy line string is not supported. Closing quote is missing or redundant newline sign was used"
    NOT_EQUAL_NO_EQUAL = "Single '!' sign is not supported. Suggest deleting it or replacing with '!=' operator"


REGEX_TO_CLASS_ALPHABET = {
    r"[a-zA-Z$_]":             CLASS_ALPHABET.MAIN_LETTER,
    r"[0-9]":                  CLASS_ALPHABET.DIGIT,
    r"\.":                     CLASS_ALPHABET.DOT,
    r"[ \t]":                  CLASS_ALPHABET.WHITE_SPACE,
    r"\"":                     CLASS_ALPHABET.QUOTE,
    r"/":                      CLASS_ALPHABET.FORWARD_SLASH,
    r"\n":                     CLASS_ALPHABET.NEW_LINE,
    r"[,()\[\]{}#+\-*\^:;|]":  CLASS_ALPHABET.SPECIAL_SIGN_SINGLE,
    r"[<>]":                   CLASS_ALPHABET.LESS_MORE,
    r"=":                      CLASS_ALPHABET.EQUAL_SIGN,
    r"!":                      CLASS_ALPHABET.EXCLAMATION_MARK,
    r"[^\n]":                  CLASS_ALPHABET.STR_LINE  # this regex has to be in the end
}

STATE_TRANSITION_TABLE = {
    (0, CLASS_ALPHABET.WHITE_SPACE): 0,

    (0, CLASS_ALPHABET.MAIN_LETTER): 1,
    (1, CLASS_ALPHABET.MAIN_LETTER): 1,
    (1, CLASS_ALPHABET.DIGIT): 1,
    (1, CLASS_ALPHABET.OTHER): 11,

    (0,  CLASS_ALPHABET.DIGIT): 2,
    (2,  CLASS_ALPHABET.DIGIT): 2,
    (2,  CLASS_ALPHABET.DOT): 21,
    (21, CLASS_ALPHABET.DIGIT): 21,
    (21, CLASS_ALPHABET.OTHER): 211,
    (2,  CLASS_ALPHABET.OTHER): 22,


    (0,  CLASS_ALPHABET.EXCLAMATION_MARK): 31,
    (31, CLASS_ALPHABET.OTHER): 311,
    (31, CLASS_ALPHABET.EQUAL_SIGN): 312,
    (0,  CLASS_ALPHABET.LESS_MORE): 32,
    (0,  CLASS_ALPHABET.EQUAL_SIGN): 32,
    (32, CLASS_ALPHABET.EQUAL_SIGN): 312,
    (32, CLASS_ALPHABET.OTHER): 321,

    (0,  CLASS_ALPHABET.SPECIAL_SIGN_SINGLE): 33,


    (0,  CLASS_ALPHABET.FORWARD_SLASH): 4,
    (4,  CLASS_ALPHABET.OTHER): 41,
    (4,  CLASS_ALPHABET.FORWARD_SLASH): 42,
    (42, CLASS_ALPHABET.OTHER): 42,
    (42, CLASS_ALPHABET.NEW_LINE): 5,

    (0, CLASS_ALPHABET.NEW_LINE): 5,

    (0, CLASS_ALPHABET.QUOTE): 6,
    (6, CLASS_ALPHABET.OTHER): 6,
    (6, CLASS_ALPHABET.QUOTE): 61,
    (6, CLASS_ALPHABET.NEW_LINE): 62,

    (0, CLASS_ALPHABET.OTHER): 7
}

STATE_START   = 0
STATE_FINISH  = (11, 211, 22, 311, 312, 321, 33, 41, 5, 61, 62, 7)
STATE_ERROR   = {
    311: CLASS_ERROR.NOT_EQUAL_NO_EQUAL,
    62:  CLASS_ERROR.NEW_LINE_IN_QUOTES,
    7:   CLASS_ERROR.UNKNOWN_LEXEME
}
STATE_PUTBACK = (11, 211, 22, 321, 41)