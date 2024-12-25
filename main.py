from antlr4 import *
import subprocess
from Antlr.antlr.TotalPearLexer import TotalPearLexer
from Antlr.antlr.TotalPearParser import TotalPearParser
from Antlr.visitors.program import ProgramVisitor
from Antlr.dijkstra_algo import Dijkstra
from Antlr.tables import Var_table, Label_generator


def main():
    with open("test.tp", "r") as file:
        reader = file.read()

    lexer  = TotalPearLexer(InputStream(reader))
    stream = CommonTokenStream(lexer)
    parser = TotalPearParser(stream)
    tree   = parser.program()

    if parser.getNumberOfSyntaxErrors() > 0:
        print("Syntax Error")
        exit(1)

    dijkstra  = Dijkstra()
    var_table = Var_table()
    label_gen = Label_generator()

    visitor = ProgramVisitor(dijkstra, var_table, label_gen)
    visitor.visit(tree)

    dijkstra.result_to("test", var_table)

    subprocess.run("ilasm test.il", shell=True)
    subprocess.run("clear", shell=True)
    subprocess.run("test.exe", shell=True)

if __name__ == "__main__":
    main()