# ================================================
# Implementation of Calculator
# ================================================
from typing import Optional, Tuple, Union, Callable
from calculator_domain import (
    AccumulatorStateData, ZeroStateData, ComputedStateData, ErrorStateData, MathOperationError,
    CalculatorInput, CalculatorMathOp, NonZeroDigit, DigitAccumulator, PendingOp, CalculatorState,
    StartStateData,  NumberInputStateData, OperatorInputStateData, ResultStateData, evaluate_expression,
    ParenthesisOpenStateData, FunctionInputStateData, Compound, Value, Operator, Parenthesis
)
from calculator_services import CalculatorServices
from compute_services import ComputeServices
from dataclasses import dataclass, field
import re

def create_compute(services: ComputeServices)-> Callable[[CalculatorState, CalculatorInput, str], CalculatorState]: 
    
    def handle_start_state(state_data: StartStateData, input) -> CalculatorState: 
        
        if input == CalculatorInput.ZERO:
            print("Zero Input - Transition to NumberInputState")
            digits = services.get_digit_display()
            value = Value(value=digits)            
            return NumberInputStateData(current_value = digits,
                                        expression_tree = Compound([value]),
                                        memory = " ")
        
        elif isinstance(input, tuple):
            input_type, _input_value = input
            input_value = _input_value.value
        
            if input_type == 'DIGIT' and input_value in range(1, 10):
                print("Digit Input - Transition to NumberInputState")
                digits = services.get_digit_display()
                value = Value(value=digits)                
                return NumberInputStateData(current_value = digits,
                                            expression_tree = Compound([value]),
                                            memory = " ")
            
            elif input_type == 'MATHOP':   
                if _input_value == CalculatorMathOp.SUBTRACT:                    
                    operator_expr = Operator(operator='-')
                    new_tree = Compound([operator_expr])
                    print(f"{new_tree}")
                    return OperatorInputStateData(previous_value = ' ',
                                                  operator = '-',
                                                  current_value = ' ',
                                                  expression_tree = new_tree,
                                                  memory = " ")
                
        elif input == CalculatorInput.PARENOPEN:
            print("Parenthesis Open Input - Transition to ParenthesisOpenState")
            new_compound = Compound([])            
            new_tree = Compound([Parenthesis(new_compound)])
            new_stack = [(state_data,new_tree)]
            return ParenthesisOpenStateData(inner_expression = "(",                                        
                                            expression_tree = new_compound,
                                            memory = " ",
                                            stack = new_stack)
        
        return state_data  # Return the current state if no condition matches    
    
    def handle_number_input_state(state_data: NumberInputStateData, input) -> CalculatorState:
        if input == CalculatorInput.ZERO:
            print("Zero Input - Stay in NumberInputState")
            digits = services.get_digit_display()
            value = Value(value=digits)
            if isinstance(state_data.expression_tree.expressions[-1], Value):
                state_data.expression_tree.expressions[-1] =  value            
            return NumberInputStateData(current_value = digits,
                                        expression_tree = state_data.expression_tree,
                                        memory = state_data.memory,
                                        stack = state_data.stack)
        
        elif isinstance(input, tuple):
            input_type, _input_value = input
            input_value = _input_value.value
        
            if input_type == 'DIGIT' and input_value in range(1, 10):
                print("Digit Input - Stay in NumberInputState")
                digits = services.get_digit_display()
                value = Value(value=digits)
                if isinstance(state_data.expression_tree.expressions[-1], Value):
                    state_data.expression_tree.expressions[-1] = value                
                return NumberInputStateData(current_value = digits,
                                            expression_tree = state_data.expression_tree,
                                            memory = state_data.memory,
                                            stack = state_data.stack)
            
            elif input_type == 'MATHOP':   
                print("Math Operation Input - Transition to OperatorInputState")
                if _input_value == CalculatorMathOp.SUBTRACT:                    
                    operator_expr = Operator(operator='-')
                    #if not state_data.stack:
                    previous = evaluate_expression(state_data.expression_tree)
                    state_data.expression_tree.expressions.append(operator_expr)                    
                    return OperatorInputStateData(previous_value = previous,
                                                  operator = '-',
                                                  current_value = ' ',
                                                  expression_tree = state_data.expression_tree,
                                                  memory = state_data.memory,
                                                  stack = state_data.stack)
                elif _input_value == CalculatorMathOp.ADD:                    
                    operator_expr = Operator(operator='+')
                    #if not state_data.stack:
                    previous = evaluate_expression(state_data.expression_tree)
                    state_data.expression_tree.expressions.append(operator_expr)                     
                    return OperatorInputStateData(previous_value = previous,
                                                  operator = '+',
                                                  current_value = ' ',
                                                  expression_tree = state_data.expression_tree,
                                                  memory = state_data.memory,
                                                  stack = state_data.stack)
                elif _input_value == CalculatorMathOp.MULTIPLY:                    
                    operator_expr = Operator(operator='*')
                    previous = evaluate_expression(state_data.expression_tree)
                    state_data.expression_tree.expressions.append(operator_expr)                     
                    return OperatorInputStateData(previous_value = previous,
                                                  operator = '*',
                                                  current_value = ' ',
                                                  expression_tree = state_data.expression_tree,
                                                  memory = state_data.memory,
                                                  stack = state_data.stack)
                elif _input_value == CalculatorMathOp.DIVIDE:                    
                    operator_expr = Operator(operator='/')
                    #if not state_data.stack:
                    previous = evaluate_expression(state_data.expression_tree)
                    state_data.expression_tree.expressions.append(operator_expr)                     
                    return OperatorInputStateData(previous_value = previous,
                                                  operator = '/',
                                                  current_value = ' ',
                                                  expression_tree = state_data.expression_tree,
                                                  memory = state_data.memory,
                                                  stack = state_data.stack)
            
        elif input == CalculatorInput.RETURN:
            print("Return Input - Transition to ResultState") 
            # Check if there is a result then return result state.
            if state_data.stack is not None and len(state_data.stack) > 0:
                _state, exp = state_data.stack[0]
                expr = evaluate_expression(exp)
                expression = str(services.simplify_expression(expr))    
            else:
                expr = evaluate_expression(state_data.expression_tree)
                expression = str(services.simplify_expression(expr))
            result = services.get_decimal_value(expression).rstrip('0').rstrip('.')
            if '.' in expression:
                memo = result
            else:
                memo = expression                
            return ResultStateData(result = result,
                                   memory = memo)
    
        elif input == CalculatorInput.PARENOPEN:
            print("Parenthesis Open Input - Transition to ParenthesisOpenState")
            new_compound = Compound([])            
            state_data.expression_tree.expressions.append(Parenthesis(new_compound))             
            if state_data.stack is not None:
                state_data.stack.append((state_data,state_data.expression_tree))
            else:
                state_data.stack = [(state_data,state_data.expression_tree)]
            print(f'new stack {state_data.stack}')
            new_inner_expression = evaluate_expression(state_data.expression_tree)
            return ParenthesisOpenStateData(inner_expression = new_inner_expression,                                        
                                            expression_tree = new_compound,
                                            memory = state_data.memory,
                                            stack = state_data.stack)
        
        elif input == CalculatorInput.PARENCLOSE:
            print("Parenthesis Close Input - Transition to ParenthesisOpenState") # ToDo: consider changing this to Parenthesis State
            if len(state_data.stack) == 0:
                return state_data
            previous_state_data, previous_expression_tree = state_data.stack.pop()                         
            state_data.expression_tree = previous_expression_tree            
            new_inner_expression = evaluate_expression(state_data.expression_tree)
            return ParenthesisOpenStateData(inner_expression = new_inner_expression,                                        
                                            expression_tree = state_data.expression_tree,
                                            memory = state_data.memory,
                                            stack = state_data.stack)        
        
        return state_data  # Return the current state if no condition matches
    
    def handle_operator_input_state(state_data: OperatorInputStateData, input) -> CalculatorState:
        
        if input == CalculatorInput.ZERO:
            print("Zero Input - Transition to NumberInputState")
            digits = services.get_digit_display()
            value = Value(value=digits)              
            state_data.expression_tree.expressions.append(value)
            return NumberInputStateData(current_value = digits,
                                        expression_tree = state_data.expression_tree,
                                        memory = state_data.memory,
                                        stack = state_data.stack)
        
        elif isinstance(input, tuple):
            input_type, _input_value = input
            input_value = _input_value.value
        
            if input_type == 'DIGIT' and input_value in range(1, 10):
                print("Digit Input - Transition to NumberInputState")
                digits = services.get_digit_display()
                value = Value(value=digits)
                state_data.expression_tree.expressions.append(value)
                print(f"Digit Input {digits}")
                return NumberInputStateData(current_value = value,
                                            expression_tree = state_data.expression_tree,
                                            stack = state_data.stack,
                                            memory = state_data.memory)
            
            elif input_type == 'MATHOP':   
                print("Math Operation Input - Transition to OperatorInputState")
                if _input_value == CalculatorMathOp.SUBTRACT:                    
                    
                    operator_expr = Operator(operator='-')
                    #if not state_data.stack:
                    previous = evaluate_expression(state_data.expression_tree)
                    state_data.expression_tree.expressions.append(operator_expr)                    
                    return OperatorInputStateData(previous_value = previous,
                                                  operator = '-',
                                                  current_value = ' ',
                                                  expression_tree = state_data.expression_tree,
                                                  memory = state_data.memory,
                                                  stack = state_data.stack)
        
        elif input == CalculatorInput.PARENOPEN:
            print("Parenthesis Open Input - Transition to ParenthesisOpenState")
            new_compound = Compound([])            
            state_data.expression_tree.expressions.append(Parenthesis(new_compound))             
            if state_data.stack is not None:
                state_data.stack.append((state_data,state_data.expression_tree))
            else:
                state_data.stack = [(state_data,state_data.expression_tree)]
            print(f'new stack {state_data.stack}')
            new_inner_expression = evaluate_expression(state_data.expression_tree)
            return ParenthesisOpenStateData(inner_expression = new_inner_expression,                                    
                                            expression_tree = new_compound,
                                            memory = state_data.memory,
                                            stack = state_data.stack)
        
        return state_data  # Return the current state if no condition matches
    
    def handle_parenthesis_open_state(state_data: ParenthesisOpenStateData, input) -> CalculatorState:
        
        if input == CalculatorInput.ZERO:
            print("Zero Input - Transition to NumberInputState")
            digits = services.get_digit_display()
            value = Value(value=digits)
            state_data.expression_tree.expressions.append(value)
            return NumberInputStateData(current_value = digits,
                                        expression_tree = state_data.expression_tree,
                                        memory = state_data.memory,
                                        stack = state_data.stack)
        
        elif isinstance(input, tuple):
            input_type, _input_value = input
            input_value = _input_value.value
        
            if input_type == 'DIGIT' and input_value in range(1, 10):
                print("Digit Input - Stay in NumberInputState")
                digits = services.get_digit_display()
                value = Value(value=digits)
                state_data.expression_tree.expressions.append(value)
                return NumberInputStateData(current_value = digits,
                                            expression_tree = state_data.expression_tree,
                                            memory = state_data.memory,
                                            stack = state_data.stack)
            
            elif input_type == 'MATHOP':   
                if _input_value == CalculatorMathOp.SUBTRACT:                    
                    operator_expr = Operator(operator='-')
                    previous = evaluate_expression(state_data.expression_tree)
                    state_data.expression_tree.expressions.append(operator_expr)
                    return OperatorInputStateData(previous_value = previous,
                                                  operator = '-',
                                                  current_value = ' ',
                                                  expression_tree = state_data.expression_tree,
                                                  memory = state_data.memory,
                                                  stack = state_data.stack)
                elif _input_value == CalculatorMathOp.ADD:                    
                    if state_data.inner_expression == '(':
                        return state_data
                    if len(state_data.stack) > 0 and state_data.inner_expression[-2:] == '()':
                        return state_data                    
                    operator_expr = Operator(operator='+')
                    #if not state_data.stack:
                    previous = evaluate_expression(state_data.expression_tree)
                    state_data.expression_tree.expressions.append(operator_expr)                     
                    return OperatorInputStateData(previous_value = previous,
                                                  operator = '+',
                                                  current_value = ' ',
                                                  expression_tree = state_data.expression_tree,
                                                  memory = state_data.memory,
                                                  stack = state_data.stack)
                elif _input_value == CalculatorMathOp.MULTIPLY:                    
                    if state_data.inner_expression == '(':
                        return state_data
                    if len(state_data.stack) > 0 and state_data.inner_expression[-2:] == '()':
                        return state_data                    
                    operator_expr = Operator(operator='*')
                    previous = evaluate_expression(state_data.expression_tree)
                    state_data.expression_tree.expressions.append(operator_expr)                     
                    return OperatorInputStateData(previous_value = previous,
                                                  operator = '*',
                                                  current_value = ' ',
                                                  expression_tree = state_data.expression_tree,
                                                  memory = state_data.memory,
                                                  stack = state_data.stack)
                elif _input_value == CalculatorMathOp.DIVIDE:                    
                    if state_data.inner_expression == '(':
                        return state_data
                    if len(state_data.stack) > 0 and state_data.inner_expression[-2:] == '()':
                        return state_data                    
                    operator_expr = Operator(operator='/')
                    #if not state_data.stack:
                    previous = evaluate_expression(state_data.expression_tree)
                    state_data.expression_tree.expressions.append(operator_expr)                     
                    return OperatorInputStateData(previous_value = previous,
                                                  operator = '/',
                                                  current_value = ' ',
                                                  expression_tree = state_data.expression_tree,
                                                  memory = state_data.memory,
                                                  stack = state_data.stack)
                
        elif input == CalculatorInput.PARENOPEN:
            print("Parenthesis Open Input - Transition to ParenthesisOpenState")
            new_compound = Compound([])            
            state_data.expression_tree.expressions.append(Parenthesis(new_compound))             
            if state_data.stack is not None:
                state_data.stack.append((state_data,state_data.expression_tree))
            else:
                state_data.stack = [(state_data,state_data.expression_tree)]
            print(f'new stack {state_data.stack}')
            new_inner_expression = evaluate_expression(state_data.expression_tree)
            return ParenthesisOpenStateData(inner_expression = new_inner_expression[:-1],                                       
                                            expression_tree = new_compound,
                                            memory = state_data.memory,
                                            stack = state_data.stack)
        
        elif input == CalculatorInput.PARENCLOSE:
            print("Parenthesis Close Input - Transition to ParenthesisOpenState") # ToDo: consider changing this to Parenthesis State
            if len(state_data.stack) == 0:
                return state_data
            previous_state_data, previous_expression_tree = state_data.stack.pop()            
            if len(state_data.inner_expression) == 1 and state_data.inner_expression[-1] != "(":                
                state_data.expression_tree = previous_expression_tree            
                new_inner_expression = evaluate_expression(state_data.expression_tree)                
                return ParenthesisOpenStateData(inner_expression = new_inner_expression,                                        
                                                expression_tree = state_data.expression_tree,
                                                memory = state_data.memory,
                                                stack = state_data.stack)
            if len(state_data.inner_expression) > 1 and state_data.inner_expression[-2:] != "()":                
                print(f"state_data.inner_expression[-2:] is {state_data.inner_expression[-2:]}")
                state_data.expression_tree = previous_expression_tree            
                new_inner_expression = evaluate_expression(state_data.expression_tree)                
                return ParenthesisOpenStateData(inner_expression = new_inner_expression,                                        
                                                expression_tree = state_data.expression_tree,
                                                memory = state_data.memory,
                                                stack = state_data.stack)
            else:
                state_data.stack.append((previous_state_data, previous_expression_tree))
                new_inner_expression = evaluate_expression(state_data.expression_tree)
                return ParenthesisOpenStateData(inner_expression = new_inner_expression,                                        
                                                expression_tree = state_data.expression_tree,
                                                memory = state_data.memory,
                                                stack = state_data.stack)
        
        elif input == CalculatorInput.RETURN:
            print("Return Input - Transition to ResultState") 
            # Check if there is a result then return result state.
            if state_data.stack is not None and len(state_data.stack) > 0:
                _state, exp = state_data.stack[0]
                expr = evaluate_expression(exp)
                expression = str(services.simplify_expression(expr))    
            else:
                expr = evaluate_expression(state_data.expression_tree)
                expression = str(services.simplify_expression(expr))
            result = services.get_decimal_value(expression).rstrip('0').rstrip('.')
            if '.' in expression:
                memo = result
            else:
                memo = expression                
            return ResultStateData(result = result,
                                   memory = memo)
        
        return state_data  # Return the current state if no condition matches
    
    def handle_function_input_state(state_data: FunctionInputStateData, input) -> CalculatorState: pass
    
    def handle_result_state(state_data: ResultStateData, input) -> CalculatorState: 
        
        if input == CalculatorInput.ZERO:
            print("Zero Input - Transition to NumberInputState")
            digits = services.get_digit_display()
            value = Value(value=digits)            
            return NumberInputStateData(current_value = digits,
                                        expression_tree = Compound([value]),
                                        memory = state_data.memory)
        
        elif isinstance(input, tuple):
            input_type, _input_value = input
            input_value = _input_value.value
        
            if input_type == 'DIGIT' and input_value in range(1, 10):
                print("Digit Input - Transition to NumberInputState")
                digits = services.get_digit_display()
                value = Value(value=digits)                
                return NumberInputStateData(current_value = digits,
                                            expression_tree = Compound([value]),
                                            memory = state_data.memory)
            
            elif input_type == 'MATHOP':   
                if _input_value == CalculatorMathOp.SUBTRACT:                    
                    operator_expr = Operator(operator='-')
                    new_tree = Compound([operator_expr])
                    print(f"{new_tree}")
                    return OperatorInputStateData(previous_value = ' ',
                                                  operator = '-',
                                                  current_value = ' ',
                                                  expression_tree = new_tree,
                                                  memory = state_data.memory)
        
        elif input == CalculatorInput.PARENOPEN:
            print("Parenthesis Open Input - Transition to ParenthesisOpenState")
            new_compound = Compound([])            
            new_tree = Compound([Parenthesis(new_compound)])
            new_stack = [(state_data,new_tree)]
            return ParenthesisOpenStateData(inner_expression = "(",                                        
                                            expression_tree = new_compound,
                                            memory = " ",
                                            stack = new_stack)
    
        return state_data  # Return the current state if no condition matches
    
    def handle_error_state(state_data: ErrorStateData, input, memory) -> CalculatorState: pass
    
    def compute(input, state) -> Optional[CalculatorState]: 
        """
        Routes the input and state to the appropriate handler and returns the new calculator state.
        
        Args:
            input (CalculatorInput): The input received by the calculator.
            state (CalculatorState): The current state of the calculator.
            
        Returns:
            Optional[CalculatorState]: The new state of the calculator after processing the input,
            or None if the input is not handled by any state.
        """
        if isinstance(state, StartStateData):
            return handle_start_state(StartStateData, input)
        elif isinstance(state, NumberInputStateData):
            return handle_number_input_state(state, input)
        elif isinstance(state, OperatorInputStateData):
            return handle_operator_input_state(state, input)        
        elif isinstance(state, ParenthesisOpenStateData):
            return handle_parenthesis_open_state(state, input)        
        elif isinstance(state, FunctionInputStateData):
            return handle_function_input_state(state, input)        
        elif isinstance(state, ResultStateData):
            return handle_result_state(state, input)        
        elif isinstance(state, ErrorStateData):
            return handle_error_state(state, input, state.memory)
        return None

    return compute