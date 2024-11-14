from enum import Enum
from dataclasses import dataclass
from typing import List, Callable

# Expression Tree Data Structure
@dataclass
class Expression:
    pass

@dataclass
class Number(Expression):
    value: str

@dataclass
class Operator(Expression):
    operator: str

@dataclass
class Parenthesis(Expression):
    expression: 'Expression'

@dataclass
class Function(Expression):
    expression: 'Expression'
    function: Callable[[str], str]

@dataclass
class Compound(Expression):
    expressions: List[Expression]

# Catamorphism to Traverse the Expression Tree
def evaluate_expression(expr: Expression) -> str:
    if isinstance(expr, Number):
        return expr.value
    elif isinstance(expr, Operator):
        return expr.operator
    elif isinstance(expr, Parenthesis):
        return f"({evaluate_expression(expr.expression)})"
    elif isinstance(expr, Function):
        return expr.function(evaluate_expression(expr.expression))
    elif isinstance(expr, Compound):
        return "".join(evaluate_expression(e) for e in expr.expressions)
    else:
        raise ValueError("Unknown Expression Type")

# Calculator States
class CalculatorState(Enum):
    START = 0
    ENTERING_NUMBER = 1
    OPERATOR_INPUT = 2
    RESULT = 3
    ERROR = 4
    PARENTHESIS_OPEN = 5
    FUNCTION_INPUT = 6

@dataclass
class StartState:
    pass

@dataclass
class EnteringNumberState:
    current_value: str

@dataclass
class OperatorInputState:
    previous_value: str
    operator: str
    current_value: str

@dataclass
class ResultState:
    result: str

@dataclass
class ErrorState:
    error_message: str

@dataclass
class ParenthesisOpenState:
    inner_expression: str

@dataclass
class FunctionInputState:
    current_value: str

class FourFunctionCalculator:
    def __init__(self):
        self.state = CalculatorState.START
        self.state_data = StartState()
        self.expression_tree = Compound([])
        self.history = []
        self.stack = []

    def input_digit(self, digit: str):
        self.save_state()
        number = Number(value=digit)
        if isinstance(self.state_data, ParenthesisOpenState) or isinstance(self.state_data, FunctionInputState):
            if self.expression_tree.expressions and isinstance(self.expression_tree.expressions[-1], (Parenthesis, Function)):
                self.expression_tree.expressions[-1].expression.expressions.append(number)
            else:
                self.expression_tree.expressions.append(number)
        else:
            self.expression_tree.expressions.append(number)
        self.state_data = EnteringNumberState(current_value=digit)
        self.state = CalculatorState.ENTERING_NUMBER
        self.debug_state("Digit Input")

    def input_operator(self, operator: str):
        self.save_state()
        operator_expr = Operator(operator=operator)
        if self.state not in {CalculatorState.PARENTHESIS_OPEN, CalculatorState.FUNCTION_INPUT}:
            self.expression_tree.expressions.append(operator_expr)
        self.state_data = OperatorInputState(
            previous_value=self.state_data.current_value if isinstance(self.state_data, EnteringNumberState) else "",
            operator=operator,
            current_value=""
        )
        self.state = CalculatorState.OPERATOR_INPUT
        self.debug_state("Operator Input")

    def input_equals(self):
        self.save_state()
        self.state = CalculatorState.RESULT
        result_expression = evaluate_expression(self.expression_tree)
        self.state_data = ResultState(result=result_expression)
        self.debug_state("Equals Input")

    def input_clear(self):
        self.state = CalculatorState.START
        self.state_data = StartState()
        self.expression_tree = Compound([])
        self.history = []
        self.stack = []
        self.debug_state("Clear Input")

    def input_parenthesis_open(self):
        self.save_state()
        new_compound = Compound([])
        if self.expression_tree.expressions and isinstance(self.expression_tree.expressions[-1], (Parenthesis, Function)):
            self.expression_tree.expressions[-1].expression.expressions.append(new_compound)
        else:
            self.expression_tree.expressions.append(Parenthesis(new_compound))
        self.stack.append((self.state, self.state_data, self.expression_tree))
        self.expression_tree = new_compound
        self.state_data = ParenthesisOpenState(inner_expression="")
        self.state = CalculatorState.PARENTHESIS_OPEN
        self.debug_state("Parenthesis Open")

    def input_parenthesis_close(self):
        self.save_state()
        if self.stack:
            previous_state, previous_state_data, previous_expression_tree = self.stack.pop()
            self.expression_tree = previous_expression_tree
            self.state = previous_state
            self.state_data = previous_state_data
        self.debug_state("Parenthesis Close")

    def input_function(self, function):
        self.save_state()
        new_compound = Compound([])
        if self.expression_tree.expressions and isinstance(self.expression_tree.expressions[-1], (Parenthesis, Function)):
            self.expression_tree.expressions[-1].expression.expressions.append(new_compound)
        else:
            self.expression_tree.expressions.append(Function(new_compound, function))
        self.stack.append((self.state, self.state_data, self.expression_tree))
        self.expression_tree = new_compound
        self.state_data = FunctionInputState(current_value="")
        self.state = CalculatorState.FUNCTION_INPUT
        self.debug_state(f"{function.__name__} Input")

    def save_state(self):
        self.history.append((
            self.state,
            self.state_data,
            self.expression_tree
        ))

    def undo(self):
        if self.history:
            self.state, self.state_data, self.expression_tree = self.history.pop()

    def debug_state(self, action: str):
        print(f"Action: {action}")
        print(f"State: {self.state}")
        print(f"State Data: {self.state_data}")
        print(f"Expression Tree: {evaluate_expression(self.expression_tree)}")
        print("==============")

    def parse_expression(self, expression: str) -> Expression:
        tokens = self.tokenize(expression)
        return self.parse_tokens(tokens)

    def tokenize(self, expression: str) -> List[str]:
        import re
        token_pattern = re.compile(r'(\d+|sqrt|[+*/()-])')
        tokens = token_pattern.findall(expression)
        return tokens

    def parse_tokens(self, tokens: List[str]) -> Expression:
        def parse_inner(tokens, index):
            exprs = []
            while index < len(tokens):
                token = tokens[index]
                if token.isdigit():
                    exprs.append(Number(token))
                    index += 1
                elif token == 'sqrt':
                    sub_expr, index = parse_function(tokens, index)
                    exprs.append(sub_expr)
                elif token in '+-*/':
                    exprs.append(Operator(token))
                    index += 1
                elif token == '(':
                    sub_expr, index = parse_inner(tokens, index + 1)
                    exprs.append(Parenthesis(sub_expr))
                elif token == ')':
                    return Compound(exprs), index + 1
                else:
                    raise ValueError(f"Unknown token: {token}")
            return Compound(exprs), index

        def parse_function(tokens, index):
            func_name = tokens[index]
            index += 1
            if tokens[index] != '(':
                raise ValueError("Expected '(' after function name")
            sub_expr, index = parse_inner(tokens, index + 1)
            if func_name == 'sqrt':
                func = self.sqrt_func
            else:
                raise ValueError(f"Unknown function: {func_name}")
            return Function(expression=sub_expr, function=func), index

        expr_tree, _ = parse_inner(tokens, 0)
        return expr_tree

    def sqrt_func(self, x: str) -> str:
        return f"sqrt({x})"

# Running the examples with the updated class and steps.
calc = FourFunctionCalculator()

# Serial parentheses example: 3 + (2 * (4 + 1)) + (5 - (3 + 2))
calc.input_digit("3")
calc.input_operator("+")
calc.input_parenthesis_open()
calc.input_digit("2")
calc.input_operator("*")
calc.input_parenthesis_open()
calc.input_digit("4")
calc.input_operator("+")
calc.input_digit("1")
calc.input_parenthesis_close()
calc.input_parenthesis_close()

calc.input_operator("+")

calc.input_parenthesis_open()
calc.input_digit("5")
calc.input_operator("-")
calc.input_parenthesis_open()
calc.input_digit("3")
calc.input_operator("+")
calc.input_digit("2")
calc.input_parenthesis_close()
calc.input_parenthesis_close()

calc.input_equals()
expression_string = evaluate_expression(calc.expression_tree)
print(expression_string)  # Should print "3+(2*(4+1))+(5-(3+2))"
parsed_expression = calc.parse_expression(expression_string)
out1 = evaluate_expression(parsed_expression)
print(out1)
print(f"{parsed_expression}")

# Root example: 9 + sqrt(4)
calc.input_clear()
calc.input_digit("9")
calc.input_digit("9")
calc.input_operator("+")
calc.input_function(calc.sqrt_func)
calc.input_digit("4")
calc.input_parenthesis_close()  # Close the root parenthesis

calc.input_equals()
out2 = evaluate_expression(calc.expression_tree)
print(out2)  # Should print "9+sqrt(4)"
parsed_tree = calc.parse_expression(out2)
out3 = evaluate_expression(parsed_tree)
print(out3) # Should print "9+sqrt(4)"
print(f"{parsed_tree}")