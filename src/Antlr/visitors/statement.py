from Antlr.antlr.TotalPearParser import TotalPearParser
from Antlr.antlr.TotalPearVisitor import TotalPearVisitor
from Antlr.consts import TOKEN_TYPES, VALUE_TYPES
from Antlr.dijkstra_algo          import Dijkstra
from Antlr.tables                 import Var_table, Label_generator
from Antlr.visitors.expression    import ExpressionVisitor
from Antlr.visitors.cycle         import CycleVisitor
from Antlr.visitors.branch        import BranchVisitor


class StatementVisitor(TotalPearVisitor):
    def __init__(self, dijkstra_worker: Dijkstra, var_table: Var_table, label_gen: Label_generator) -> None:
        self.dijkstra_worker   = dijkstra_worker
        self.expressionVisitor = ExpressionVisitor(dijkstra_worker, var_table)

        visit_body_lambda = lambda ctx=TotalPearParser.ConditionalIfContext, obj=self: obj.visitBody(ctx)

        self.cycleVisitor      = CycleVisitor(dijkstra_worker, label_gen, self.expressionVisitor, visit_body_lambda)
        self.branchVisitor     = BranchVisitor(dijkstra_worker, var_table, label_gen, self.expressionVisitor, visit_body_lambda)
        self.var_table         = var_table


    # def visitStatementLine(self, ctx: TotalPearParser.StatementLineContext):
    #     super().visitStatementLine(ctx)


    # def visitStatementLocal(self, ctx: TotalPearParser.StatementLocalContext):
    #     super().visitStatementLocal(ctx)


    def visitBody(self, ctx: TotalPearParser.BodyContext):
        self.dijkstra_worker.push(TOKEN_TYPES.CURVE_L)
        local_list = ctx.statementLocal()
        for i in range(len(local_list)):
            self.visit(local_list[i])
        self.dijkstra_worker.push(TOKEN_TYPES.CURVE_R)


    # point - expression
    def visitInitDeclare(self, ctx: TotalPearParser.InitDeclareContext):
        self.expressionVisitor.visitInitDeclare(ctx)


    # point - expression
    def visitExpression(self, ctx: TotalPearParser.ExpressionContext) -> VALUE_TYPES:
        return self.expressionVisitor.visit(ctx)


    # possible remove
    # def visitAssign(self, ctx: TotalPearParser.AssignContext):
    #     super().visitAssign(ctx)


    # point - expression
    def visitAssignStatement(self, ctx: TotalPearParser.AssignStatementContext):
        self.expressionVisitor.visit(ctx)


    # possible remove
    # def visitPrint(self, ctx: TotalPearParser.PrintContext):
    #     super().visitPrint(ctx)

    # possible remove
    # def visitPrintList(self, ctx: TotalPearParser.PrintListContext):
    #     super().visitPrintList(ctx)


    # point - expression
    def visitPrintable(self, ctx: TotalPearParser.PrintableContext):
        self.expressionVisitor.visit(ctx)


    # point - expression
    def visitInputStatement(self, ctx: TotalPearParser.InputStatementContext) -> VALUE_TYPES:
        return self.expressionVisitor.visit(ctx)


    # point - cycle
    def visitCycleWhile(self, ctx: TotalPearParser.CycleWhileContext):
        self.cycleVisitor.visit(ctx)


    # point - cycle
    def visitCycleFor(self, ctx: TotalPearParser.CycleForContext):
        self.cycleVisitor.visit(ctx)


    # point - cycle
    def visitCycleDo(self, ctx: TotalPearParser.CycleDoContext):
        self.cycleVisitor.visit(ctx)


    # point - branch
    def visitConditionalFlags(self, ctx: TotalPearParser.ConditionalFlagsContext):
        self.branchVisitor.visit(ctx)


    # point - branch
    def visitConditionalIf(self, ctx: TotalPearParser.ConditionalIfContext):
        self.branchVisitor.visit(ctx)


    # point - branch
    def visitConditionalSwitch(self, ctx: TotalPearParser.ConditionalSwitchContext):
        self.branchVisitor.visit(ctx)
