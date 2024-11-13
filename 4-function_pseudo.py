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

# FourFunctionCalculator Class
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
            if self.expression_tree.expressions and isinstance(self.expression_tree.expressions[-1], (Parenthesis, Root)):
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

    def input_function(self,function):
        self.save_state()
        new_compound = Compound([])
        if self.expression_tree.expressions and isinstance(self.expression_tree.expressions[-1], (Parenthesis, Function)):
            self.expression_tree.expressions[-1].expression.expressions.append(new_compound)
        else:
            self.expression_tree.expressions.append(Function(new_compound,function))
        self.stack.append((self.state, self.state_data, self.expression_tree))
        self.expression_tree = new_compound
        self.state_data = FunctionInputState(current_value="")
        self.state = CalculatorState.FUNCTION_INPUT
        self.debug_state(str(function) + " Input")

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

    # Define the square root function
    def sqrt_func(x: str) -> str:        
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
print(evaluate_expression(calc.expression_tree))  # Should print "3+(2*(4+1))+(5-(3+2))"

# Root example: 9 + sqrt(4)
calc.input_clear()
calc.input_digit("9")
calc.input_operator("+")
calc.input_function(FourFunctionCalculator.sqrt_func)
calc.input_digit("4")
calc.input_parenthesis_close()  # Close the root parenthesis

calc.input_equals()
print(evaluate_expression(calc.expression_tree))  # Should print "9+sqrt(4)"
