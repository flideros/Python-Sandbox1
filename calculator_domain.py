# ================================================
# Calculator Domain using a state machine
# ================================================
from typing import Optional, Tuple, Union, List
from enum import Enum
from dataclasses import dataclass

# Type aliases for better readability
Number = float
DigitAccumulator = str

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

# Type alias for a tuple representing a pending operation and its associated number
PendingOp = Tuple[CalculatorMathOp, Number]

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
class ParenthesisOpenState:
    inner_expression: str

@dataclass
class RootInputState:
    current_value: str

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
    MEMORYSTORE = "MEMORYSTORE"
    MEMORYCLEAR = "MEMORYCLEAR"
    MEMORYRECALL = "MEMORYRECALL"
    
    def __call__(self, *args):
        if callable(self.value):
            return self.value(*args)
        raise TypeError(f"{self.name} is not callable")
    
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
class Root(Expression):
    expression: 'Expression'

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
    elif isinstance(expr, Root):
        return f"√({evaluate_expression(expr.expression)})"
    elif isinstance(expr, Compound):
        return "".join(evaluate_expression(e) for e in expr.expressions)
    else:
        raise ValueError("Unknown Expression Type")
