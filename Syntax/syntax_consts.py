from enum import Enum

class CONSOLE_COLORS(Enum):
    ERROR   = '\033[31m'
    WARNING = '\033[93m'
    OK      = '\033[32m'
    NORMAL  = '\033[0m'


FILE_TYPE_IN:  str = ".tp"
FILE_TYPE_OUT: str = ".tpsynt"