# ================================================
# Compute Services
# ================================================
from typing import Optional, Tuple, Union, Dict, Callable, List
from calculator_domain import (Expression, Value, Operator, Parenthesis, Function, Compound, CalculatorInput, Number, CalculatorMathOp,
                               ErrorStateData, StartStateData,  NumberInputStateData, MathFunction, evaluate_expression,
                               OperatorInputStateData, ResultStateData, ParenthesisOpenStateData, FunctionInputStateData)
import re
import math
import sympy as sp

class ComputeServices:    
    def __init__(self):
        super().__init__()
        self.digit_display = " "
    
    def handle_return(self,state) -> bool:
        def inner(state) -> bool:            
            if isinstance(state, ResultStateData):
                return True            
            else:
                return False
        return inner(state)
    
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
    
    def receive_ten_key_display(self, display: str):
        self.digit_display = display
        print(f"Service received ten key display: {display}")
                 
    def get_digit_display(self):
        out = self.digit_display
        return out
    
    def preprocess_expression(self,expression:str) -> str:
        # Insert multiplication between number and parenthesis to allow implicit multiplication
        processed_expression = re.sub(r'(\d)(\()', r'\1*\2', expression)
        processed_expression = re.sub(r'(\))(\d)', r'\1*\2', processed_expression)
        return processed_expression
    
    def get_decimal_value(self, expression):
        exp = self.preprocess_expression(expression)
        expr = sp.sympify(exp)
        return str(expr.evalf())
    
    def simplify_expression(self, expression):
        exp = self.preprocess_expression(expression)
        return sp.sympify(exp)
    
    def get_display_from_state(self, error_msg: str):
        """
        Returns the display strings based on the current state of the computation.
        """
        def format_(exp:str) -> str:
            return exp.replace('*','\\\\times').replace('/','\\\\div')
        
        def inner(calculator_state) -> str:
            if isinstance(calculator_state, StartStateData):
                return (self.digit_display, " ")
            
            elif isinstance(calculator_state, NumberInputStateData):                
                if calculator_state.stack is not None and len(calculator_state.stack) > 0:
                    _state, exp = calculator_state.stack[0]
                    expression = evaluate_expression(exp)
                    expression_out = expression[:-len(calculator_state.stack)]
                else:
                    expression = evaluate_expression(calculator_state.expression_tree)
                    expression_out = expression
                ex = self.preprocess_expression(expression)
                try:                    
                    exp = sp.sympify(ex)
                    expr = sp.Rational(exp)
                    integer = expr // 1 # Integer division
                    fraction = expr - integer
                    numerator = fraction.numerator
                    denominator = fraction.denominator
                    if '.' in (str(exp)):
                        result = str(exp.evalf(10)).rstrip('0').rstrip('.')
                    else:                        
                        if integer == 0 and fraction == 0:
                            result = "0"
                        elif integer == 0 and fraction != 0: 
                            result = f"\\\\frac{{{numerator}}}{{{denominator}}}"
                        elif integer != 0 and fraction == 0:
                            result = f"{integer}"
                        elif integer != 0 and fraction != 0:
                            result = f"{integer} \\\\frac{{{numerator}}}{{{denominator}}}"                            
                    print(result)
                except Exception as e:
                    result = (str(e))                
                return (format_(expression_out),result)
            
            elif isinstance(calculator_state, OperatorInputStateData):
                if calculator_state.stack is not None and len(calculator_state.stack) > 0:
                    _state, exp = calculator_state.stack[0]
                    expression = evaluate_expression(exp)
                    expression_out = expression[:-len(calculator_state.stack)]
                else:
                    expression_out = evaluate_expression(calculator_state.expression_tree) 
                result = " "                
                return (format_(expression_out),result)
            
            elif isinstance(calculator_state, ResultStateData):
                return (" ",None)
            
            elif isinstance(calculator_state, ParenthesisOpenStateData):
                if calculator_state.stack is not None and len(calculator_state.stack) > 0:
                    _state, exp = calculator_state.stack[0]
                    expression = evaluate_expression(exp)
                    expression_out = expression[:-len(calculator_state.stack)]
                else:
                    expression_out = evaluate_expression(calculator_state.expression_tree)
                ex = self.preprocess_expression(expression_out)
                try:                    
                    exp = sp.sympify(ex)
                    expr = sp.Rational(exp)
                    integer = expr // 1 # Integer division
                    fraction = expr - integer
                    numerator = fraction.numerator
                    denominator = fraction.denominator
                    if '.' in (str(exp)):
                        result = str(exp.evalf(10)).rstrip('0').rstrip('.')
                    else:                        
                        if integer == 0 and fraction == 0:
                            result = "0"
                        elif integer == 0 and fraction != 0: 
                            result = f"\\\\frac{{{numerator}}}{{{denominator}}}"
                        elif integer != 0 and fraction == 0:
                            result = f"{integer}"
                        elif integer != 0 and fraction != 0:
                            result = f"{integer} \\\\frac{{{numerator}}}{{{denominator}}}"                
                except Exception as e:
                    result = " "                
                return (format_(expression_out),result)
            
            elif isinstance(calculator_state, FunctionInputStateData):
                return (calculator_state.expression_tree, None)
                
            elif isinstance(calculator_state, ErrorStateData):
                return (error_msg + calculator_state.math_error.value, None)
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
            '(': (CalculatorInput.PARENOPEN, None),
            ')': (CalculatorInput.PARENCLOSE, None)
        }