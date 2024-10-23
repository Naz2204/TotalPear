import sys
import re
from Lexer.lexer_tables import *
from Lexer.lexer_stream import *
import json


class Lexer:
    usage: str = "main class produce results"

    def __init__(self, *, work_file: Lexer_file, id_table: Lexer_ident_table, results_table: Lexer_results_table,
                 literal_table: Lexer_literal_table) -> None:
        self.state = 0
        self.stream = work_file

        self.id_table = id_table
        self.literal_table = literal_table

        self.result_table = results_table

    @staticmethod
    def character_to_class(character: str) -> CLASS_ALPHABET:
        for regex in REGEX_TO_CLASS_ALPHABET.keys():
            if re.match(regex, character):
                return REGEX_TO_CLASS_ALPHABET[regex]

        return CLASS_ALPHABET.OTHER

    @staticmethod
    def next_state(state: int, character: str) -> int:
        character_type = Lexer.character_to_class(character)
        # ok
        state_tuple = (state, character_type)
        if state_tuple in STATE_TRANSITION_TABLE:
            # print_console(f"{state_tuple}", CONSOLE_COLORS.WARNING)
            return STATE_TRANSITION_TABLE[state_tuple]

        # not found
        other_tuple = (state, CLASS_ALPHABET.OTHER)
        if other_tuple in STATE_TRANSITION_TABLE:
            return STATE_TRANSITION_TABLE[other_tuple]

        # error - unreachable code
        print_console("Error -> TP lexer (Runtime): TP lexer internal error, state dead-end", CONSOLE_COLORS.ERROR)
        exit(2)

    def end_lexeme_processing(self, lexeme: str) -> None:
        # New line state or end of comment lexeme (both should be ignored): state 5
        if self.state == 5:
            return

        token_type: str = ''
        id_var: str = ''

        if self.state in STATE_ERROR:
            # Error : all error states
            print_console("Error -> TP lexer (Runtime):", CONSOLE_COLORS.ERROR)
            self.print_lexer_error(STATE_ERROR[self.state].value)
            exit(1)

        elif lexeme in TOKENS_TABLE:
            # SPECIAL TOKEN (not literal) : state 312, 321, 33, 41, part 11
            token_type = TOKENS_TABLE[lexeme]

        elif self.state in LITERAL_TOKENS_TABLE:
            # Literal : state 211, 22
            token_type = LITERAL_TOKENS_TABLE[self.state]
            id_var_or_none: str | None = self.literal_table.find(lexeme)
            id_var = (id_var_or_none if id_var_or_none is not None else self.literal_table.add(lexeme, token_type))

        elif lexeme in IDENT_OR_LITERAL:
            # Literal : part 11
            token_type = IDENT_OR_LITERAL[lexeme]
            id_var_or_none: str | None = self.literal_table.find(lexeme)
            id_var = (id_var_or_none if id_var_or_none is not None else self.literal_table.add(lexeme, token_type))

        elif self.state in IDENTIFIER_TOKEN:
            # Identifier : state 11
            id_var_or_none: str | None = self.id_table.find(lexeme)
            id_var = (id_var_or_none if id_var_or_none is not None else self.id_table.add(lexeme))
            token_type = IDENTIFIER_TOKEN[self.state]

        elif self.state in STRING_TOKEN:
            # String : state 61
            lexeme = lexeme[1:-1]
            token_type = STRING_TOKEN[self.state]
            id_var_or_none: str | None = self.literal_table.find(lexeme)
            id_var = (id_var_or_none if id_var_or_none is not None else self.literal_table.add(lexeme, token_type))

        else:
            print(lexeme, self.state)
            print_console("Error -> TP lexer (Runtime): TP lexer internal error, state dead-end", CONSOLE_COLORS.ERROR)
            exit(2)

        self.result_table.add(self.stream.get_current_line_counter(), lexeme, token_type, id_var)

    def run(self) -> None:
        # self.state = STATE_START
        lexeme: str = ''

        while not self.stream.empty():
            character = self.stream.get_char()
            self.state = Lexer.next_state(self.state, character)

            if self.state == STATE_START: continue  # do nothing

            if self.state not in STATE_PUTBACK:
                lexeme += character
            else:
                self.stream.unget_char()

            if self.state in STATE_FINISH:
                self.end_lexeme_processing(lexeme)
                self.state = STATE_START
                lexeme = ''

        print_console("Success -> TP lexer (Runtime): lexer finished work correctly", CONSOLE_COLORS.OK)

    def print_lexer_error(self, error_text: str):
        """
        assumes that next char in stream is incorrect
        """
        self.stream.unget_char() # get back to error - will be restored to current in the end
        """
        file.py (40:3)   !b = 3;
                         ^    
        Error unknown symbol on line 40
        """
        ERROR_SPACES_LEN: int = 4
        line_of_error: int = self.stream.get_current_line_counter()
        error_space:   str = " " * ERROR_SPACES_LEN
        error_place:   str = f"{self.stream.get_file_name()} ({line_of_error}:{self.stream.get_current_char_line_position()})"
        error_line:    str = self.stream.get_current_line()
        error_header:  str = f"{error_place}{error_space}{error_line.lstrip()}"

        # -----
        error_line_leading_ws = len(error_line) - len(error_line.lstrip())
        # -----
        error_place_int: int = self.stream.get_current_char_line_position() - 1 - error_line_leading_ws
        error_place_int += len(error_space) + len(error_place)
        error_pointer: str = " " * error_place_int + "^"

        # -----
        error_message: str = f"{error_text} on line {line_of_error}"

        # -----
        to_print: str = error_header + '\n' + error_pointer + '\n' + error_message

        print_console(to_print, CONSOLE_COLORS.ERROR)

        self.stream.get_char() # restore of state

    def print_results(self):
        LINE_LENGTH = 30
        print_console("Lexical table".center(LINE_LENGTH, '='))
        print_table(self.result_table.get_table(True))
        print_console("Identifier table".center(LINE_LENGTH, '='))
        print_table(self.id_table.get_table(True))
        print_console("Literals table".center(LINE_LENGTH, '='))
        print_table(self.literal_table.get_table(True))

    def print_results_to_file(self, dir_path: str, file_name: str) -> None:
        to_write: dict[str, list] = {
            'result_table':     self.result_table.get_table(True),
            'literal_table':    self.literal_table.get_table(True),
            'identifier_table': self.id_table.get_table(True)
        }
        try:
            with open(dir_path + "/" + file_name + FILE_TYPE_OUT, "w") as file:
                json.dump(to_write, file, indent=4)
        except:
            print_console("Error -> TP lexer (Finishing): error occurred while writing result to file",
                          CONSOLE_COLORS.ERROR)
            exit(1)
        print_console("Success -> TP lexer (Finishing): writing results to file were successful", CONSOLE_COLORS.OK)



def process_start_args() -> tuple[str, bool] | None:
    """
    :return: file path and bool (is_verbose)
    """

    # get check amount of params
    startup_args: list[str] = sys.argv
    if len(startup_args) < 2:
        print_console("Error -> TP lexer (Startup): no file was provided", CONSOLE_COLORS.ERROR)
        return None
    if len(startup_args) > 2 and startup_args[2] != "-v":
        print_console("Error -> TP lexer (Startup): too many parameters were provided", CONSOLE_COLORS.ERROR)
        return None

    # check if param is absolute or relative
    file_path_param = sys.argv[1]
    if not os.path.isabs(file_path_param):
        file_path_param = os.getcwd() + '\\' + file_path_param

    # check if path exists
    if not os.path.isfile(file_path_param):
        print_console(f"Error -> TP lexer (Startup): no file was found by address {file_path_param}",
                      CONSOLE_COLORS.ERROR)
        return None

    print_console(f"TP lexer (Startup): file was found - {file_path_param}", CONSOLE_COLORS.OK)

    # check file type
    if not file_path_param.endswith(FILE_TYPE_IN):
        print_console("Error -> TP lexer (Startup): incorrect file type", CONSOLE_COLORS.ERROR)
        return None

    return (file_path_param, len(startup_args) == 3)


def lexer_run(file_path: str) -> tuple[dict, dict, list]:
    work_file     = Lexer_file(file_path)
    id_table      = Lexer_ident_table()
    results_table = Lexer_results_table()
    literal_table = Lexer_literal_table()
    lexer = Lexer(work_file=work_file, id_table=id_table, results_table=results_table, literal_table=literal_table)
    lexer.run()
    return id_table.get_dict(), literal_table.get_dict(), results_table.get_table()

def main_lexer():
    args: tuple[str, bool] | None = process_start_args()
    if args is None: exit(1)

    file_path: str   = args[0]
    is_verbose: bool = args[1]

    # ----------------------------------------------
    # setup lexer
    work_file     = Lexer_file(file_path)
    id_table      = Lexer_ident_table()
    results_table = Lexer_results_table()
    literal_table = Lexer_literal_table()
    lexer = Lexer(work_file=work_file, id_table=id_table, results_table=results_table, literal_table=literal_table)
    lexer.run()
    if is_verbose:
        lexer.print_results()
    lexer.print_results_to_file(os.path.dirname(file_path), os.path.basename(file_path).rsplit('.', 1)[0])


if __name__ == '__main__':
    try:
        main_lexer()
    except: pass