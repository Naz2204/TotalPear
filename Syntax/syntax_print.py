from syntax_consts import CONSOLE_COLORS

class Syntax_print:
    def __init__(self): pass

def print_console(message: str, message_type: CONSOLE_COLORS = CONSOLE_COLORS.NORMAL):
    print(message_type.value + message + CONSOLE_COLORS.NORMAL.value)