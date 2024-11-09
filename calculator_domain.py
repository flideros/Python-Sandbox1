# ================================================
# Calculator Domain using a state machine
# ================================================
from typing import Optional, Tuple, Union

# Type aliases for better readability
Number = float
DigitAccumulator = str

class NonZeroDigit:
    """
    Enumeration for non-zero digits.
    """
    ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE = range(1, 10)

class CalculatorMathOp:
    """
    Enumeration for calculator mathematical operations.
    """
    ADD, SUBTRACT, MULTIPLY, DIVIDE, INVERSE, PERCENT, ROOT, CHANGESIGN, MEMORYADD, MEMORYSUBTRACT = range(10)

# Type alias for a tuple representing a pending operation and its associated number
PendingOp = Tuple[CalculatorMathOp, Number]

class MathOperationError:
    """
    Constants for various math operation errors.
    """
    DIVIDEBYZERO = "Divide by Zero Error"
    MATHDOMAINERROR = "Math Domain Error"

class MathOperationResult:
    """
    Represents the result of a math operation, including success and failure cases.
    
    Attributes:
        success (Optional[Number]): The result of the operation if successful.
        failure (Optional[MathOperationError]): The error if the operation failed.
    """
    def __init__(self, success: Optional[Number] = None, failure: Optional[MathOperationError] = None):
        self.success = success
        self.failure = failure

class AccumulatorStateData:
    """
    State data for the accumulator phase of the calculator.
    
    Attributes:
        digits (str): The digits accumulated.
        pending_op (Optional[PendingOp]): The pending operation.
        memory (str): The memory state.
    """
    def __init__(self, digits: str = "", pending_op: Optional[PendingOp] = None, memory: str = ""):
        self.digits = digits
        self.pending_op = pending_op
        self.memory = memory

    def __str__(self): return f"AccumulatorStateData(digits='{self.digits}', pending_op={self.pending_op}, memory='{self.memory}')"

class ComputedStateData:
    """
    State data for the computed phase of the calculator.
    
    Attributes:
        display_number (float): The number to display.
        pending_op (Optional[PendingOp]): The pending operation.
        memory (str): The memory state.
    """
    def __init__(self, display_number: float = 0.0, pending_op: Optional[PendingOp] = None, memory: str = ""):
        self.display_number = display_number
        self.pending_op = pending_op
        self.memory = memory
        
    def __str__(self): return f"ComputedStateData(display_number={self.display_number}, pending_op={self.pending_op}, memory='{self.memory}')"

class ErrorStateData:
    """
    State data for the error phase of the calculator.
    
    Attributes:
        error (MathOperationError): The error encountered.
        memory (str): The memory state.
    """
    def __init__(self, error: MathOperationError, memory: str = ""):
        self.error = error
        self.memory = memory

    def __str__(self): return f"ErrorStateData(error={self.error}, memory='{self.memory}')"

class ZeroStateData:
    """
    State data for the zero phase of the calculator.
    
    Attributes:
        pending_op (Optional[PendingOp]): The pending operation.
        memory (str): The memory state.
    """
    def __init__(self, pending_op: Optional[PendingOp] = None, memory: str = ""):
        self.pending_op = pending_op
        self.memory = memory

    def __str__(self): return f"ZeroStateData(pending_op={self.pending_op}, memory='{self.memory}')"

class CalculatorState:
    """
    Enumeration for the different states of the calculator.
    """
    ZERO, ACCUMULATOR, COMPUTED, ERROR = range(4)

class CalculatorInput:
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
