from Lexer.lexer   import lexer_run as lexer
from syntax_stream import *
from syntax_print  import *
from syntax_consts import *
import sys
import os

class Syntax:
    def __init__(self, stream: Syntax_input, output: Syntax_print):
        self.stream = stream
        self.output = output

    def run(self):
        self.program()


    def check_token(self):
        """
            Check for expected token
        """
        pass

    def program(self): pass

    #  --- variable ---
    def declaration(self) -> bool: pass

    def initialization(self) -> bool: pass

    def assign(self) -> bool: pass

    def print(self) -> bool: pass

    def input(self) -> bool: pass

    def cycle_while(self) -> bool: pass

    def cycle_for(self) -> bool: pass

    def cycle_do(self) -> bool: pass

    def conditional_flags(self) -> bool: pass

    def conditional_switch(self) -> bool: pass

    def conditional_if(self) -> bool: pass

def process_start_args() -> str | None:
    """
    :return: file path
    """

    # get check amount of params
    startup_args: list[str] = sys.argv
    if len(startup_args) < 1:
        print_console("Error -> TP syntax (Startup): no file was provided", CONSOLE_COLORS.ERROR)
        return None
    if len(startup_args) > 1:
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
    syntax = Syntax(syntax_stream, syntax_output)
    syntax.run()


if __name__ == '__main__':
    try:
        main_syntax()
    except:
        pass