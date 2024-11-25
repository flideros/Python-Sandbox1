# ================================================
# Compute Services
# ================================================
from typing import Optional, Tuple, Union, Dict, Callable
from calculator_domain import (Expression, Value, Operator, Parenthesis, Function, Compound, CalculatorInput, Number, CalculatorMathOp,
                               ErrorStateData, StartStateData,  NumberInputStateData, MathFunction,
                               OperatorInputStateData, ResultStateData, ParenthesisOpenStateData, FunctionInputStateData)
import math

class ComputeServices:    
    def __init__(self):
        super().__init__()
        self.digit_display = " "   
    
    def handle_return(self,state) -> bool:
        def inner(state) -> bool:
            if isinstance(state, StartStateData):
                return False
            
            elif isinstance(state, NumberInputStateData):
                return False
            
            elif isinstance(state, OperatorInputStateData):
                return False
            
            elif isinstance(state, ResultStateData):
                return True
            
            elif isinstance(state, ParenthesisOpenStateData):
                return False
            
            elif isinstance(state, FunctionInputStateData):
                return False
                
            elif isinstance(state, ErrorStateData):
                return False
        return inner(state)
    
    def receive_ten_key_display(self, display: str):
        self.digit_display = display
        print(f"Service received ten key display: {display}")
                 
    def get_digit_display(self):
        out = self.digit_display
        return out
    
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
            'Return': (CalculatorInput.RETURN, None),
            'Sqrt': (CalculatorInput.FUNCTION, MathFunction.SQRT),
            'Power': (CalculatorInput.FUNCTION, MathFunction.POWER),
            '(': (CalculatorInput.RETURN, None),
            ')': (CalculatorInput.RETURN, None)
        }