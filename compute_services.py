# ================================================
# Compute Services
# ================================================
from typing import Optional, Tuple, Union, Dict, Callable
from calculator_domain import (Expression, Value, Operator, Parenthesis, Function, Compound, CalculatorInput, Number, CalculatorMathOp,
                               ErrorStateData, StartStateData,  NumberInputStateData,
                               OperatorInputStateData, ResultStateData, ParenthesisOpenStateData, FunctionInputStateData)
import math

class ComputeServices:    
    def __init__(self):
        super().__init__()
        self.digit_display = " "   
    
    def receive_ten_key_display(self, display: str):
        self.digit_display = display
        print(f"Service received ten key display: {display}")
                
    def get_digit_display(self):
        return self.digit_display
    
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
    initial_state = StartStateData()
    """
    Returns a dictionary of charachter mappings to calculator inputs
    """
    input_mapping = {
            '+': (CalculatorInput.MATHOP, CalculatorMathOp.ADD),
            '-': (CalculatorInput.MATHOP, CalculatorMathOp.SUBTRACT),
            '*': (CalculatorInput.MATHOP, CalculatorMathOp.MULTIPLY),
            '/': (CalculatorInput.MATHOP, CalculatorMathOp.DIVIDE),
            '=': (CalculatorInput.EQUALS, None),
            '√': (CalculatorInput.MATHOP, CalculatorMathOp.ROOT)
        }