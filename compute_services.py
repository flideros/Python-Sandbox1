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
                elif token == 'Sqrt':
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
            if func_name == 'Sqrt':
                func = self.sqrt_func
            else:
                raise ValueError(f"Unknown function: {func_name}")
            return Function(expression=sub_expr, function=func), index

        expr_tree, _ = parse_inner(tokens, 0)
        return expr_tree
    
    def sqrt_func(self, x: str) -> str:
        print(f"x: {x}")
        return '\\\\sqrt({x})'
    
    def receive_ten_key_display(self, display: str):
        self.digit_display = display
    
    def add_parentheses_if_needed(self, text):
        # Check if the string contains a plus or minus sign
        if re.search(r'[+-/*]', text):
            # Add parentheses around the string
            text = f'({text})'
        return text
    
    def replace_sqrt(self,exp):       
        # Define a function to replace sqrt recursively        
        def replace(match):
            inner_exp = match.group(1)
            # Replace nested sqrt inside the current match r'sqrt(\((.*?)\))'
            nested_exp = re.sub(r'sqrt(\((.*?)\))', replace, inner_exp)
            #nested_exp = re.sub(r'sqrt\(([^()]+)\)', replace, inner_exp)
            return f'sqrt{{\\({nested_exp}\\)}}'
        
        # Replace all sqrt expressions, including nested ones
        #while re.search(r'sqrt\(([^()]+)\)', exp):
            #exp = re.sub(r'sqrt\(([^()]+)\)', replace, exp)
        while re.search(r'sqrt(\((.*?)\))', exp):
            exp = re.sub(r'sqrt\((.*?)\)', replace, exp)
            
        return exp
    
    def get_digit_display(self):
        out = self.digit_display        
        return out
    
    def preprocess_expression(self,expression:str) -> str:
        # Function to replace the matched pattern with the captured number
        def replace_with_number(match):
            return match.group(1)
        # Regular expression to extract the number within the last set of curly braces
        pattern1 = r"\\\\class\{result-box\}\{(-?\d+)\}" # Integer
        pattern2 = r"\\\\class\{result-box\}\{(-?\d+/-?\d+)\}" # Fraction
        pattern3 = r"\\\\class\{result-box\}\{(-?\d+\.\d+)\}" # Decimal
        
        pattern4 = r"\\\\class\{result-box\}\{((.*?)\))\}" # other
        
        # Insert multiplication between number and parenthesis to allow implicit multiplication
        pattern5 = r'(\d)(\()' # Group 1: digit, Group 2: open parenthesis
        pattern6 = r'(\))(\d)' # Group 1: close parenthesis, Group 2: digit
        pattern7 = r'(\))(\()' # Group 1: close parenthesis, Group 2: open parenthesis
        pattern8 = r'(\d)(sqrt)' # Group 1: digit, Group 2: 'sqrt'
        pattern9 = r'(\))(sqrt)' # Between close parenthesis and sqrt
        
        patternA = r'\1*\2' # Insert multiplication
        # Process expression with patterns 
        processed_expression = re.sub(pattern1, replace_with_number, expression)
        processed_expression = re.sub(pattern2, replace_with_number, processed_expression)
        processed_expression = re.sub(pattern3, replace_with_number, processed_expression)        
        processed_expression = re.sub(pattern4, replace_with_number, processed_expression)
        processed_expression = re.sub(pattern5, patternA, processed_expression)
        processed_expression = re.sub(pattern6, patternA, processed_expression)
        processed_expression = re.sub(pattern7, patternA, processed_expression)
        processed_expression = re.sub(pattern8, patternA, processed_expression)
        processed_expression = re.sub(pattern9, patternA, processed_expression)        
        return processed_expression
    
    def get_decimal_value(self, expression):
        exp = self.preprocess_expression(expression)
        expr = sp.sympify(exp)
        return str(expr.evalf())
    
    def simplify_expression(self, expression):
        exp = self.preprocess_expression(expression)
        return sp.sympify(exp)

    def add_backslashes(self,exp):
        exp = re.sub(r'(?<!\\)sqrt', r'\\\\sqrt', exp)       
        return exp
    
    def get_mixed_number(self, expression: str):
        try:
            print("Expression received:", expression)
            exp = sp.sympify(expression)
            print("Sympified expression:", exp)
            
            # Convert the expression to a string to replace sqrt and fractions
            result = str(exp)            
            # Function to convert fraction to mixed number
            def to_mixed_fraction(match):
                numerator = int(match.group(1))
                denominator = int(match.group(2))
                integer = numerator // denominator
                remainder = numerator % denominator
                if integer != 0 and remainder != 0:
                    return f"{integer} \\\\frac{{{remainder}}}{{{denominator}}}"
                elif integer != 0:
                    return f"{integer}"
                else: return f"\\\\frac{{{numerator}}}{{{denominator}}}"            
            def format_sqrt(exp):                
                # Format the innermost sqrt first
                def replacer(match):
                    return f"sqrt{{{(match.group(1))}}}"
                # Apply the replacement recursively for nested sqrt
                while 'sqrt(' in exp:
                    exp = re.sub(r'sqrt\(([^()]+)\)', replacer, exp)
                if len(exp) > 5 and exp[5] == '\\frac':
                    print("test")
                    return exp
                exp = re.sub(r'sqrt(\(([^()]+)\))', r'sqrt{\(\1\)}', exp)
                return exp
            
            # Handle '**' by replacing it with '^{}
            result = re.sub(r'(.*?)\*\*\(([^)]+)\)', r'\1^{{{\(\2\)}}}', result)
            # Handle square root expressions: sqrt(anything)
            result = format_sqrt(result)
            # Replace '/' with '\frac{{{}}}' in the entire result
            result = re.sub(r'(\d+)/(\d+)', to_mixed_fraction, result)
            result = re.sub(r'(\d+)/(\((.*?)\))', r'\\\\frac{{{\1}}}{{{\2}}}', result)
            result = re.sub(r'(\((.*?)\))/(\d+)', r'\\\\frac{{{\1}}}{{{\2}}}', result)                          
            #result = re.sub(r'([^/]+)/([^/]+)', r'\\\\frac{{{\1}}}{{{\2}}}', result)                        
            # Handle square root expressions: sqrt(anything)
            result = format_sqrt(result)                          
              
            # Handle mixed numbers
            if 'sqrt' not in result and 'I' not in result:
                try:
                    fraction = sp.Rational(exp)
                    abs_numerator = abs(fraction.numerator)
                    numerator = fraction.numerator
                    denominator = fraction.denominator
                    integer = abs_numerator // denominator  # Integer division
                    remainder = abs_numerator % denominator
                    
                    print(f"Numerator: {numerator}, Denominator: {denominator}, Integer: {integer}, Remainder: {remainder}")

                    if numerator < 0:
                        integer = -integer
                    if integer == 0 and numerator < 0:
                        remainder = -remainder

                    if integer == 0 and remainder == 0:
                        result = "0"
                    elif integer == 0 and remainder != 0:
                        result = f"\\\\frac{{{remainder}}}{{{denominator}}}"
                    elif integer != 0 and remainder == 0:
                        result = f"{integer}"
                    elif integer != 0 and remainder != 0:
                        result = f"{integer} \\\\frac{{{remainder}}}{{{denominator}}}"
                    print("Mixed number handled: result =", result)
                except Exception as e:
                    result = result
            
            # Return a decimal number if a decimal seperator is present.
            if '.' in (str(exp)):
                result = str(exp.evalf(10)).rstrip('0').rstrip('.')
            
            print(f"----final result: {result}")
        except Exception as e:
            print(f"----error: {e} ")
            result = " "  # or str(e)
        
        result = self.add_backslashes(result)
        return result

    
    def get_display_from_state(self, error_msg: str):
        """
        Returns the display strings based on the current state of the computation.
        """
        def format_(exp:str) -> str:
            exp = self.replace_sqrt(exp)            
            exp = exp.replace('*','\\\\times').replace('/','\\\\div').replace('I',' I').replace('sqrt','\\sqrt')            
            def format_outer_sqrt(exp):
                # Step 1: Remove existing backslashes
                exp = exp.replace(r'\\\\', '')
                exp = exp.replace(r'\\', '')            
                # Step 2: Format only the outer sqrt content
                exp = re.sub(r'sqrt(\((.*?)\))', r'sqrt{\(\1\)}', exp)            
                # Step 3: Add the backslashes back in and ensure all parts are correctly enclosed
                exp = exp.replace('sqrt', r'\\sqrt').replace('times', r'\\times').replace('class', r'\\class').replace('div', r'\\div')            
                exp = re.sub(r'\\\\\\', r'\\\\', exp)
                return exp
            return format_outer_sqrt(exp)
        
        def inner(calculator_state) -> str:
            if isinstance(calculator_state, StartStateData):                
                return (self.digit_display, " ")
            
            elif isinstance(calculator_state, NumberInputStateData):                
                if calculator_state.stack is not None and len(calculator_state.stack) > 0:
                    _state, exp = calculator_state.stack[0]
                    expression = evaluate_expression(exp)
                    expression_out = expression#[:-len(calculator_state.stack)]
                else:
                    expression = evaluate_expression(calculator_state.expression_tree)
                    expression_out = expression
                ex = self.preprocess_expression(expression)
                result = self.get_mixed_number(ex)                
                print(expression_out)
                return (format_(expression_out),result.replace('*','\\\\cdot'))
            
            elif isinstance(calculator_state, OperatorInputStateData):
                if calculator_state.stack is not None and len(calculator_state.stack) > 0:
                    _state, exp = calculator_state.stack[0]
                    expression = evaluate_expression(exp)
                    expression_out = expression[:-len(calculator_state.stack)]
                else:
                    expression_out = evaluate_expression(calculator_state.expression_tree) 
                result = " "                
                return (format_(expression_out),result.replace('*','\\\\cdot'))
            
            elif isinstance(calculator_state, ResultStateData):
                return (" ", None)
            
            elif isinstance(calculator_state, ParenthesisOpenStateData):
                if calculator_state.stack is not None and len(calculator_state.stack) > 0:
                    _state, exp = calculator_state.stack[0]
                    expression = evaluate_expression(exp)
                    expression_out = expression[:-len(calculator_state.stack)]
                else:
                    expression_out = evaluate_expression(calculator_state.expression_tree)
                ex = self.preprocess_expression(expression_out)
                result = self.get_mixed_number(ex)                
                return (format_(expression_out),result.replace('*','\\\\cdot'))
            
            elif isinstance(calculator_state, FunctionInputStateData):
                if calculator_state.stack is not None and len(calculator_state.stack) > 0:
                    _state, exp = calculator_state.stack[0]
                    expression = evaluate_expression(exp)
                    expression_out = expression[:-len(calculator_state.stack)]                    
                else:
                    expression_out = evaluate_expression(calculator_state.expression_tree)
                ex = self.preprocess_expression(expression_out)                
                result = self.get_mixed_number(ex)
                print(expression_out)
                return (format_(expression_out),result.replace('*','\\\\cdot'))
                
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
            'Plus': (CalculatorInput.MATHOP, CalculatorMathOp.ADD),
            'Minus': (CalculatorInput.MATHOP, CalculatorMathOp.SUBTRACT),
            'Times': (CalculatorInput.MATHOP, CalculatorMathOp.MULTIPLY),
            'Divide by': (CalculatorInput.MATHOP, CalculatorMathOp.DIVIDE),
            'Return': (CalculatorInput.RETURN, None),
            'Sqrt': (CalculatorInput.FUNCTION, MathFunction.SQRT),
            'Power': (CalculatorInput.FUNCTION, MathFunction.POWER),
            '(': (CalculatorInput.PARENOPEN, None),
            ')': (CalculatorInput.PARENCLOSE, None)
        }