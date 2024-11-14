# ================================================
# Compute Services
# ================================================
from typing import Optional, Tuple, Union, Dict, Callable
from calculator_domain import (Expression, Value, Operator, Parenthesis, Function, Compound, CalculatorInput, Number, CalculatorMathOp,
                               ErrorStateData, AccumulatorStateData, StartStateData,  NumberInputStateData,
                               OperatorInputStateData, ResultStateData, ParenthesisOpenStateData, FunctionInputStateData)
import math

class ComputeServices:
    #pass
    def get_number_from_accumulator(self, accumulator_state_data) -> Number:
        """
        Converts the digits in the accumulator to a float number.
        """
        try:
            return float(accumulator_state_data.digits)
        except ValueError:
            return 0.0
        
    def get_display_from_state(self, error_msg: str):
        """
        Returns the display strings based on the current state of the computation.
        """
        def inner(calculator_state) -> str:
            if isinstance(calculator_state, StartStateData):
                return " "
            
            elif isinstance(calculator_state, NumberInputStateData):
                return calculator_state.expression_tree
            
            elif isinstance(calculator_state, OperatorInputStateData):
                return calculator_state.expression_tree
            
            elif isinstance(calculator_state, ResultStateData):
                return calculator_state.result
            
            elif isinstance(calculator_state, ParenthesisOpenStateData):
                return calculator_state.expression_tree
            
            elif isinstance(calculator_state, FunctionInputStateData):
                return calculator_state.expression_tree
                
            elif isinstance(calculator_state, ErrorStateData):
                return error_msg + calculator_state.math_error.value
        return inner
    
    """
    Returns the initial state of the calculator.
    """
    initial_state = StartStateData(memory=" ")
    """
    Returns a dictionary of charachter mappings to calculator inputs
    """
    input_mapping = {
            '+': (CalculatorInput.MATHOP, CalculatorMathOp.ADD),
            '-': (CalculatorInput.MATHOP, CalculatorMathOp.SUBTRACT),
            '*': (CalculatorInput.MATHOP, CalculatorMathOp.MULTIPLY),
            '/': (CalculatorInput.MATHOP, CalculatorMathOp.DIVIDE),
            '=': (CalculatorInput.EQUALS, None),
            '√': (CalculatorInput.MATHOP, CalculatorMathOp.ROOT),

        }
    
    """
    Returns a dictionary of charachter mappings to calculator inputs
    """
    @staticmethod
    
    def create_services() -> Dict[str, Callable]:
        """
        Creates and returns a dictionary of compute service functions.
        Each service function is mapped to a corresponding key, allowing for
        easy access and invocation of various calculator operations such as
        digit accumulation, mathematical operations, and state retrieval.
            
        Returns:
            dict: A dictionary with the following keys and corresponding service functions:
            - "get_number_from_accumulator": Function to convert accumulator to a number.
            - "get_display_from_state": Function to retrieve display string from calculator state.
        """
        services = CalculatorServices()
        return {
            "get_number_from_accumulator": services.get_number_from_accumulator,
            "get_display_from_state": services.get_display_from_state("ERROR:")
        }