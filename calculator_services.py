# ================================================
# Calculator Services
# ================================================
from typing import Optional, Tuple, Union, Dict, Callable
from calculator_domain import (NonZeroDigit, PendingOp, CalculatorMathOp, Number,
    DigitAccumulator, ZeroStateData, AccumulatorStateData, ComputedStateData,
    ErrorStateData, MathOperationError, MathOperationResult, CalculatorInput)
import math

class CalculatorServices:
    def append_to_accumulator(self, max_len: int, accumulator: DigitAccumulator, append_ch: str) -> DigitAccumulator:
        """
        Appends a character to the accumulator if it doesn't exceed the maximum length.
        """
        if len(accumulator.strip()) >= max_len:
            print("Max length reached; ignoring new input.")
            return accumulator.strip()  # Ignore new input if length exceeds max
        print(f"Appending '{append_ch}' to accumulator '{accumulator.strip()}'.")
        return accumulator.strip() + append_ch

    def accumulate_non_zero_digit(self, max_len: int):
        """
        Returns a function that appends a non-zero digit to the accumulator.
        """
        def inner(digit: NonZeroDigit, accumulator: DigitAccumulator) -> DigitAccumulator:
            append_ch = str(digit)
            new_accumulator = self.append_to_accumulator(max_len, accumulator.strip(), append_ch)
            print(f"Resulting accumulator: '{new_accumulator}'")
            return new_accumulator
        return inner

    def accumulate_zero(self, max_len: int):
        """
        Returns a function that appends a zero to the accumulator.
        """
        def inner(accumulator: DigitAccumulator) -> DigitAccumulator:
            print(f"Accumulating zero to: '{accumulator.strip()}'")
            return self.append_to_accumulator(max_len, accumulator.strip(), "0")
        return inner

    def accumulate_separator(self, max_len: int):
        """
        Returns a function that appends a decimal separator to the accumulator.
        """
        def inner(accumulator: DigitAccumulator) -> DigitAccumulator:
            if '.' in accumulator:
                return accumulator
            else:
                append_ch = "0." if accumulator.strip() == "" else "."
                print(f"Accumulating separator to: '{accumulator.strip()}'")    
                new_accumulator = self.append_to_accumulator(max_len, accumulator.strip(), append_ch)
                print(f"Resulting accumulator: '{new_accumulator}'")
                return new_accumulator
        return inner
    
    def get_number_from_accumulator(self, accumulator_state_data) -> Number:
        """
        Converts the digits in the accumulator to a float number.
        """
        try:
            return float(accumulator_state_data.digits)
        except ValueError:
            return 0.0

    def do_math_operation(self, op: CalculatorMathOp, f1: Number, f2: Number, memory: DigitAccumulator) -> MathOperationResult:
        """
        Performs a mathematical operation based on the provided operator.
        """
        if op == CalculatorMathOp.PERCENT:
            print(f"convert to percent: '{f1}'")
            return MathOperationResult(success=f1/100)
        elif op == CalculatorMathOp.ROOT:
            try: d = math.sqrt(f1)
            except ValueError: d = None
            if d is not None:                
                return MathOperationResult(success=d)
            else:
                return MathOperationResult(failure=MathOperationError.MATHDOMAINERROR)
        elif op == CalculatorMathOp.INVERSE:
            if f1 == 0:
                return MathOperationResult(failure=MathOperationError.DIVIDEBYZERO)
            return MathOperationResult(success=f2 / f1)
        elif op == CalculatorMathOp.ADD:
            return MathOperationResult(success=f1 + f2)
        elif op == CalculatorMathOp.SUBTRACT:
            return MathOperationResult(success=f1 - f2)
        elif op == CalculatorMathOp.MULTIPLY:
            return MathOperationResult(success=f1 * f2)
        elif op == CalculatorMathOp.DIVIDE:
            if f2 == 0:
                return MathOperationResult(failure=MathOperationError.DIVIDEBYZERO)
            return MathOperationResult(success=f1 / f2)
        elif op == CalculatorMathOp.CHANGESIGN:
            return MathOperationResult(success=f1 * -1)
        elif op == CalculatorMathOp.MEMORYADD:
            return MathOperationResult(success=f1 + f2) 
        elif op == op == CalculatorMathOp.MEMORYSUBTRACT:
            return MathOperationResult(success=f2 - f1) 
        
    def get_display_from_state(self, error_msg: str):
        """
        Returns the display strings based on the current state of the calculator.
        """
        def inner(calculator_state) -> str:
            if isinstance(calculator_state, ZeroStateData):
                return "0"
            elif isinstance(calculator_state, AccumulatorStateData):
                accu_str = calculator_state.digits
                number_str = str(self.get_number_from_accumulator(calculator_state))
                if '.' in number_str and '.' in accu_str:
                    return accu_str
                else:
                    return number_str.rstrip('0').rstrip('.')
                return number_str
            elif isinstance(calculator_state, ComputedStateData):
                number_str = f"{calculator_state.display_number:.10g}"  # Format to limit significant digits
                if '.' in number_str:
                    return number_str.rstrip('0') #.rstrip('.')
                return number_str
            elif isinstance(calculator_state, ErrorStateData):
                return error_msg + calculator_state.math_error.value
        return inner

    def get_pending_op_from_state(self):
        """
        Returns the pending operation string based on the current state of the calculator.
        """
        def op_to_string(op: CalculatorMathOp) -> str:
            return {
                CalculatorMathOp.ADD: "+",
                CalculatorMathOp.SUBTRACT: "-",
                CalculatorMathOp.MULTIPLY: "*",
                CalculatorMathOp.DIVIDE: "/",
                CalculatorMathOp.CHANGESIGN: "(change sign)",
                CalculatorMathOp.INVERSE: "(inverse)"
            }.get(op, "")

        def display_string_for_pending_op(pending_op: Optional[PendingOp]) -> str:
            if pending_op:
                op, number = pending_op
                formatted_number = str(number).rstrip('0').rstrip('.') if '.' in str(number) else str(number)
                return f"{formatted_number} {op_to_string(op)}"
            return ""

        def inner(calculator_state) -> str:
            if calculator_state is None or isinstance(calculator_state, ErrorStateData) or calculator_state.pending_op is None:
                return ""
            return display_string_for_pending_op(calculator_state.pending_op)

        return inner
 
    def get_memo_from_state(self):
        """
        Returns the memory indicator string based on the current state of the calculator.
        """
        def get_memo_from(state_data: DigitAccumulator) -> str:
            return "M" if state_data.strip() != "" else " "

        def inner(calculator_state) -> str:
            if calculator_state is None or calculator_state.memory is None:
                return " "
            return get_memo_from(calculator_state.memory)

        return inner
    """
    Returns the initial state of the calculator.
    """
    initial_state = ZeroStateData(pending_op=None, memory=" ")
    """
    Returns a dictionary of charachter mappings to calculator inputs
    """
    input_mapping = {
            '0': (CalculatorInput.ZERO, None),
            '1': (CalculatorInput.DIGIT, NonZeroDigit.ONE),
            '2': (CalculatorInput.DIGIT, NonZeroDigit.TWO),
            '3': (CalculatorInput.DIGIT, NonZeroDigit.THREE),
            '4': (CalculatorInput.DIGIT, NonZeroDigit.FOUR),
            '5': (CalculatorInput.DIGIT, NonZeroDigit.FIVE),
            '6': (CalculatorInput.DIGIT, NonZeroDigit.SIX),
            '7': (CalculatorInput.DIGIT, NonZeroDigit.SEVEN),
            '8': (CalculatorInput.DIGIT, NonZeroDigit.EIGHT),
            '9': (CalculatorInput.DIGIT, NonZeroDigit.NINE),
            '.': (CalculatorInput.DECIMALSEPARATOR, None),
            '+': (CalculatorInput.MATHOP, CalculatorMathOp.ADD),
            '-': (CalculatorInput.MATHOP, CalculatorMathOp.SUBTRACT),
            '*': (CalculatorInput.MATHOP, CalculatorMathOp.MULTIPLY),
            '/': (CalculatorInput.MATHOP, CalculatorMathOp.DIVIDE),
            '=': (CalculatorInput.EQUALS, None),
            '√': (CalculatorInput.MATHOP, CalculatorMathOp.ROOT),
            '±': (CalculatorInput.MATHOP, CalculatorMathOp.CHANGESIGN),
            '1/x': (CalculatorInput.MATHOP, CalculatorMathOp.INVERSE),
            '%': (CalculatorInput.MATHOP, CalculatorMathOp.PERCENT),
            '←': (CalculatorInput.BACK, None),
            'C': (CalculatorInput.CLEAR, None),
            'CE': (CalculatorInput.CLEARENTRY, None),
            'MC': (CalculatorInput.MEMORYCLEAR, None),
            'MR': (CalculatorInput.MEMORYRECALL, None),
            'MS': (CalculatorInput.MEMORYSTORE, None),
            'M+': (CalculatorInput.MATHOP, CalculatorMathOp.MEMORYADD),
            'M-': (CalculatorInput.MATHOP, CalculatorMathOp.MEMORYSUBTRACT)
        }
    
    ten_key_input_mapping = {
            '0': (CalculatorInput.ZERO, None),
            '1': (CalculatorInput.DIGIT, NonZeroDigit.ONE),
            '2': (CalculatorInput.DIGIT, NonZeroDigit.TWO),
            '3': (CalculatorInput.DIGIT, NonZeroDigit.THREE),
            '4': (CalculatorInput.DIGIT, NonZeroDigit.FOUR),
            '5': (CalculatorInput.DIGIT, NonZeroDigit.FIVE),
            '6': (CalculatorInput.DIGIT, NonZeroDigit.SIX),
            '7': (CalculatorInput.DIGIT, NonZeroDigit.SEVEN),
            '8': (CalculatorInput.DIGIT, NonZeroDigit.EIGHT),
            '9': (CalculatorInput.DIGIT, NonZeroDigit.NINE),
            '.': (CalculatorInput.DECIMALSEPARATOR, None),
            '←': (CalculatorInput.BACK, None),
            'CE': (CalculatorInput.CLEARENTRY, None),
            'MR': (CalculatorInput.MEMORYRECALL, None)
        }
    """
    Returns a dictionary of charachter mappings to calculator inputs
    """
    @staticmethod
    
    def create_services() -> Dict[str, Callable]:
        """
        Creates and returns a dictionary of calculator service functions.
        Each service function is mapped to a corresponding key, allowing for
        easy access and invocation of various calculator operations such as
        digit accumulation, mathematical operations, and state retrieval.
            
        Returns:
            dict: A dictionary with the following keys and corresponding service functions:
            - "accumulate_non_zero_digit": Function to accumulate non-zero digits.
            - "accumulate_zero": Function to accumulate zeros.
            - "accumulate_separator": Function to accumulate decimal separators.
            - "do_math_operation": Function to perform mathematical operations.
            - "get_number_from_accumulator": Function to convert accumulator to a number.
            - "get_display_from_state": Function to retrieve display string from calculator state.
            - "get_pending_op_from_state": Function to retrieve pending operation from calculator state.
            - "get_memo_from_state": Function to retrieve memory state.
        """
        services = CalculatorServices()
        return {
            "accumulate_non_zero_digit": services.accumulate_non_zero_digit(10),
            "accumulate_zero": services.accumulate_zero(15),
            "accumulate_separator": services.accumulate_separator(15),
            "do_math_operation": services.do_math_operation,
            "get_number_from_accumulator": services.get_number_from_accumulator,
            "get_display_from_state": services.get_display_from_state("ERROR:"),
            "get_pending_op_from_state": services.get_pending_op_from_state(),
            "get_memo_from_state": services.get_memo_from_state()
        }