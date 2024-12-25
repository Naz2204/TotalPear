from Antlr.antlr.TotalPearParser import TotalPearParser
from Antlr.antlr.TotalPearVisitor import TotalPearVisitor
from Antlr.dijkstra_algo import Dijkstra
from Antlr.tables import Var_table, Label_generator
from Antlr.visitors.expression import ExpressionVisitor
from Antlr.consts import RPN_TYPES, TOKEN_TYPES
from Antlr.utils import jump_on_label, assign_label_position


class BranchVisitor(TotalPearVisitor):
    def __init__(self, dijkstra_worker: Dijkstra, var_table: Var_table,
                 label_gen: Label_generator,
                 expression_visitor: ExpressionVisitor,
                 visit_body_lambda) -> None:

        self.dijkstra_worker = dijkstra_worker
        self.var_table = var_table
        self.label_gen = label_gen
        self.expressionVisitor = expression_visitor

        self.visit_body_lambda = visit_body_lambda

        # ---

        self.end_label: str = ""


    def visitConditionalFlags(self, ctx: TotalPearParser.ConditionalFlagsContext):
        super().visitConditionalFlags(ctx)


    def visitFlagList(self, ctx: TotalPearParser.FlagListContext):
        super().visitFlagList(ctx)


    def visitFlagDeclare(self, ctx: TotalPearParser.FlagDeclareContext):
        super().visitFlagDeclare(ctx)


    def visitFlag(self, ctx: TotalPearParser.FlagContext):
        super().visitFlag(ctx)


    def visitFlagBody(self, ctx: TotalPearParser.FlagBodyContext):
        super().visitFlagBody(ctx)

    # ---

    def visitConditionalIf(self, ctx: TotalPearParser.ConditionalIfContext):
        self.expressionVisitor.visit(ctx.logicalExpression())

        # if - false - next jmp: jmp
        next_label = self.label_gen.get_label()
        jump_on_label(self.dijkstra_worker, next_label, TOKEN_TYPES.OP_JF)

        # body
        self.visit_body_lambda(ctx.body())

        # if - true - end jmp: jmp
        self.end_label = self.label_gen.get_label()
        jump_on_label(self.dijkstra_worker, self.end_label)

        # if - false - next jmp: make
        assign_label_position(self.dijkstra_worker, next_label)

        # else-elif
        else_exists = ctx.else_() is not None
        amount_else = ctx.getChildCount() - 3 - (1 if else_exists else 0)
        for i in range(3, amount_else + 3):
            self.visit(ctx.getChild(i))
        if else_exists:
            self.visit(ctx.else_())
        # end else-elif

        # if - true - end jmp: make
        assign_label_position(self.dijkstra_worker, self.end_label)


    def visitElif(self, ctx: TotalPearParser.ElifContext):
        self.expressionVisitor.visit(ctx.logicalExpression())

        # elif - false: jmp
        next_label = self.label_gen.get_label()
        jump_on_label(self.dijkstra_worker, next_label, TOKEN_TYPES.OP_JF)

        self.visit_body_lambda(ctx.body())

        # elif - true: jmp
        jump_on_label(self.dijkstra_worker, self.end_label)

        # elif - false: make
        assign_label_position(self.dijkstra_worker, next_label)

        jump_on_label(self.dijkstra_worker, self.end_label)


    def visitElse(self, ctx: TotalPearParser.ElseContext):
        self.visit_body_lambda(ctx.body())

    # ---

    def visitConditionalSwitch(self, ctx: TotalPearParser.ConditionalSwitchContext):
        super().visitConditionalSwitch(ctx)


    def visitCase(self, ctx: TotalPearParser.CaseContext):
        super().visitCase(ctx)


    def visitDefault(self, ctx: TotalPearParser.DefaultContext):
        super().visitDefault(ctx)