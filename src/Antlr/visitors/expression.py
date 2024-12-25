from Antlr.antlr.TotalPearParser import TotalPearParser
from Antlr.antlr.TotalPearVisitor import TotalPearVisitor
from Antlr.consts import VALUE_TYPES, TOKEN_TYPES, RPN_TYPES
from Antlr.dijkstra_algo import Dijkstra
from Antlr.tables import Var_table
from Antlr.utils import check_assign_type, expression_type, expression_type_unary, check_type_expression_is_math

class ExpressionVisitor(TotalPearVisitor):
    def __init__(self, dijkstra_worker: Dijkstra, var_table: Var_table) -> None:
        self.dijkstra_worker = dijkstra_worker
        self.var_table       = var_table


    def visitExpression(self, ctx: TotalPearParser.ExpressionContext) -> VALUE_TYPES:

        result: bool | str  = check_type_expression_is_math(ctx.getText(), var_table=self.var_table)
        if type(result) is str:
            print(result) # error
            exit(1)

        if result:
            result_expression: VALUE_TYPES | str = self.visitMathPolynomial(ctx.getChild(0))
        else:
            result_expression: VALUE_TYPES | str = self.visitLogicalExpression(ctx.getChild(0))

        if type(result_expression) is str:
            print(result_expression) # error
            exit(1)

        return result_expression


    def visitMathPolynomial(self, ctx: TotalPearParser.MathPolynomialContext) -> VALUE_TYPES | str:
        left_type: VALUE_TYPES | str = self.visit(ctx.getChild(0))

        for i in range(2, ctx.getChildCount(), 2): # + 1 to make i <= ctx.getChildCount()
            self.dijkstra_worker.push(TOKEN_TYPES(ctx.getChild(i - 1).getText()))

            right_type: VALUE_TYPES | str = self.visit(ctx.getChild(i))
            left_type = expression_type(left_type, right_type, TOKEN_TYPES(ctx.getChild(i - 1).getText()))

        return left_type



    def visitMathMonomial(self, ctx: TotalPearParser.MathMonomialContext) -> VALUE_TYPES | str:
        left_type: VALUE_TYPES | str = self.visit(ctx.getChild(0))

        #TODO перевірити ділення на нуль

        for i in range(2, ctx.getChildCount(), 2): # + 1 to make i <= ctx.getChildCount()
            self.dijkstra_worker.push(TOKEN_TYPES(ctx.getChild(i - 1).getText()))

            right_type: VALUE_TYPES | str = self.visit(ctx.getChild(i))
            left_type = expression_type(left_type, right_type, TOKEN_TYPES(ctx.getChild(i - 1).getText()))

        return left_type


    def visitMathPrimary1(self, ctx: TotalPearParser.MathPrimary1Context) -> VALUE_TYPES | str:
        has_minus = (ctx.getChildCount() - 1) % 2 != 0
        if has_minus:
            self.dijkstra_worker.push(TOKEN_TYPES.OP_UMINUS)

        expression_type_var: VALUE_TYPES | str = self.visit(ctx.mathPrimary2())
        if has_minus:
            expression_type_var = expression_type_unary(TOKEN_TYPES.OP_UMINUS, expression_type_var)

        return expression_type_var


    def visitMathPrimary2(self, ctx: TotalPearParser.MathPrimary2Context) -> VALUE_TYPES | str:
        if ctx.getChildCount() == 1:
            return self.visit(ctx.mathPrimary3())

        left_type = self.visit(ctx.mathPrimary3())
        self.dijkstra_worker.push(TOKEN_TYPES.OP_POWER)
        right_type = self.visit(ctx.mathPrimary1())
        return expression_type(left_type, right_type, TOKEN_TYPES.OP_POWER)


    def visitMathPrimary3(self, ctx: TotalPearParser.MathPrimary3Context) -> VALUE_TYPES | str:
        is_brackets: bool = ctx.getChildCount() == 3
        if is_brackets:
            self.dijkstra_worker.push(TOKEN_TYPES.BRACKET_L)
            expression_type_var = self.visit(ctx.mathPolynomial())
            self.dijkstra_worker.push(TOKEN_TYPES.BRACKET_R)
            return expression_type_var

        # ---

        is_ident = ctx.IDENTIFIER() is not None
        if is_ident:
            ident = ctx.IDENTIFIER().getText()
            expression_type_var = self.var_table.get_type(ident)
            if expression_type_var is None:
                print("Unknown identifier")
                exit(1)
            elif expression_type_var not in [VALUE_TYPES.INT, VALUE_TYPES.FLOAT]:
                return "Logical type variable in arithmetic expression"

            self.dijkstra_worker.push(RPN_TYPES.R_VAL, ident)
            return expression_type_var

        # ---

        return self.visit(ctx.getChild(0))


    def visitLogicalExpression(self, ctx: TotalPearParser.LogicalExpressionContext) -> VALUE_TYPES | str:
        left_type: VALUE_TYPES | str = self.visit(ctx.getChild(0))

        for i in range(2, ctx.getChildCount(), 2): # + 1 to make i <= ctx.getChildCount()
            self.dijkstra_worker.push(TOKEN_TYPES(ctx.getChild(i - 1).getText()))

            right_type: VALUE_TYPES | str = self.visit(ctx.getChild(i))
            left_type = expression_type(left_type, right_type, TOKEN_TYPES(ctx.getChild(i - 1).getText()))

        return left_type


    def visitLogical2(self, ctx: TotalPearParser.Logical2Context) -> VALUE_TYPES | str:
        left_type: VALUE_TYPES | str = self.visit(ctx.getChild(0))

        for i in range(2, ctx.getChildCount(), 2): # + 1 to make i <= ctx.getChildCount()
            self.dijkstra_worker.push(TOKEN_TYPES(ctx.getChild(i - 1).getText()))

            right_type: VALUE_TYPES | str = self.visit(ctx.getChild(i))
            left_type = expression_type(left_type, right_type, TOKEN_TYPES(ctx.getChild(i - 1).getText()))

        return left_type


    def visitLogical3(self, ctx: TotalPearParser.Logical3Context) -> VALUE_TYPES | str:
        has_not = (ctx.getChildCount() - 1) % 2 != 0
        if has_not:
            self.dijkstra_worker.push(TOKEN_TYPES.OP_NOT)

        expression_type_var: VALUE_TYPES | str = self.visit(ctx.logical4())
        if has_not:
            expression_type_var = expression_type_unary(TOKEN_TYPES.OP_NOT, expression_type_var)

        return expression_type_var


    def visitLogical4(self, ctx: TotalPearParser.Logical4Context) -> VALUE_TYPES | str:
        is_brackets: bool = ctx.getChildCount() == 3
        if is_brackets:
            self.dijkstra_worker.push(TOKEN_TYPES.BRACKET_L)
            expression_type_var = self.visit(ctx.logicalExpression())
            self.dijkstra_worker.push(TOKEN_TYPES.BRACKET_R)
            return expression_type_var

        # ---

        is_ident = ctx.IDENTIFIER() is not None
        if is_ident:
            ident = ctx.IDENTIFIER().getText()
            expression_type_var = self.var_table.get_type(ident)
            if expression_type_var is None:
                print("Unknown identifier")
                exit(1)
            elif expression_type_var is not VALUE_TYPES.BOOL:
                return "Arithmetic type variable in math expression"

            self.dijkstra_worker.push(RPN_TYPES.R_VAL, ident)
            return expression_type_var

        # ---

        return self.visit(ctx.getChild(0))


    def visitComparison(self, ctx: TotalPearParser.ComparisonContext) -> VALUE_TYPES | str:
        left_type: VALUE_TYPES | str = self.visit(ctx.getChild(1))

        for i in range(3, ctx.getChildCount(), 2): # + 1 to make i <= ctx.getChildCount()
            self.dijkstra_worker.push(TOKEN_TYPES(ctx.getChild(i - 1).getText()))

            right_type: VALUE_TYPES | str = self.visit(ctx.getChild(i))
            left_type = expression_type(left_type, right_type, TOKEN_TYPES(ctx.getChild(i - 1).getText()))

        return left_type

    # ---

    def visitAssignStatement(self, ctx: TotalPearParser.AssignStatementContext):
        name: str = ctx.IDENTIFIER().getText()

        var_type: VALUE_TYPES | None = self.var_table.get_type(name)
        if var_type is None:
            print("Undeclared identifier")
            exit(1)

        self.dijkstra_worker.push(RPN_TYPES.L_VAL, name)

        expression_type_var: VALUE_TYPES = self.visit(ctx.getChild(2)) # expression | input
        if not check_assign_type(var_type, expression_type_var):
            print("Invalid init type")
            exit(1)

        self.dijkstra_worker.push(TOKEN_TYPES.OP_ASSIGN)
        self.dijkstra_worker.push(TOKEN_TYPES.END_STATEMENT)


    def visitInitDeclare(self, ctx: TotalPearParser.InitDeclareContext):
        var_type: VALUE_TYPES = self.visit(ctx.type_())
        name: str = ctx.IDENTIFIER().getText()

        is_unique = self.var_table.add(var_type, name)
        if not is_unique:
            print("Identifier already exists")
            exit(1)

        if ctx.getChildCount() == 3:
            return

        # ---
        self.dijkstra_worker.push(RPN_TYPES.L_VAL, name)

        expression_type_var: VALUE_TYPES = self.visit(ctx.getChild(3)) # expression | input
        if not check_assign_type(var_type, expression_type_var):
            print("Invalid init type")
            exit(1)

        self.dijkstra_worker.push(TOKEN_TYPES.OP_ASSIGN)
        self.dijkstra_worker.push(TOKEN_TYPES.END_STATEMENT)


    def visitPrintable(self, ctx: TotalPearParser.PrintableContext):
        is_string: bool = ctx.STRING() is not None
        if is_string:
            self.dijkstra_worker.push(VALUE_TYPES.STRING, ctx.STRING().getText())
            self.dijkstra_worker.push(TOKEN_TYPES.OP_OUT_STR)
            self.dijkstra_worker.push(TOKEN_TYPES.END_STATEMENT)
            return

        semantic_type: VALUE_TYPES = self.visit(ctx.getChild(0))
        match semantic_type:
            case VALUE_TYPES.INT:
                self.dijkstra_worker.push(TOKEN_TYPES.OP_OUT_INT)
            case VALUE_TYPES.FLOAT:
                self.dijkstra_worker.push(TOKEN_TYPES.OP_OUT_FLOAT)
            case VALUE_TYPES.BOOL:
                self.dijkstra_worker.push(TOKEN_TYPES.OP_OUT_BOOL)
        self.dijkstra_worker.push(TOKEN_TYPES.END_STATEMENT)


    def visitInputStatement(self, ctx: TotalPearParser.InputStatementContext) -> VALUE_TYPES:
        input_type: tuple[VALUE_TYPES, TOKEN_TYPES] = self.visit(ctx.inputType())
        string = ctx.STRING()

        string = "\"\"" if string is None else string.getText()
        self.dijkstra_worker.push(VALUE_TYPES.STRING, string)
        self.dijkstra_worker.push(input_type[1])

        return input_type[0]

    # ---

    def visitUfloat(self, ctx: TotalPearParser.UfloatContext) -> VALUE_TYPES:
        self.dijkstra_worker.push(VALUE_TYPES.FLOAT, ctx.UNSIGNED_FLOAT().getText())
        return VALUE_TYPES.FLOAT


    def visitUint(self, ctx: TotalPearParser.UintContext) -> VALUE_TYPES:
        self.dijkstra_worker.push(VALUE_TYPES.INT, ctx.UNSIGNED_INTEGER().getText())
        return VALUE_TYPES.INT


    def visitType(self, ctx: TotalPearParser.TypeContext) -> VALUE_TYPES:
        match ctx.TYPE().getText():
            case 'int':
                return VALUE_TYPES.INT
            case 'float':
                return VALUE_TYPES.FLOAT
            case 'bool':
                return VALUE_TYPES.BOOL


    def visitBool(self, ctx: TotalPearParser.BoolContext) -> VALUE_TYPES:
        self.dijkstra_worker.push(VALUE_TYPES.BOOL, ctx.BOOL().getText())
        return VALUE_TYPES.BOOL


    def visitInputType(self, ctx: TotalPearParser.InputTypeContext) -> tuple[VALUE_TYPES, TOKEN_TYPES]:
        match ctx.INPUT_TYPE().getText():
            case 'inputInt':
                return VALUE_TYPES.INT, TOKEN_TYPES.OP_INPUT_INT
            case 'inputFloat':
                return VALUE_TYPES.FLOAT, TOKEN_TYPES.OP_INPUT_FLOAT
            case 'inputBool':
                return VALUE_TYPES.BOOL, TOKEN_TYPES.OP_INPUT_BOOL

