from Antlr.antlr.TotalPearParser import TotalPearParser
from Antlr.antlr.TotalPearVisitor import TotalPearVisitor
from Antlr.dijkstra_algo import Dijkstra
from Antlr.tables import Label_generator
from Antlr.visitors.expression import ExpressionVisitor
from Antlr.utils import jump_on_label, assign_label_position
from Antlr.consts import TOKEN_TYPES

class CycleVisitor(TotalPearVisitor):
    def __init__(self, dijkstra_worker: Dijkstra,
                 label_gen: Label_generator,
                 expression_visitor: ExpressionVisitor,
                 visit_body_lambda) -> None:

        self.dijkstra_worker = dijkstra_worker
        self.label_gen = label_gen
        self.expressionVisitor = expression_visitor

        self.visit_body_lambda = visit_body_lambda


    def visitCycleWhile(self, ctx: TotalPearParser.CycleWhileContext):
        check_label = self.label_gen.get_label()
        assign_label_position(self.dijkstra_worker, check_label)

        self.expressionVisitor.visit(ctx.logicalExpression())

        end_label = self.label_gen.get_label()
        jump_on_label(self.dijkstra_worker, end_label, TOKEN_TYPES.OP_JF)

        self.visit_body_lambda(ctx.body())

        jump_on_label(self.dijkstra_worker, check_label)
        assign_label_position(self.dijkstra_worker, end_label)

    def visitCycleFor(self, ctx: TotalPearParser.CycleForContext):
        super().visitCycleFor(ctx)
        
        self.expressionVisitor.visit(ctx.assignStatement()[0])
        
        # check label
        check_label = self.label_gen.get_label()
        assign_label_position(self.dijkstra_worker, check_label)
        
        # check
        self.expressionVisitor.visit(ctx.logicalExpression())
        self.dijkstra_worker.push(TOKEN_TYPES.END_STATEMENT)

        # label: check - false (jmp to the end)
        end_label = self.label_gen.get_label()
        jump_on_label(self.dijkstra_worker, end_label, TOKEN_TYPES.OP_JF)

        # label: check - true (jmp to body)
        body_label = self.label_gen.get_label()
        jump_on_label(self.dijkstra_worker, body_label)
        
        # label: step
        step_label = self.label_gen.get_label()
        assign_label_position(self.dijkstra_worker, step_label)

        # step
        self.expressionVisitor.visit(ctx.assignStatement()[1])

        # lable: jmp on check
        jump_on_label(self.dijkstra_worker, check_label)

        # body
        assign_label_position(self.dijkstra_worker, body_label)
        self.visit_body_lambda(ctx.body())

        # label: jmp to step
        jump_on_label(self.dijkstra_worker, step_label)

        # label: end label
        assign_label_position(self.dijkstra_worker, end_label)


    def visitCycleDo(self, ctx: TotalPearParser.CycleDoContext):
        start_label = self.label_gen.get_label()
        assign_label_position(self.dijkstra_worker, start_label)
        
        self.visit_body_lambda(ctx.body())
        
        self.expressionVisitor.visit(ctx.logicalExpression())
        jump_on_label(self.dijkstra_worker, start_label, TOKEN_TYPES.OP_JT)

