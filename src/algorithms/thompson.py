"""
Algoritmo de construcción de Thompson: AST → AFN
"""
from ..models.nfa import NFA
from ..parsing.ast_builder import RegexNode


def _merge_trans(ta, tb):
    """Mezcla dos diccionarios de transiciones"""
    for s, lst in tb.items():
        ta.setdefault(s, []).extend(lst)


def thompson_from_ast(root: RegexNode) -> NFA:
    """
    Construye un AFN desde un AST usando el algoritmo de construcción de Thompson
    
    Args:
        root: La raíz del árbol de sintaxis abstracta
        
    Returns:
        NFA: El autómata finito no determinista construido
    """
    counter = {'id': 0}
    
    def new_state():
        counter['id'] += 1
        return counter['id']

    def lit_symbol(tok):
        # '\X' → 'X'; 'ε' se queda como 'ε'
        if tok == 'ε': 
            return 'ε'
        if tok.startswith('\\') and len(tok) == 2:
            return tok[1]
        return tok

    def build(node):
        if node.left is None and node.right is None:
            s, t = new_state(), new_state()
            sym = lit_symbol(node.value)
            trans = {s: [(sym, t)]}
            return NFA(s, t, trans)

        v = node.value
        if v == '.':   # concatenación
            A = build(node.left)
            B = build(node.right)
            _merge_trans(A.transitions, B.transitions)
            A.transitions.setdefault(A.accept, []).append(('ε', B.start))
            return NFA(A.start, B.accept, A.transitions)

        if v == '|':   # unión
            A = build(node.left)
            B = build(node.right)
            s, t = new_state(), new_state()
            trans = {}
            _merge_trans(trans, A.transitions)
            _merge_trans(trans, B.transitions)
            trans.setdefault(s, []).extend([('ε', A.start), ('ε', B.start)])
            trans.setdefault(A.accept, []).append(('ε', t))
            trans.setdefault(B.accept, []).append(('ε', t))
            return NFA(s, t, trans)

        if v == '*':   # estrella
            A = build(node.left)
            s, t = new_state(), new_state()
            trans = {}
            _merge_trans(trans, A.transitions)
            trans.setdefault(s, []).extend([('ε', A.start), ('ε', t)])
            trans.setdefault(A.accept, []).extend([('ε', A.start), ('ε', t)])
            return NFA(s, t, trans)

        if v == '+':   # por si no se desazucare (uno o más)
            # A . A*
            A = build(node.left)
            s1 = RegexNode('.', left=node.left, right=RegexNode('*', left=node.left))
            return build(s1)

        if v == '?':   # cero o uno
            A = build(node.left)
            s, t = new_state(), new_state()
            trans = {}
            _merge_trans(trans, A.transitions)
            trans.setdefault(s, []).extend([('ε', A.start), ('ε', t)])
            trans.setdefault(A.accept, []).append(('ε', t))
            return NFA(s, t, trans)

        raise ValueError(f"Operador no soportado: {v}")

    return build(root)
