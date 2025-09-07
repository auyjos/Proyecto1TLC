"""
Algoritmo Shunting Yard para convertir expresiones infijas a postfijas
"""
from typing import List, Optional, Tuple


def precedence(op: str):
    """Retorna la precedencia de los operadores"""
    if op in ('*', '+', '?'): return 3
    if op == '.':             return 2
    if op == '|':             return 1
    return 0


def shunting_yard(tokens, collect_steps: bool = False):
    """
    Convierte tokens en notación infija a postfija usando el algoritmo Shunting Yard
    
    Args:
        tokens: Lista de tokens en notación infija
        collect_steps: Si True, colecciona los pasos del algoritmo para debug
    
    Returns:
        tuple: (output, pasos) donde output es la lista de tokens postfijos
    """
    output, stack, pasos = [], [], []
    for token in tokens:
        if token.startswith('\\') or (len(token) == 1 and (token.isalnum() or token in ['_', '[', ']', '{', '}', 'ε'])):
            output.append(token); pasos.append((f"operand {token}", output.copy(), stack.copy())) if collect_steps else None
        elif token == '(':
            stack.append(token); pasos.append(("push (", output.copy(), stack.copy())) if collect_steps else None
        elif token == ')':
            while stack and stack[-1] != '(':
                op = stack.pop(); output.append(op)
                pasos.append(("pop for )", output.copy(), stack.copy())) if collect_steps else None
            if stack and stack[-1] == '(':
                stack.pop(); pasos.append(("pop (", output.copy(), stack.copy())) if collect_steps else None
            else:
                pasos.append(("ignore unmatched )", output.copy(), stack.copy())) if collect_steps else None
        elif token in ['|', '.', '*', '+', '?']:
            while stack and precedence(stack[-1]) >= precedence(token):
                if stack[-1] == '(': break
                op = stack.pop(); output.append(op)
                pasos.append((f"pop op {op}", output.copy(), stack.copy())) if collect_steps else None
            stack.append(token); pasos.append((f"push op {token}", output.copy(), stack.copy())) if collect_steps else None
        else:
            pasos.append((f"ignore {token}", output.copy(), stack.copy())) if collect_steps else None
    while stack:
        op = stack.pop(); output.append(op)
        pasos.append((f"pop end {op}", output.copy(), stack.copy())) if collect_steps else None
    return (output, pasos) if collect_steps else (output, [])
