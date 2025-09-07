"""
Constructor del Árbol de Sintaxis Abstracta (AST) para expresiones regulares
"""
from typing import List, Optional


class RegexNode:
    """Nodo del árbol de sintaxis abstracta para expresiones regulares"""
    
    def __init__(self, value, left=None, right=None):
        self.value = value      # str: el valor/operador del nodo
        self.left = left        # RegexNode: hijo izquierdo
        self.right = right      # RegexNode: hijo derecho


def build_syntax_tree(postfix_tokens: List[str]) -> RegexNode:
    """
    Construye un AST desde una lista de tokens en notación postfija
    
    Args:
        postfix_tokens: Lista de tokens en notación postfija
        
    Returns:
        RegexNode: La raíz del árbol de sintaxis abstracta
    """
    stack = []
    for tok in postfix_tokens:
        if tok in ('*', '+', '?'):
            child = stack.pop()
            stack.append(RegexNode(tok, left=child))
        elif tok in ('.', '|'):
            r = stack.pop()
            l = stack.pop()
            stack.append(RegexNode(tok, left=l, right=r))
        else:
            stack.append(RegexNode(tok))
    return stack.pop()
