import json
from Syntaxer.reverse_table import Syntax_var_table, Label_table
from Syntaxer.reverse_syntax_consts import CONSOLE_COLORS, KEYWORDS, TOKEN_TYPES, VALUE_TYPES, RPN_TYPES
from Syntaxer.reverse_semantic_consts import SEMANTIC_TYPE_TO_VALUE_TYPE
from Lexer.lexer_print import print_table as lexer_print_table

FILE_TYPE_OUT = ".il"

def print_console(message: str, message_type: CONSOLE_COLORS = CONSOLE_COLORS.NORMAL):
    print(message_type.value + message + CONSOLE_COLORS.NORMAL.value)

class Syntax_print:
    def __init__(self, is_verbose: bool):
        self.__indentation = 0
        self.__INDENTATION = "│  "
        self.__prepared_print: list[str] = []

        if not is_verbose:
            Syntax_print.prepare_print_function = lambda obj, text : None
            Syntax_print.discard_print_function = lambda obj       : None
            Syntax_print.accept_print_function  = lambda obj       : None

    @staticmethod
    def token_to_str(token: TOKEN_TYPES | KEYWORDS | VALUE_TYPES) -> str:
        if type(token) in [KEYWORDS, VALUE_TYPES]:
            return str(token.value)
        else:
            return token.value[1]

    @staticmethod
    def token_to_type_str(token: TOKEN_TYPES | KEYWORDS | VALUE_TYPES) -> str:
        if type(token) in [KEYWORDS, VALUE_TYPES]:
            return str(token.value)
        else:
            return token.value[1]

    def prepare_print_function(self, function_name: str) -> None:
        self.__prepared_print.append((self.__INDENTATION * self.__indentation) + function_name + "():")
        self.increase_indentation()

    def discard_print_function(self) -> None:
        self.__prepared_print.pop()
        self.decrease_indentation()

    def accept_print_function(self) -> None:
        self.decrease_indentation()
        for x in self.__prepared_print:
            print_console(x)

        self.__prepared_print.clear()


    def print_lexeme(self, line: str, value: str, token_type: TOKEN_TYPES | KEYWORDS | VALUE_TYPES) -> None:
        print_console((self.__INDENTATION * self.__indentation) + f"line {line} - {value} of type {self.token_to_type_str(token_type)}")

    def increase_indentation(self):
        self.__indentation += 1

    def decrease_indentation(self):
        if self.__indentation == 0:
            print_console("Error -> TP (Internal): Broken indentations - possible incorrect behavior", CONSOLE_COLORS.ERROR)
            exit(1)

        self.__indentation -= 1

    def print_incorrect_found_error(self,
                                    found: tuple[str, TOKEN_TYPES | KEYWORDS | VALUE_TYPES],
                                    expected: list[TOKEN_TYPES | KEYWORDS | VALUE_TYPES],
                                    error_line_num: int):

        if found[1] == TOKEN_TYPES.EOF:
            to_print = "Error -> TP (Syntax): Unexpected EOF\nExpected: "
        else:
            found_str1 = str(found[0])
            found_str2 = self.token_to_type_str(found[1])

            found_str = found_str1 + " of type " + found_str2 if found_str1 != found_str2 else found_str1

            to_print = ("Error -> TP (Syntax): Unexpected element on line " + str(error_line_num) + "\n" +
                        "Found element: '" + found_str + "'\n" +
                        "Expected: ")

        for i in range(len(expected) - 1):
            to_print += f"'{self.token_to_str(expected[i])}', "
        to_print += (f"'{self.token_to_str(expected[-1])}'")

        print_console(to_print, CONSOLE_COLORS.ERROR)


    def print_lexeme_error(self, error_line_num: int):
        """
        :param error_line_num: Line where error occurred
        """
        print_console("Error -> TP (Syntax): Unexpected lexeme on line " + str(error_line_num), CONSOLE_COLORS.ERROR)

    def print_no_token_error(self, error_line_num: int):
        """
        :param error_line_num: Line where error occurred
        """
        print_console("Error -> TP (Syntax): Token missing on line " + str(error_line_num), CONSOLE_COLORS.ERROR)


    def print_semantic_error(self, error_line_num: int, error_text: str):
        """
        :param error_line_num: Line where error occurred
        """
        print_console("Error -> TP (Semantic): " + error_text + " on line " + str(error_line_num), CONSOLE_COLORS.ERROR)

# ----------------------------------------------------------------

class RPN_out:
    def __init__(self, is_verbose: bool):
        self.__RPN_table: list[tuple[str, RPN_TYPES | TOKEN_TYPES | VALUE_TYPES]] = []
        self.__operators_buffer: list[tuple[TOKEN_TYPES, int]] = []
        self.__last_index = 0

        # якщо пріоритет токену на вході більше ніж у буфері - то більший вибиває менше
        # менше число не може вибити більше
        # більше число вибиває менше

        # таким чином більший пріоритет обрахунку = менше число-пріоритет

        # 1 + 2 ^ 3 -> +: 2, ^: 1
        # 1 2 3 ^ +       stack: +,     in: ^

        self.__priority_dict: dict[TOKEN_TYPES, int] = {
            TOKEN_TYPES.OP_POWER:   1,

            TOKEN_TYPES.OP_UMINUS:  2,
            TOKEN_TYPES.OP_NOT:     2,

            TOKEN_TYPES.OP_MULTI:   3,
            TOKEN_TYPES.OP_DIVIDE:  3,
            TOKEN_TYPES.OP_AND:     3,

            TOKEN_TYPES.OP_PLUS:    4,
            TOKEN_TYPES.OP_MINUS:   4,
            TOKEN_TYPES.OP_OR:      4,

            TOKEN_TYPES.OP_BIGGER:       5,
            TOKEN_TYPES.OP_BIGGER_EQUAL: 5,
            TOKEN_TYPES.OP_LESS:         5,
            TOKEN_TYPES.OP_LESS_EQUAL:   5,
            TOKEN_TYPES.OP_EQUAL:        5,
            TOKEN_TYPES.OP_NOT_EQUAL:    5,

            TOKEN_TYPES.BRACKET_R:       6,
            TOKEN_TYPES.BRACKET_L:       7,

            TOKEN_TYPES.OP_OUT_STR:   20,
            TOKEN_TYPES.OP_OUT_INT:   20,
            TOKEN_TYPES.OP_OUT_FLOAT: 20,
            TOKEN_TYPES.OP_OUT_BOOL:  20,

            TOKEN_TYPES.OP_INPUT_INT:   21,
            TOKEN_TYPES.OP_INPUT_FLOAT: 21,
            TOKEN_TYPES.OP_INPUT_BOOL:  21,

            # TOKEN_TYPES.OP_CAST_FLOAT_TO_INT: 30,
            # TOKEN_TYPES.OP_CAST_INT_TO_FLOAT: 30,

            TOKEN_TYPES.OP_ASSIGN: 50,

            TOKEN_TYPES.OP_JMP: 60,
            TOKEN_TYPES.OP_JF: 60,
            TOKEN_TYPES.OP_JT: 60,

            TOKEN_TYPES.END_STATEMENT: 100,

            TOKEN_TYPES.CURVE_R: 199,
            TOKEN_TYPES.CURVE_L: 200,
        }


        if not is_verbose:
            RPN_out.print_to_console = lambda obj : None

    def __del__(self):
        self.print_to_console()

    def add(self, token_type: RPN_TYPES | TOKEN_TYPES | VALUE_TYPES, lexeme: str | None = None) -> int:
        """
        :param lexeme: lexeme to add to RPN table
        :param token_type: type of the token
        :return: index af added lexeme
        """
        # print(token_type, lexeme)
        if token_type in TOKEN_TYPES:
            if token_type not in [TOKEN_TYPES.END_STATEMENT, TOKEN_TYPES.CURVE_L, TOKEN_TYPES.CURVE_R]:
                priority = self.__priority_dict[token_type]
                if token_type is TOKEN_TYPES.BRACKET_L:
                    self.__operators_buffer.append((token_type, priority))
                else:
                    while len(self.__operators_buffer) > 0 and self.__operators_buffer[-1][1] <= priority:
                        lexeme = self.__operators_buffer.pop(-1)[0]
                        self.__RPN_table.append((lexeme.value[1], lexeme))
                        self.__last_index += 1

                    if  token_type is TOKEN_TYPES.BRACKET_R and \
                        self.__operators_buffer[-1][0] is TOKEN_TYPES.BRACKET_L:
                        self.__operators_buffer.pop(-1)
                    else:
                        self.__operators_buffer.append((token_type, priority))
            else:
                while len(self.__operators_buffer) > 0:
                    buf = self.__operators_buffer.pop(-1)[0]
                    self.__RPN_table.append((buf.value[1], buf))
                    self.__last_index += 1

        else:
            self.__RPN_table.append((lexeme, token_type))  # self.__RPN_table.append((lexeme, token_type.value))
            self.__last_index += 1

        return self.__last_index - 1

    def print_to_console(self) -> None:
        temp_table = []
        for i, value in enumerate(self.__RPN_table):
            temp_table.append((i, value))
        lexer_print_table([["№", "postfixCode"]] + temp_table)

    def write_to_file(self, dir_path: str, file_name: str, var_table: Syntax_var_table, label_table: Label_table) -> None:
        cil = CIL(var_table, self.__RPN_table)
        section_locals = cil.locals_from_var_table()
        section_code   = cil.cil_from_code_list()
        to_write = """
.assembly extern mscorlib {}
.assembly extern utils {}
.assembly %s {}
.module %s.exe

.class private Program extends [mscorlib]System.Object {
  .method public static void Main(string[] args) cil managed {
    .locals init (
      int64   _rax_i8,
      float64 _rax_r8%s 
    )
    
    .entrypoint
    call void [utils]Utils.Reader::ChangeGlobalization()
%s
    ret    
  }
}

"""%(file_name, file_name, section_locals, section_code)
        #print(to_write)
        try:
            with open(dir_path + "/../Generated/" + file_name + FILE_TYPE_OUT, "w") as file:
                file.write(to_write)
        except:
            print_console("Error -> TP Syntax (Finishing): error occurred while writing code to file",
                          CONSOLE_COLORS.ERROR)
            exit(1)
        print_console("Success -> code successfully written to file ", CONSOLE_COLORS.OK)


# ----------------------------------------------------------------

class CIL:
    def __init__(self, var_table: Syntax_var_table, RPN_table: list[tuple[str, RPN_TYPES | TOKEN_TYPES | VALUE_TYPES]]):
        self.RPN_table = RPN_table
        self.var_table: Syntax_var_table = var_table
        
        # update var names, add USERVAR_ prefix
        self.__PREFIX = "USERVAR_"
        
        
        self.pseudo_stack: list[VALUE_TYPES] = []
        self.TAB        = ' ' * 4 
        self.TAB_locals = ' ' * 6
        
        self.__CIL_MATH = {
            TOKEN_TYPES.OP_PLUS:   "add",
            TOKEN_TYPES.OP_MINUS:  "sub",
            TOKEN_TYPES.OP_MULTI:  "mul",
            TOKEN_TYPES.OP_DIVIDE: "div",
            TOKEN_TYPES.OP_UMINUS: "neg",
            TOKEN_TYPES.OP_POWER:  "call float64 [mscorlib]System.Math::Pow(float64, float64)",

            TOKEN_TYPES.OP_AND:    "and",
            TOKEN_TYPES.OP_OR:     "or",
            TOKEN_TYPES.OP_NOT:    (f"ldc.i4 1\n{self.TAB}xor"),

            TOKEN_TYPES.OP_LESS:         "clt",
            TOKEN_TYPES.OP_LESS_EQUAL:   (f"cgt\n{self.TAB}ldc.i4 1\n{self.TAB}xor"),
            TOKEN_TYPES.OP_BIGGER:       "cgt",
            TOKEN_TYPES.OP_BIGGER_EQUAL: (f"clt\n{self.TAB}ldc.i4 1\n{self.TAB}xor"),
            TOKEN_TYPES.OP_EQUAL:        "ceq",
            TOKEN_TYPES.OP_NOT_EQUAL:    (f"ceq\n{self.TAB}ldc.i4 1\n{self.TAB}xor")
        }

        self.__CIL_OUT = {
            TOKEN_TYPES.OP_OUT_STR:   "call void [mscorlib]System.Console::Write(string)",
            TOKEN_TYPES.OP_OUT_BOOL:  "call void [mscorlib]System.Console::Write(bool)",
            TOKEN_TYPES.OP_OUT_INT:   "call void [mscorlib]System.Console::Write(int64)",
            TOKEN_TYPES.OP_OUT_FLOAT: "call void [mscorlib]System.Console::Write(float64)"
        }

    def locals_from_var_table (self) -> str:
        result    = ""
        variables = self.var_table.get_table_CIL(self.__PREFIX)
        for x in variables:
            result += ",\n" + self.TAB_locals
            result += CIL.__to_cil_var_type(SEMANTIC_TYPE_TO_VALUE_TYPE[x[1]]) + ' ' + x[0]      
        return result
    
    def __load(self, value, value_type: VALUE_TYPES | RPN_TYPES) -> str:
        to_return: str = ""
        match value_type:
            case VALUE_TYPES.INT:
                self.pseudo_stack.append(VALUE_TYPES.INT)
                to_return = f"ldc.i8 {value}"
            
            case VALUE_TYPES.FLOAT:
                self.pseudo_stack.append(VALUE_TYPES.FLOAT)
                to_return = f"ldc.r8 {value}"
            
            case VALUE_TYPES.BOOL:
                self.pseudo_stack.append(VALUE_TYPES.BOOL)
                to_return = f"ldc.i4 {1 if value == "true" else 0}"
            
            case VALUE_TYPES.STRING:
                self.pseudo_stack.append(VALUE_TYPES.STRING)
                to_return = f"ldstr \"{value}\""
            
            case RPN_TYPES.R_VAL:
                self.pseudo_stack.append(SEMANTIC_TYPE_TO_VALUE_TYPE[self.var_table.get(value)])
                to_return = f"ldloc {self.__PREFIX + value}"

            case RPN_TYPES.L_VAL:
                self.pseudo_stack.append(SEMANTIC_TYPE_TO_VALUE_TYPE[self.var_table.get(value)])
                to_return = f"ldloca {self.__PREFIX + value}"

            case _ : 
                print_console(f"Error -> TP Translation (Finishing): unable to process type {value_type} or value {value}",
                          CONSOLE_COLORS.ERROR)
        return to_return
    
    @staticmethod
    def __to_cil_type (inner_type: VALUE_TYPES) -> str:
        match inner_type:
            case VALUE_TYPES.INT:
                return "i8"
            case VALUE_TYPES.FLOAT:
                return "r8"
            case VALUE_TYPES.BOOL:
                return "i4"
            case _:
                print_console(f"Error -> TP Translation (Finishing): unable to process type inner type",
                    CONSOLE_COLORS.ERROR)
    
    @staticmethod
    def __to_cil_var_type (inner_type: VALUE_TYPES) -> str:
        match inner_type:
            case VALUE_TYPES.INT:
                return "int64"
            case VALUE_TYPES.FLOAT:
                return "float64"
            case VALUE_TYPES.BOOL:
                return "int32"
            case _:
                print_console(f"Error -> TP Translation (Finishing): unable to process type inner type",
                    CONSOLE_COLORS.ERROR)

    def __load_to_local (self): # TOKEN_TYPES.OP_ASSIGN        
        result: str = ""

        stack_result = self.pseudo_stack[-1]
        variable     = self.pseudo_stack[-2]

        # conv.type
        if variable == VALUE_TYPES.INT and stack_result == VALUE_TYPES.FLOAT:
            result += "conv.i8\n" + self.TAB
        elif variable == VALUE_TYPES.FLOAT and stack_result == VALUE_TYPES.INT:
            result += "conv.r8\n" + self.TAB

        return result + f"stind.{CIL.__to_cil_type(variable)}"    
    
    def __left_to (self, new_type: VALUE_TYPES) -> str: 
        result = ""
        
        right = self.pseudo_stack[-1]
        self.pseudo_stack[-2] = new_type

        result += "stloc _rax_" + CIL.__to_cil_type(right)    + '\n' + self.TAB
        result += "conv."       + CIL.__to_cil_type(new_type) + '\n' + self.TAB
        result += "ldloc _rax_" + CIL.__to_cil_type(right)    + '\n' + self.TAB
        return result
    
    def __right_to (self, new_type: VALUE_TYPES) -> str:
        self.pseudo_stack[-1] = new_type
        return "conv." + CIL.__to_cil_type(new_type) + '\n' + self.TAB    

    def __unary(self, operator: TOKEN_TYPES) -> str:
        return self.__CIL_MATH[operator]

    def __math(self, operator: TOKEN_TYPES) -> str:
        result = ""

        left  = self.pseudo_stack[-2]
        right = self.pseudo_stack[-1]
        if (operator in [TOKEN_TYPES.OP_DIVIDE, TOKEN_TYPES.OP_POWER]) or (left != right):
            if left != VALUE_TYPES.FLOAT:
                result += self.__left_to(VALUE_TYPES.FLOAT)

            if right != VALUE_TYPES.FLOAT:
                result += self.__right_to(VALUE_TYPES.FLOAT)

        result += self.__CIL_MATH[operator]
        self.pseudo_stack.pop()
        return result
    
    def __logic(self, operator: TOKEN_TYPES) -> str: 
        self.pseudo_stack.pop()
        return self.__CIL_MATH[operator]

    def __compare(self, operator: TOKEN_TYPES) -> str:
        result = ""
        
        left  = self.pseudo_stack[-2]
        right = self.pseudo_stack[-1]
        
        if left != right:  # can only be if one is float and other is int
            if left != VALUE_TYPES.FLOAT:
                result += self.__left_to(VALUE_TYPES.FLOAT)
            else: # right != VALUE_TYPES.FLOAT:
                result += self.__right_to(VALUE_TYPES.FLOAT)

        result += self.__CIL_MATH[operator]
        self.pseudo_stack.pop()
        self.pseudo_stack.pop()
        self.pseudo_stack.append(VALUE_TYPES.BOOL)
        return result

    def __out(self, operator: TOKEN_TYPES) -> str: 
        return self.__CIL_OUT[operator]
        
    def __jump(self, operator: TOKEN_TYPES, label: str) -> str:
        match operator:
            case TOKEN_TYPES.OP_JF:
                return "brfalse " + label
            case TOKEN_TYPES.OP_JT:
                return "brtrue " + label
            case TOKEN_TYPES.OP_JMP:
                return "br " + label            

    def __label(self, label: str) -> str:
        self.entry_index += 1
        next_entry = self.RPN_table[self.entry_index]

        if next_entry[1] in [TOKEN_TYPES.OP_JF, TOKEN_TYPES.OP_JT, TOKEN_TYPES.OP_JMP]:
            return self.__jump(next_entry[1], label) 

        return label + ':'

    def __input(self, input_type: TOKEN_TYPES) -> str:
        match input_type:
            case TOKEN_TYPES.OP_INPUT_INT:
                return f"call int64 [utils]Utils.Reader::ReadInt(string)" 
            case TOKEN_TYPES.OP_INPUT_FLOAT:
                return f"call float64 [utils]Utils.Reader::ReadFloat(string)"
            case TOKEN_TYPES.OP_INPUT_BOOL:
                return f"call bool [utils]Utils.Reader::ReadBool(string)"   
        

    def __process_entry(self, entry: tuple[str, RPN_TYPES | TOKEN_TYPES | VALUE_TYPES]) -> str:
        if (type(entry[1]) is VALUE_TYPES) or (entry[1] in [RPN_TYPES.R_VAL, RPN_TYPES.L_VAL]):
            return self.__load(entry[0], entry[1])
        
        if entry[1] in [TOKEN_TYPES.OP_PLUS,  TOKEN_TYPES.OP_MINUS, 
                        TOKEN_TYPES.OP_MULTI, TOKEN_TYPES.OP_DIVIDE, 
                        TOKEN_TYPES.OP_POWER]:
            return self.__math(entry[1])

        if entry[1] in [TOKEN_TYPES.OP_NOT, TOKEN_TYPES.OP_UMINUS]:
            return self.__unary(entry[1])
    
        if entry[1] in [TOKEN_TYPES.OP_AND, TOKEN_TYPES.OP_OR]:
            return self.__logic(entry[1])

        if entry[1] in [TOKEN_TYPES.OP_OUT_BOOL, TOKEN_TYPES.OP_OUT_FLOAT, TOKEN_TYPES.OP_OUT_INT, TOKEN_TYPES.OP_OUT_STR]:
            return self.__out(entry[1])
        
        if entry[1] in [TOKEN_TYPES.OP_BIGGER, TOKEN_TYPES.OP_BIGGER_EQUAL, 
                        TOKEN_TYPES.OP_LESS,   TOKEN_TYPES.OP_LESS_EQUAL,
                        TOKEN_TYPES.OP_EQUAL,  TOKEN_TYPES.OP_NOT_EQUAL]:
            return self.__compare(entry[1])

        if entry[1] in [TOKEN_TYPES.OP_INPUT_BOOL, TOKEN_TYPES.OP_INPUT_INT, TOKEN_TYPES.OP_INPUT_FLOAT]:
            return self.__input(entry[1])

        if entry[1] == RPN_TYPES.LABEL:
            return self.__label(entry[0])

        if entry[1] == TOKEN_TYPES.OP_ASSIGN:
                return self.__load_to_local()
        
        print_console(f"Error -> TP Translation (Inner): unknown option while processing tokens",
                      CONSOLE_COLORS.ERROR)
        exit(1)
        
    
    def cil_from_code_list (self) -> str:
        result: str = ""
        self.pseudo_stack.clear()
        self.entry_index = 0
        while self.entry_index < len(self.RPN_table):
            # print(entry)
            result += self.TAB
            result += self.__process_entry(self.RPN_table[self.entry_index])
            result += '\n'
            self.entry_index += 1
        self.pseudo_stack.clear()
        return result