# ================================================
# Implementation of Calculator
# ================================================
from typing import Optional, Tuple, Union
from calculator_domain import (
    AccumulatorStateData, ZeroStateData, ComputedStateData, ErrorStateData, MathOperationError,
    CalculatorInput, CalculatorMathOp, NonZeroDigit, DigitAccumulator, PendingOp
)
from calculator_services import CalculatorServices
import re

def create_calculate(services: CalculatorServices):   
    """
    Defines the state handlers and returns a calculate function to route the state to the appropriate handlers.
    
    Args:
        services (CalculatorServices): An instance of CalculatorServices containing various service functions.
        
    Returns:
        Callable[[CalculatorState, CalculatorInput, str], CalculatorState]: A function that processes the given state and input, and returns the new state. """
    # Handle input during Zero state and return new state 
    def handle_zero_state(state_data: ZeroStateData, input, memory):
        """
        Handles input during the Zero state and returns the new state.
        
        Args:
            state_data (ZeroStateData): The current state data in the Zero state.
            input (CalculatorInput): The input received by the calculator.
            memory (str): The current memory value of the calculator.
        
        Returns:
            CalculatorState: The new state of the calculator after processing the input.
        """
        digits = " "   # empty digit accumlator for state transitions     
        if input == CalculatorInput.ZERO:
            print("Zero Input - State remains ZeroState")
            return ZeroStateData(pending_op=state_data.pending_op, memory=state_data.memory)

        elif input[0] == 'DIGIT' and input[1] in range(1, 10):
            accumulate_function = services['accumulate_non_zero_digit']
            new_digits = accumulate_function(input[1], digits)  # Now call the function with the correct arguments
            return AccumulatorStateData(digits=new_digits, pending_op=state_data.pending_op, memory=state_data.memory)

        elif input == CalculatorInput.DECIMALSEPARATOR:
            new_digits = services["accumulate_separator"](digits)
            print(f"Decimal added to accumulator: {new_digits}")
            return AccumulatorStateData(digits=new_digits, pending_op=state_data.pending_op, memory=state_data.memory)

        elif input[0] == 'MATHOP' and input[1] in range(0, 9):   
            if input[1] in [CalculatorMathOp.DIVIDE, CalculatorMathOp.MULTIPLY, CalculatorMathOp.SUBTRACT, CalculatorMathOp.ADD]:
                if state_data.pending_op is None:
                    new_op = (input[1], 0)
                    return ZeroStateData(pending_op=new_op, memory=state_data.memory)
                else:
                    _old_op, numb = state_data.pending_op
                    new_op = (input[1], numb)
                    return ZeroStateData(pending_op=new_op, memory=state_data.memory)
                
            elif input[1] in [CalculatorMathOp.MEMORYADD, CalculatorMathOp.MEMORYSUBTRACT]:
                return ZeroStateData(pending_op=state_data.pending_op, memory=memory)

            elif input[1] == CalculatorMathOp.CHANGESIGN:
                return AccumulatorStateData(digits="-", pending_op=state_data.pending_op, memory=memory)

            elif input[1] == CalculatorMathOp.INVERSE:
                return ErrorStateData(error=MathOperationError.DIVIDEBYZERO, memory=memory)

            elif input[1] in [CalculatorMathOp.ROOT, CalculatorMathOp.PERCENT]:
                return ZeroStateData(pending_op=state_data.pending_op, memory=memory)

        elif input == CalculatorInput.EQUALS:
            if state_data.pending_op is not None:
                pending_op, _ = state_data.pending_op
                if pending_op == CalculatorMathOp.DIVIDE:
                    return ErrorStateData(error=MathOperationError.DIVIDEBYZERO, memory=memory)
            return ZeroStateData(pending_op=state_data.pending_op, memory=memory)

        elif input == CalculatorInput.CLEARENTRY:
            return ZeroStateData(pending_op=state_data.pending_op, memory=memory)

        elif input == CalculatorInput.CLEAR:
            return ZeroStateData(pending_op=None, memory=memory)

        elif input == CalculatorInput.BACK:
            return ZeroStateData(pending_op=state_data.pending_op, memory=memory)

        elif input == CalculatorInput.MEMORYSTORE:
            return ZeroStateData(pending_op=state_data.pending_op, memory="0")

        elif input == CalculatorInput.MEMORYCLEAR:
            return ZeroStateData(pending_op=state_data.pending_op, memory=" ")

        elif input == CalculatorInput.MEMORYRECALL:
            return AccumulatorStateData(digits=memory, pending_op=state_data.pending_op, memory=memory)                

        return state_data  # Return the current state if no condition matches

    # Handle input during Accmulator state and return new state
    
    def handle_accumulator_state(state_data: AccumulatorStateData, input):
        """
        Handles input during the Accumulator state and returns the new state.
        
        Args:
            state_data (AccumulatorStateData): The current state data in the Accumulator state.
            input (CalculatorInput): The input received by the calculator.
        
        Returns:
            CalculatorState: The new state of the calculator after processing the input.
        """
        if input[0] == 'DIGIT' and input[1] in range(1, 10):
            new_digits = services["accumulate_non_zero_digit"](input[1], state_data.digits)
            return AccumulatorStateData(digits=new_digits, pending_op=state_data.pending_op, memory=state_data.memory)

        elif input == CalculatorInput.DECIMALSEPARATOR:
            new_digits = services["accumulate_separator"](state_data.digits)
            print(f"Decimal added to accumulator: {new_digits}")
            return AccumulatorStateData(digits=new_digits, pending_op=state_data.pending_op, memory=state_data.memory)

        elif input == CalculatorInput.ZERO:
            new_digits = services["accumulate_zero"](state_data.digits)
            print(f"Accumulating zero to {state_data.digits}, Result: {new_digits}")
            return AccumulatorStateData(digits=new_digits, pending_op=state_data.pending_op, memory=state_data.memory)

        elif input[0] == 'MATHOP' and input[1] in range(0, 10):   
            if input[1] in [CalculatorMathOp.DIVIDE, CalculatorMathOp.MULTIPLY, CalculatorMathOp.SUBTRACT, CalculatorMathOp.ADD]:
                if state_data.pending_op is None:
                    new_op = (input[1], float(state_data.digits))
                    return ZeroStateData(pending_op=new_op, memory=state_data.memory)
                else:
                    _old_op, numb = state_data.pending_op
                    new_op = (input[1], numb)
                    return AccumulatorStateData(digits=state_data.digits,pending_op=new_op, memory=state_data.memory)
            
            elif input[1] == CalculatorMathOp.MEMORYADD:                
                try: d = float(state_data.digits)
                except ValueError: d = None                
                try: e = float(state_data.memory)
                except ValueError: e = None
                
                if d is not None and e is not None:
                    math_result = services['do_math_operation'](CalculatorMathOp.MEMORYADD,d,e,memory=state_data.memory)
                    new_memory = str(math_result.success)
                    print(f"{d} added to memory.")
                elif d is None and e is not None: new_memory = str(e)
                elif d is not None and e is None: new_memory = str(d)
                else: new_memory = " "
                print(f"Memory now {new_memory}")
                return AccumulatorStateData(digits=state_data.digits, pending_op=state_data.pending_op, memory=new_memory)
                        
            elif input[1] == CalculatorMathOp.MEMORYSUBTRACT:                
                try: d = float(state_data.digits)
                except ValueError: d = None                
                try: e = float(state_data.memory)
                except ValueError: e = None
                
                if d is not None and e is not None:
                    math_result = services['do_math_operation'](CalculatorMathOp.MEMORYSUBTRACT,d,e,memory=state_data.memory)
                    new_memory = str(math_result.success)
                    print(f"{d} subtracted from memory.")
                elif d is None and e is not None: new_memory = str(e)
                elif d is not None and e is None: new_memory = str(-d)
                else: new_memory = " "
                print(f"Memory now {new_memory}")
                return AccumulatorStateData(digits=state_data.digits, pending_op=state_data.pending_op, memory=new_memory)
  
            elif input[1] == CalculatorMathOp.CHANGESIGN:
                try: d = float(state_data.digits)
                except ValueError: d = None
                if d is not None:
                    math_result = services['do_math_operation'](CalculatorMathOp.CHANGESIGN,d,-1,memory=state_data.memory)
                    if math_result.success > 0:                        
                        new_digits = str(math_result.success)                        
                        return AccumulatorStateData(digits=new_digits, pending_op=state_data.pending_op, memory=state_data.memory)
                    else:
                        new_digits = '-' + state_data.digits
                        return AccumulatorStateData(digits=new_digits, pending_op=state_data.pending_op, memory=state_data.memory)
                    
                return state_data
                
            elif input[1] == CalculatorMathOp.INVERSE: # op 4
                try: d = float(state_data.digits)
                except ValueError: d = None
                if d == None:
                    return AccumulatorStateData(digits=state_data.digits, pending_op=state_data.pending_op, memory=state_data.memory)
                else:
                    math_result = services['do_math_operation'](CalculatorMathOp.INVERSE,d,1,memory=state_data.memory)
                    if math_result.success is not None:
                        if state_data.pending_op is None:
                            return ComputedStateData(display_number = math_result.success, memory=state_data.memory)
                        else:
                            return AccumulatorStateData(digits=str(math_result.success), pending_op=state_data.pending_op, memory=state_data.memory)
                    else:
                        return ErrorStateData(error=math_result.failure,memory=state_data.memory)
                
            elif input[1] == CalculatorMathOp.ROOT:
                try: d = float(state_data.digits)
                except ValueError: d = None
                if d == None:
                    return AccumulatorStateData(digits=state_data.digits, pending_op=state_data.pending_op, memory=state_data.memory)
                else:
                    math_result = services['do_math_operation'](CalculatorMathOp.ROOT,d,1,memory=state_data.memory)
                    if math_result.success is not None:
                        if state_data.pending_op is None:
                            return ComputedStateData(display_number = math_result.success, memory=state_data.memory)
                        else:
                            return AccumulatorStateData(digits=str(math_result.success), pending_op=state_data.pending_op, memory=state_data.memory)
                    else:
                        print(math_result.failure)
                        return ErrorStateData(error=math_result.failure, memory=state_data.memory)
            
            elif input[1] == CalculatorMathOp.PERCENT:
                try: d = float(state_data.digits)
                except ValueError: d = None
                if d == None:
                    return AccumulatorStateData(digits=state_data.digits, pending_op=state_data.pending_op, memory=state_data.memory)
                else:
                    math_result = services['do_math_operation'](CalculatorMathOp.PERCENT,d,None,memory=state_data.memory)
                    if state_data.pending_op is None:
                        return ComputedStateData(display_number = math_result.success,memory=state_data.memory)
                    else:
                        return AccumulatorStateData(digits=str(math_result.success), pending_op=state_data.pending_op, memory=state_data.memory)              

        elif input == CalculatorInput.EQUALS:
            print("performing calculation")
            new_state = _get_computation_state(services,accumulator_state_data=state_data, next_op=None)
            return new_state
           
        elif input == CalculatorInput.CLEARENTRY:
            print("clear entry")
            if state_data.pending_op is not None:
                return AccumulatorStateData(digits=" ", pending_op=state_data.pending_op, memory=state_data.memory)
            else:
                return ZeroStateData(pending_op=None, memory=state_data.memory)

        elif input == CalculatorInput.CLEAR:
            print("Clearing - State reset to ZeroState")
            return ZeroStateData(pending_op=None, memory=state_data.memory)

        elif input == CalculatorInput.BACK:            
            string_length = len(state_data.digits)
            first_n_chars = re.match(r'.{%d}' % (string_length-1), state_data.digits).group()
            if len(first_n_chars) < 1:
                print("Can't go back from empty accumulator, return to Zero state")
                return ZeroStateData(pending_op=state_data.pending_op, memory=state_data.memory)            
            elif len(first_n_chars) == 1 and '-' in first_n_chars:                
                print("Last item removed from accumulator")
                return ZeroStateData(pending_op=state_data.pending_op, memory=state_data.memory)            
            else:
                print("Last item removed from accumulator")
                return AccumulatorStateData(digits=first_n_chars, pending_op=state_data.pending_op, memory=state_data.memory)              

        elif input == CalculatorInput.MEMORYSTORE:
            return AccumulatorStateData(digits=state_data.digits, pending_op=state_data.pending_op, memory=state_data.digits)

        elif input == CalculatorInput.MEMORYCLEAR:
            return ZeroStateData(pending_op=state_data.pending_op, memory="")

        elif input == CalculatorInput.MEMORYRECALL:
            return AccumulatorStateData(digits=state_data.memory, pending_op=state_data.pending_op, memory=state_data.memory)

        return state_data  # Return the current state if no condition matches    
    
    def handle_computed_state(state_data: ComputedStateData, input):
        """
        Handles input during the Computed state and returns the new state.

        Args:
            state_data (ComputedStateData): The current state data in the Computed state.
            input (CalculatorInput): The input received by the calculator.
            memory (str): The current memory value of the calculator.
            
        Returns:
            CalculatorState: The new state of the calculator after processing the input.
        """
        empty_accumulator_state_data = AccumulatorStateData(digits=" ", pending_op=state_data.pending_op, memory=state_data.memory)

        if input == CalculatorInput.ZERO:
            return ZeroStateData(pending_op=empty_accumulator_state_data.pending_op, memory=state_data.memory)

        elif input[0] == 'DIGIT' and input[1] in range(1, 10):
            new_digits = services["accumulate_non_zero_digit"](input[1], " ")
            return AccumulatorStateData(digits=new_digits, pending_op=state_data.pending_op, memory=state_data.memory)

        elif input == CalculatorInput.DECIMALSEPARATOR:
            new_accumulator_data = AccumulatorStateData(digits="0.", pending_op=state_data.pending_op, memory=state_data.memory)
            print(f"Decimal added to accumulator: {new_digits}")
            return new_accumulator_data
        
        elif input[0] == 'MATHOP' and input[1] in range(0, 10):   
            if input[1] in [CalculatorMathOp.DIVIDE, CalculatorMathOp.MULTIPLY, CalculatorMathOp.SUBTRACT, CalculatorMathOp.ADD]:
                next_op = input[1]
                pending_op = (next_op, state_data.display_number)
                return ZeroStateData(pending_op=pending_op, memory=state_data.memory)
            
            elif input[1] == CalculatorMathOp.MEMORYADD:
                d = state_data.display_number                
                try: e = float(state_data.memory)
                except ValueError: e = None
                
                if e is not None:
                    math_result = services['do_math_operation'](CalculatorMathOp.MEMORYADD,d,e,memory=state_data.memory)
                    new_memory = str(math_result.success)            
                elif e is None: new_memory = str(d)
                else: new_memory = " "
                print(f"Memory now {new_memory}")
                return ComputedStateData(display_number=state_data.display_number, memory=new_memory)
                        
            elif input[1] == CalculatorMathOp.MEMORYSUBTRACT:
                d = state_data.display_number               
                try: e = float(state_data.memory)
                except ValueError: e = None
                
                if e is not None:
                    math_result = services['do_math_operation'](CalculatorMathOp.MEMORYSUBTRACT,d,e,memory=state_data.memory)
                    new_memory = str(math_result.success)
                elif e is None: new_memory = str(-d)
                else: new_memory = " "
                print(f"Memory now {new_memory}")
                return ComputedStateData(display_number=state_data.display_number, memory=new_memory)
  
            elif input[1] == CalculatorMathOp.CHANGESIGN:
                d = state_data.display_number
                math_result = services['do_math_operation'](CalculatorMathOp.CHANGESIGN,d,-1,memory=state_data.memory)
                return ComputedStateData(display_number=math_result.success, memory=state_data.memory)
                
            elif input[1] == CalculatorMathOp.INVERSE:
                d = state_data.display_number
                math_result = services['do_math_operation'](CalculatorMathOp.INVERSE,d,1,memory=state_data.memory)
                if math_result.success is not None:
                    return ComputedStateData(display_number = math_result.success, memory=state_data.memory)
                else:
                    return ErrorStateData(error=math_result.failure, memory=state_data.memory)
                
            elif input[1] == CalculatorMathOp.ROOT:
                d = state_data.display_number
                math_result = services['do_math_operation'](CalculatorMathOp.ROOT,d,1,memory=state_data.memory)
                if math_result.success is not None:
                    return ComputedStateData(display_number = math_result.success, memory=state_data.memory)
                else:
                    print(math_result.failure)
                    return ErrorStateData(error=math_result.failure, memory=state_data.memory)
            
            elif input[1] == CalculatorMathOp.PERCENT:
                d = state_data.display_number
                math_result = services['do_math_operation'](CalculatorMathOp.PERCENT,d,None,memory=state_data.memory)
                return ComputedStateData(display_number = math_result.success, memory=state_data.memory)          
        
        elif input == CalculatorInput.EQUALS:
            return state_data

        elif input == CalculatorInput.CLEARENTRY:
            return ZeroStateData(pending_op=None, memory=state_data.memory)

        elif input == CalculatorInput.CLEAR:
            return ZeroStateData(pending_op=None, memory=state_data.memory)

        elif input == CalculatorInput.BACK:
            return state_data

        elif input == CalculatorInput.MEMORYSTORE:
            return ComputedStateData(display_number=state_data.display_number, memory=str(state_data.display_number))  # Store current digits in memory

        elif input == CalculatorInput.MEMORYCLEAR:
            return ComputedStateData(display_number=state_data.display_number, memory=" ")  # Clear memory

        elif input == CalculatorInput.MEMORYRECALL:
            return ComputedStateData(display_number=float(state_data.memory), memory=state_data.memory)
        
    # Handle input during Error state and return zero state for input CLEAR
    def handle_error_state(state_data: ErrorStateData, input, memory):
        """
        Handles input during the Error state and returns the new state.
        
        Args:
            state_data (ErrorStateData): The current state data in the Error state.
            input (CalculatorInput): The input received by the calculator.
            memory (str): The current memory value of the calculator.
        Returns:
            CalculatorState: The new state of the calculator after processing the input.
        """
        if input in [
            CalculatorInput.ZERO,
            CalculatorInput.DIGIT,
            CalculatorInput.DECIMALSEPARATOR,
            CalculatorInput.MATHOP,
            CalculatorInput.CLEARENTRY,
            CalculatorInput.BACK,
            CalculatorInput.MEMORYSTORE,
            CalculatorInput.MEMORYCLEAR,
            CalculatorInput.MEMORYRECALL,
            CalculatorInput.EQUALS,
        ]:
            return state_data  # Stay in ErrorState
        elif input == CalculatorInput.CLEAR:
            return ZeroStateData(pending_op=None, memory=" ")  # Transition to ZeroState and throw away any pending ops
    
    # Helper function to assist in evaluating a binary operation from Accumulator state
    def _get_computation_state(services, accumulator_state_data: AccumulatorStateData, next_op) -> Union[ComputedStateData, ErrorStateData]:
        """
        Processes the accumulator state data and returns the new state based on the current operation.
        
        Args:
            services (CalculatorServices): An instance of CalculatorServices containing various service functions.
            accumulator_state_data (AccumulatorStateData): The current state data in the Accumulator state.
            next_op (Optional[CalculatorMathOp]): The next mathematical operation to be performed.
        
        Returns:
            CalculatorState: The new state of the calculator after processing the current operation.
        """
        def get_new_state(display_number):
            """
            Creates a new state with the given display number and returns a ComputedStateData instance.

            Args:
                display_number (float): The number to be displayed in the calculator.
            
            Returns:
                ComputedStateData: The new state data with the updated display number, pending operation, and memory.
            """
            new_pending_op = (next_op, display_number) if next_op else None
            return ComputedStateData(display_number=display_number, pending_op=new_pending_op, memory=accumulator_state_data.memory)
        
        current_number = services['get_number_from_accumulator'](accumulator_state_data)
        compute_state_with_no_pending_op = get_new_state(current_number)
        
        if accumulator_state_data.pending_op:
            op, previous_number = accumulator_state_data.pending_op
            result = services['do_math_operation'](op, previous_number, current_number, accumulator_state_data.memory)
            if result.success is not None:
                return get_new_state(result.success)
            else:
                return ErrorStateData(error=result.failure, memory=" ")
        
        return compute_state_with_no_pending_op
    
    
    def calculate(input, state):
        """
        Routes the input and state to the appropriate handler and returns the new calculator state.
        
        Args:
            input (CalculatorInput): The input received by the calculator.
            state (CalculatorState): The current state of the calculator.
            
        Returns:
            Optional[CalculatorState]: The new state of the calculator after processing the input,
            or None if the input is not handled by any state.
        """
        if isinstance(state, ZeroStateData):
            return handle_zero_state(state, input, state.memory)
        elif isinstance(state, AccumulatorStateData):
            return handle_accumulator_state(state, input)
        elif isinstance(state, ComputedStateData):
            return handle_computed_state(state, input)  # Ensure input is passed here
        elif isinstance(state, ErrorStateData):
            return handle_error_state(state, input, state.memory)
        return None

    return calculate