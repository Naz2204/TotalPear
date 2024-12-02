from Lexer.lexer_print import *
import os


class Lexer_file:
    usage: str = "to be able take char and put back - stream as std::istream"

    def __init__(self, file_path) -> None:
        with open(file_path, "r", encoding="utf-8") as reader:
            self.text = reader.read()
        self.char_index = 0
        self.line_counter = 1
        self.file_name = os.path.basename(file_path)

    def get_char(self) -> str:
        if self.char_index == len(self.text):
            print_console("Error -> TP lexer (Runtime): TP lexer internal error, incorrect stream usage", CONSOLE_COLORS.ERROR)
            exit(2) 

        result = self.text[self.char_index]
        if result == '\n': 
            self.line_counter += 1
        self.char_index += 1
        return result

    def unget_char(self):
        if self.char_index == 0:
            print_console("Error -> TP lexer (Runtime): TP lexer internal error, incorrect stream usage", CONSOLE_COLORS.ERROR)
            exit(2) 

        self.char_index -= 1
        if self.text[self.char_index] == '\n': 
            self.line_counter -= 1
    
    def get_current_char_line_position(self) -> int:
        if self.line_counter == 0: return self.char_index + 1
        
        start_index: int = self.char_index
        if self.text[start_index] == '\n':
            start_index -= 1

        while self.text[start_index] != '\n': start_index -= 1
        start_index += 1

        return self.char_index - start_index + 1 # for read comfort

    def get_current_line_counter(self) -> int:
        # get current line of \n char
        if self.char_index != 0 and self.text[self.char_index - 1] == '\n': 
            return self.line_counter - 1

        return self.line_counter

    def empty(self) -> bool:
        return self.char_index == len(self.text)

    def get_current_line(self) -> str:
        start_line_index: int = self.char_index

        if self.char_index > 0 and self.text[self.char_index - 1] != '\n':
            start_line_index -= 1   # to remove posibility that self.text[start_line_index] == '\n'
                                    # which is end of current line

        while start_line_index != 0 and self.text[start_line_index - 1] != '\n':
            start_line_index -= 1
        
        end_line_index: int = start_line_index
        while end_line_index + 1 < len(self.text) and self.text[end_line_index + 1] != '\n':
            end_line_index += 1

        return self.text[start_line_index : end_line_index + 1]

    def get_file_name(self) -> str:
        return self.file_name