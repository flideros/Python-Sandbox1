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
            if isinstance(state, FunctionInputStateData):
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
        return(f"sqrt({x})")
    
    def power_func(self, x: str) -> str:        
        return(f"**({x})")
    
    def receive_ten_key_display(self, display: str):
        self.digit_display = display
    
    def get_digit_display(self):
        out = self.digit_display        
        return out
    
    def add_parentheses_if_needed(self, text): 
        if re.search(r'[/*+-]', text):
            # Add parentheses around the string
            text = f'({text})'
        return text
            
    def replace_sqrt(self, exp):
        def replace_all_sqrt(exp):
            pattern = re.compile(r'sqrt\(([^()]*)\)')
            while 'sqrt(' in exp:
                matches = list(pattern.finditer(exp))
                if not matches:
                    break
                for match in matches:
                    start = match.start()
                    end = match.end()
                    inner_exp = match.group(1)
                    exp = exp[:start] + f'sqrt{{{inner_exp}}}' + exp[end:]
            return exp
        
        def find_balanced_parentheses(s, start_index):
            stack = []
            end_index = start_index
            for index in range(start_index, len(s)):
                if s[index] == '(':
                    stack.append(index)
                elif s[index] == ')':
                    if stack:
                        stack.pop()
                    if not stack:
                        end_index = index + 1
                        break
            return s[start_index:end_index], end_index

        def replace_balanced_sqrt(exp):
            while True:
                start_index = exp.find('sqrt(')
                if start_index == -1:
                    break
                open_paren = 0
                for i in range(start_index + 5, len(exp)):
                    if exp[i] == '(':
                        open_paren += 1
                    elif exp[i] == ')':
                        if open_paren == 0:
                            inner_exp = exp[start_index + 5:i]
                            replaced_inner_exp = replace_all_sqrt(inner_exp)
                            exp = exp[:start_index] + f'sqrt{{{replaced_inner_exp}}}' + exp[i+1:]
                            break
                        else:
                            open_paren -= 1
            return exp
        
        return replace_balanced_sqrt(exp)
    
    def replace_power(self, exp):
        def replace_recursive(exp):
            pattern_nested = re.compile(r'(\S+)\*\*\((.*?)\)')
            while pattern_nested.search(exp):
                exp = pattern_nested.sub(lambda match: f'{match.group(1)}^{{{replace_recursive(match.group(2))}}}', exp)
            return exp
        
        # Handle basic powers like `x**2`
        exp = re.sub(r'(\S+)\*\*(\d+)', r'\1^{{{\2}}}', exp)        
        # Handle nested exponents recursively
        exp = replace_recursive(exp)        
        # Final pass to handle any remaining cases
        exp = re.sub(r'(\S+)\*\*\(([^)]+)\)', r'\1^{{{\2}}}', exp)        
        
        return exp
    
    def preprocess_expression(self,expression:str) -> str:
        # Function to replace the matched pattern with the captured number
        def replace_with_number(match):
            return match.group(1)
        expression = expression.replace('.-','.0-').replace('.+','.0+').replace('.*','.0*').replace('./','.0/')
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
        pattern10 =r'(\d)\.(\D)' # Group 1: digit, Group 2: non-digit (assume implicitly decimal number)
        
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
        processed_expression = re.sub(pattern10, patternA, processed_expression)
        
        return processed_expression
    
    def get_decimal_value(self, expression):
        exp = self.preprocess_expression(expression)
        try:
            expr = sp.sympify(exp)
            return str(expr.evalf())
        except Exception as e:
            print(f"get_decimal_value----error: {e} ")
            result = exp  # or str(e)
    def simplify_expression(self, expression):
        try:
            exp = self.preprocess_expression(expression)
            result = sp.sympify(exp)
        except Exception as e:
            print(f"simplify_expression----error: {e} ")
            result = exp  # or str(e)
        
        return result
    
    def get_mixed_number(self, expression: str):
        try:            
            exp = sp.sympify(expression)           
            
            # Convert the SymPy expression to LaTeX with double backslashes for keywords
            result = sp.latex(exp, mode='equation').replace('\\', '\\\\')
            
            # Handle mixed numbers
            if 'sqrt' not in result and 'I' not in result:                
                try:
                    fraction = sp.Rational(exp)
                    abs_numerator = abs(fraction.numerator)
                    numerator = fraction.numerator
                    denominator = fraction.denominator
                    integer = abs_numerator // denominator  # Integer division
                    remainder = abs_numerator % denominator
                    
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
                except Exception as e:
                    result = result
                    
            # Return a decimal number if a decimal seperator is present.
            if '.' in (str(exp)):
                result = str(exp.evalf(15)).rstrip('0').rstrip('.')

        except Exception as e:
            print(f"get_mixed_number----error: {e} ")
            result = expression  # or str(e)
        
        return result
    
    def get_stack_count_from_state(self, calculator_state) -> int:        
        if isinstance(calculator_state, StartStateData):
            return 0            
        elif isinstance(calculator_state, NumberInputStateData):                
            return len(calculator_state.stack)            
        elif isinstance(calculator_state, OperatorInputStateData):
            return len(calculator_state.stack)            
        elif isinstance(calculator_state, ResultStateData):
            return 0            
        elif isinstance(calculator_state, ParenthesisOpenStateData):
            return len(calculator_state.stack)            
        elif isinstance(calculator_state, FunctionInputStateData):
            return len(calculator_state.stack)                
        elif isinstance(calculator_state, ErrorStateData):
            return 0      
    
    def get_display_from_state(self, error_msg: str):
        """
        Returns the display strings based on the current state of the computation.
        """
        def format_(exp:str) -> str:                   
            # Handle '**' by replacing it with '^{}                       
            exp = self.replace_power(exp)
            
            exp = exp.replace('.-','.0-').replace('.+','.0+').replace('.*','.0*').replace('./','.0/')
            exp = exp.replace('*','\\\\times').replace('/','\\\\div').replace('I',' I').replace('sqrt','\\\\sqrt')            
            return exp 
        
        def inner(calculator_state) -> str:
            if isinstance(calculator_state, StartStateData):                
                return (self.digit_display, " ")
            
            elif isinstance(calculator_state, NumberInputStateData):                
                if calculator_state.stack is not None and len(calculator_state.stack) > 0:
                    _state, exp = calculator_state.stack[0]                    
                    expression = evaluate_expression(exp)                                        
                else:                    
                    expression = evaluate_expression(calculator_state.expression_tree)                                        
                ex = self.preprocess_expression(expression)
                expression_out = self.replace_sqrt(ex)
                result = self.get_mixed_number(ex)
                result = self.replace_sqrt(result)
                return (format_(expression_out),result.replace('I',' I').replace('*','\\\\cdot '))
            
            elif isinstance(calculator_state, OperatorInputStateData):
                if calculator_state.stack is not None and len(calculator_state.stack) > 0:
                    _state, exp = calculator_state.stack[0]                    
                    expression = evaluate_expression(exp)
                    expression = self.preprocess_expression(expression)
                    expression_out = expression
                    expression_out = self.replace_sqrt(expression_out)
                else:
                    expression_out = evaluate_expression(calculator_state.expression_tree)
                    expression_out = self.preprocess_expression(expression_out)
                    expression_out = self.replace_sqrt(expression_out)
                result = " "                
                return (format_(expression_out),result)
            
            elif isinstance(calculator_state, ResultStateData):
                return (" ", None)
            
            elif isinstance(calculator_state, ParenthesisOpenStateData):
                if calculator_state.stack is not None and len(calculator_state.stack) > 0:
                    _state, exp = calculator_state.stack[0]
                    expression = evaluate_expression(exp)
                    expression_out = expression#[:-len(calculator_state.stack)]                    
                else:
                    expression_out = evaluate_expression(calculator_state.expression_tree)                    
                    print(f"Expression Out: {expression_out}")
                ex = self.preprocess_expression(expression_out)
                if ex[-2:] == '()':
                    result = " "
                else: 
                    result = self.get_mixed_number(ex)
                    result = self.replace_sqrt(result)
                expression_out = self.replace_sqrt(ex)
                return (format_(expression_out),result.replace('I',' I').replace('times','cdot ').replace('*','\\\\cdot '))
            
            elif isinstance(calculator_state, FunctionInputStateData):
                if calculator_state.stack is not None and len(calculator_state.stack) > 0:
                    _state, exp = calculator_state.stack[0]
                    expression = evaluate_expression(exp)
                    expression_out = expression                   
                else:
                    expression_out = evaluate_expression(calculator_state.expression_tree)                    
                ex = self.preprocess_expression(expression_out)                
                expression_out = self.replace_sqrt(ex)
                result = " "                
                return (format_(expression_out),result)
                
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