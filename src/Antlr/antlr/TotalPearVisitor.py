# Generated from TotalPear.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .TotalPearParser import TotalPearParser
else:
    from TotalPearParser import TotalPearParser

# This class defines a complete generic visitor for a parse tree produced by TotalPearParser.

class TotalPearVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by TotalPearParser#program.
    def visitProgram(self, ctx:TotalPearParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#statementList.
    def visitStatementList(self, ctx:TotalPearParser.StatementListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#statementLine.
    def visitStatementLine(self, ctx:TotalPearParser.StatementLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#statementLocal.
    def visitStatementLocal(self, ctx:TotalPearParser.StatementLocalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#initDeclare.
    def visitInitDeclare(self, ctx:TotalPearParser.InitDeclareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#expression.
    def visitExpression(self, ctx:TotalPearParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#mathPolynomial.
    def visitMathPolynomial(self, ctx:TotalPearParser.MathPolynomialContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#mathMonomial.
    def visitMathMonomial(self, ctx:TotalPearParser.MathMonomialContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#mathPrimary1.
    def visitMathPrimary1(self, ctx:TotalPearParser.MathPrimary1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#mathPrimary2.
    def visitMathPrimary2(self, ctx:TotalPearParser.MathPrimary2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#mathPrimary3.
    def visitMathPrimary3(self, ctx:TotalPearParser.MathPrimary3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#logicalExpression.
    def visitLogicalExpression(self, ctx:TotalPearParser.LogicalExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#logical2.
    def visitLogical2(self, ctx:TotalPearParser.Logical2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#logical3.
    def visitLogical3(self, ctx:TotalPearParser.Logical3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#logical4.
    def visitLogical4(self, ctx:TotalPearParser.Logical4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#comparison.
    def visitComparison(self, ctx:TotalPearParser.ComparisonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#assign.
    def visitAssign(self, ctx:TotalPearParser.AssignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#assignStatement.
    def visitAssignStatement(self, ctx:TotalPearParser.AssignStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#print.
    def visitPrint(self, ctx:TotalPearParser.PrintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#printList.
    def visitPrintList(self, ctx:TotalPearParser.PrintListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#printable.
    def visitPrintable(self, ctx:TotalPearParser.PrintableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#inputStatement.
    def visitInputStatement(self, ctx:TotalPearParser.InputStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#cycleWhile.
    def visitCycleWhile(self, ctx:TotalPearParser.CycleWhileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#body.
    def visitBody(self, ctx:TotalPearParser.BodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#cycleFor.
    def visitCycleFor(self, ctx:TotalPearParser.CycleForContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#cycleDo.
    def visitCycleDo(self, ctx:TotalPearParser.CycleDoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#conditionalFlags.
    def visitConditionalFlags(self, ctx:TotalPearParser.ConditionalFlagsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#flagList.
    def visitFlagList(self, ctx:TotalPearParser.FlagListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#flagDeclare.
    def visitFlagDeclare(self, ctx:TotalPearParser.FlagDeclareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#flag.
    def visitFlag(self, ctx:TotalPearParser.FlagContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#flagBody.
    def visitFlagBody(self, ctx:TotalPearParser.FlagBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#conditionalIf.
    def visitConditionalIf(self, ctx:TotalPearParser.ConditionalIfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#elif.
    def visitElif(self, ctx:TotalPearParser.ElifContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#else.
    def visitElse(self, ctx:TotalPearParser.ElseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#conditionalSwitch.
    def visitConditionalSwitch(self, ctx:TotalPearParser.ConditionalSwitchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#case.
    def visitCase(self, ctx:TotalPearParser.CaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#default.
    def visitDefault(self, ctx:TotalPearParser.DefaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#inputType.
    def visitInputType(self, ctx:TotalPearParser.InputTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#bool.
    def visitBool(self, ctx:TotalPearParser.BoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#type.
    def visitType(self, ctx:TotalPearParser.TypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#uint.
    def visitUint(self, ctx:TotalPearParser.UintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TotalPearParser#ufloat.
    def visitUfloat(self, ctx:TotalPearParser.UfloatContext):
        return self.visitChildren(ctx)



del TotalPearParser