# ================================================
# Calculator Domain using a state machine
# ================================================
from typing import Optional, Tuple, Union, List, Callable
from enum import Enum
from dataclasses import dataclass, field

# Type aliases for better readability
Number = float
DigitAccumulator = str

class CalculatorState(Enum):
    """
    Enumeration for the different states of the calculator.
    """
    # Common states
    ERROR = 0
    # Basic number entry states
    ZERO = 1
    ACCUMULATOR = 2
    COMPUTED = 3
    # Expression entry states    
    START = 4
    ENTERING_NUMBER = 5
    OPERATOR_INPUT = 6
    RESULT = 7
    PARENTHESIS_OPEN = 8
    ROOT_INPUT = 9

class CalculatorInput(Enum):
    """
    Represents various inputs for the calculator.
    """
    ZERO = "ZERO"
    DIGIT = lambda digit: ('DIGIT', digit)
    DECIMALSEPARATOR = "DECIMALSEPARATOR"
    MATHOP = lambda op: ('MATHOP', op)
    EQUALS = "EQUALS"
    CLEAR = "CLEAR"
    CLEARENTRY = "CLEARENTRY"
    BACK = "BACK"
    UNDO = "UNDO"
    REDO = "REDO"
    PARENOPEN = "PARENOPEN"
    PARENCLOSE = "PARENCLOSE"
    RETURN = "RETURN"
    FUNCTION = lambda func: ('FUNCTION', func)
    MEMORYSTORE = "MEMORYSTORE"
    MEMORYCLEAR = "MEMORYCLEAR"
    MEMORYRECALL = "MEMORYRECALL"
    
    
    def __call__(self, *args):
        if callable(self.value):
            return self.value(*args)
        raise TypeError(f"{self.name} is not callable")
    
class NonZeroDigit(Enum):
    """
    Enumeration for non-zero digits.
    ONE,TWO,THREE,FOUR,FIVE,SIX,SEVEN,EIGHT,NINE = range(1,10)
    """    
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    
class CalculatorMathOp(Enum):
    """
    Enumeration for calculator mathematical operations.
    """
    ADD = 1
    SUBTRACT = 2
    MULTIPLY = 3
    DIVIDE = 4
    INVERSE = 5
    PERCENT = 6
    ROOT = 7
    CHANGESIGN = 8
    MEMORYADD = 9
    MEMORYSUBTRACT = 10
    
class MathFunction(Enum):
    """
    Enumeration for mathematical functions.
    """
    SQRT = 1
    POWER = 2
    # 

# Type alias for a tuple representing a pending operation and its associated number
PendingOp = Tuple[CalculatorMathOp, Number]

# Expression Tree Data Structure
'''
Expression: This is the base class for all types of expressions. It's defined as
an empty class (a placeholder) from which other expression types inherit.
'''
@dataclass
class Expression:
    pass
'''
Value:
--Represents a numerical value in the expression.
--Inherits from Expression.
--Contains a single field value which is a string representation of the number.
'''
@dataclass
class Value(Expression):
    value: str
    result: bool = field(default=False)
'''
Operator:
--Represents an operator (e.g., +, -, *, /) in the expression.
--Inherits from Expression.
--Contains a single field operator which is a string representing the operator.
'''
@dataclass
class Operator(Expression):
    operator: str
'''
Parenthesis:
--Represents an expression enclosed in parentheses.
--Inherits from Expression.
--Contains a single field expression which is another Expression type,
  indicating the expression within the parentheses.
'''
@dataclass
class Parenthesis(Expression):
    expression: 'Expression'
'''
Function:
--Represents a function application to an argument.
--Inherits from Expression.
--This field holds a callable function that takes a string representation of an
  expression and returns a string. This allows you to define any mathematical
  function (e.g., square root, sine, cosine) and apply it to the expression.
'''
@dataclass
class Function(Expression):
    expression: 'Expression'
    function: Callable[[str], str]
'''
Compound:
--Represents a compound expression composed of multiple sub-expressions.
--Inherits from Expression.
--Contains a single field expressions which is a list of Expression objects.
'''
@dataclass
class Compound(Expression):
    expressions: List[Expression] = field(default_factory=list)
    
@dataclass
class Variable(Expression):
    name: str
    
@dataclass
class Exponentiation(Expression):
    base: Expression
    exponent: Expression

@dataclass
class Fraction(Expression):
    numerator: Expression
    denominator: Expression 

@dataclass
class Subscript(Expression):
    base: Expression
    subscript: Expression 

@dataclass
class Superscript(Expression):
    base: Expression
    superscript: Expression
    
@dataclass
class NthRoot(Expression):
    radicand: Expression
    degree: Expression 

@dataclass
class Matrix(Expression):
    rows: List[List[Expression]] 

@dataclass
class Equation(Expression):
    lhs: Expression
    rhs: Expression 

@dataclass
class Conditional(Expression):
    condition: Expression
    true_expr: Expression
    false_expr: Expression

# Catamorphism to Traverse the Expression Tree
def evaluate_expression(expr: Expression) -> str:
    if isinstance(expr, Value) and expr.result == False:
        return expr.value
    elif isinstance(expr, Value) and expr.result == True:
        return f"\\\\class{{result-box}}{{{expr.value}}}"
    elif isinstance(expr, Variable):
        return expr.name
    elif isinstance(expr, Operator):
        return expr.operator
    elif isinstance(expr, Parenthesis):
        return f"({evaluate_expression(expr.expression)})"
    elif isinstance(expr, Function):        
        return expr.function(f"({evaluate_expression(expr.expression)})")
    elif isinstance(expr, Compound):
        return "".join(evaluate_expression(e) for e in expr.expressions)
    elif isinstance(expr, Exponentiation):
        return f"{evaluate_expression(expr.base)}^{evaluate_expression(expr.exponent)}"
    elif isinstance(expr, Fraction):
        return f"({evaluate_expression(expr.numerator)}/{evaluate_expression(expr.denominator)})"
    elif isinstance(expr, Subscript):
        return f"{evaluate_expression(expr.base)}_{evaluate_expression(expr.subscript)}"
    elif isinstance(expr, Superscript):
        return f"{evaluate_expression(expr.base)}^{evaluate_expression(expr.superscript)}"
    elif isinstance(expr, NthRoot):
        return f"√[{evaluate_expression(expr.degree)}]{evaluate_expression(expr.radicand)}"
    elif isinstance(expr, Matrix):
        return "[" + "; ".join(["[" + ", ".join(evaluate_expression(e) for e in row) + "]" for row in expr.rows]) + "]"
    elif isinstance(expr, Equation):
        return f"{evaluate_expression(expr.lhs)} = {evaluate_expression(expr.rhs)}"
    elif isinstance(expr, Conditional):
        return f"if {evaluate_expression(expr.condition)} then {evaluate_expression(expr.true_expr)} else {evaluate_expression(expr.false_expr)}"
    else:
        pass
        #raise ValueError("Unknown Expression Type")

class MathOperationError(Enum):
    """
    Constants for various math operation errors.
    """
    DIVIDEBYZERO = "Divide by Zero Error"
    MATHDOMAINERROR = "Math Domain Error"

@dataclass
class MathOperationResult:
    """
    Represents the result of a math operation, including success and failure cases.
    
    Attributes:
        success (Optional[Number]): The result of the operation if successful.
        failure (Optional[MathOperationError]): The error if the operation failed.
    """
    success: Optional[Number] = None
    failure: Optional[MathOperationError] = None
    
    def __str__(self):
        return f"MathOperationResult(success='{success}', failure='{failure}')"

# Computation States
@dataclass
class AccumulatorStateData:
    """
    State data for the accumulator phase of the calculator.
    
    Attributes:
        digits (str): The digits accumulated.
        pending_op (Optional[PendingOp]): The pending operation.
        memory (str): The memory state.
    """     
    digits: str = ""
    pending_op: Optional[PendingOp] = None
    memory: str = ""    

    def __str__(self):
        return f"AccumulatorStateData(digits='{self.digits}', pending_op={self.pending_op}, memory='{self.memory}')"

@dataclass
class ComputedStateData:
    """
    State data for the computed phase of the calculator.
    
    Attributes:
        display_number (float): The number to display.
        pending_op (Optional[PendingOp]): The pending operation.
        memory (str): The memory state.
    """
    display_number: float = 0.0
    pending_op: Optional[PendingOp] = None
    memory: str = ""
        
    def __str__(self):
        return f"ComputedStateData(display_number={self.display_number}, pending_op={self.pending_op}, memory='{self.memory}')"

@dataclass
class ErrorStateData:
    """
    State data for the error phase of the calculator.
    
    Attributes:
        error (MathOperationError): The error encountered.
        memory (str): The memory state.
    """
    math_error: Optional[MathOperationError] = None
    # additional error types as needed
    memory: str = ""
                 
    def __str__(self):
        return f"ErrorStateData(math_error={self.math_error}, memory='{self.memory}')"

@dataclass
class ZeroStateData:
    """
    State data for the zero phase of the calculator.
    
    Attributes:
        pending_op (Optional[PendingOp]): The pending operation.
        memory (str): The memory state.
    """
    pending_op: Optional[PendingOp] = None
    memory: str = ""
    
    def __str__(self):
        return f"ZeroStateData(pending_op={self.pending_op}, memory='{self.memory}')"

####### Expression States#######
@dataclass
class StartStateData:
    memory: str = " "    
    

@dataclass
class NumberInputStateData:
    current_value: str
    expression_tree: Compound()
    memory: str = " "       
    stack: List[str] = field(default_factory=list)

@dataclass
class OperatorInputStateData:
    previous_value: str
    operator: str
    current_value: str
    expression_tree: Compound()
    memory: str = " "    
    stack: List[str] = field(default_factory=list)
    
@dataclass
class ResultStateData:
    result: str
    memory: str = " "    
    history: List[str] = field(default_factory=list) # ToDo
    
@dataclass
class ParenthesisOpenStateData:
    inner_expression: str
    expression_tree: Compound()
    memory: str = " "    
    stack: List[str] = field(default_factory=list)
    
@dataclass
class FunctionInputStateData:
    current_value: str
    expression_tree: Compound()
    memory: str = " "    
    stack: List[str] = field(default_factory=list)
    
    
    
