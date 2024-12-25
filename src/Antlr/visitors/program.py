from Antlr.antlr.TotalPearParser import TotalPearParser
from Antlr.antlr.TotalPearVisitor import TotalPearVisitor
from Antlr.dijkstra_algo import Dijkstra
from Antlr.visitors.statement import StatementVisitor
from Antlr.tables import Var_table, Label_generator

class ProgramVisitor(TotalPearVisitor):
    def __init__(self, dijkstra_worker: Dijkstra, var_table: Var_table, label_gen: Label_generator) -> None:
        self.statementVisitor  = StatementVisitor(dijkstra_worker, var_table, label_gen)

    def visitProgram(self, ctx:TotalPearParser.ProgramContext):
        amount_of_nodes: int = ctx.getChildCount()
        for i in range(amount_of_nodes):
            self.statementVisitor.visit(ctx.getChild(i))