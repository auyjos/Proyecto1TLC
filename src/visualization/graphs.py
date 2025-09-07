"""
Funciones de visualización usando Graphviz
"""
from typing import Optional

from ..models.dfa import DFA
from ..models.nfa import NFA
from ..parsing.ast_builder import RegexNode
from ..utils.validation import _collect_states

# Importar Graphviz si está disponible
try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False


def visualize_tree(root: RegexNode, filename: str = 'tree') -> None:
    """
    Visualiza el árbol de sintaxis abstracta
    
    Args:
        root: La raíz del AST
        filename: Nombre base del archivo (sin extensión)
    """
    if not GRAPHVIZ_AVAILABLE:
        print(f"  No se puede generar {filename}.png (Graphviz no disponible)")
        return
        
    dot = Digraph(format='png')
    dot.attr(rankdir='TB')
    cnt = 0
    
    def visit(node):
        nonlocal cnt
        nid = f"n{cnt}"
        cnt += 1
        dot.node(nid, label=node.value)
        if node.left:
            lid = visit(node.left)
            dot.edge(lid, nid)
        if node.right:
            rid = visit(node.right)
            dot.edge(rid, nid)
        return nid
    
    visit(root)
    dot.render(filename, cleanup=True)


def visualize_nfa(nfa: NFA, filename: str = 'nfa') -> None:
    """
    Visualiza un autómata finito no determinista
    
    Args:
        nfa: El AFN a visualizar
        filename: Nombre base del archivo (sin extensión)
    """
    if not GRAPHVIZ_AVAILABLE:
        print(f"  No se puede generar {filename}.png (Graphviz no disponible)")
        return
        
    dot = Digraph(format='png')
    dot.attr(rankdir='LR')
    
    # Estados
    states = _collect_states(nfa.transitions)
    for s in states:
        shape = 'doublecircle' if s == nfa.accept else 'circle'
        dot.node(str(s), shape=shape)
    
    # Flecha inicial
    dot.node('start', shape='point')
    dot.edge('start', str(nfa.start))
    
    # Transiciones
    for s, lst in nfa.transitions.items():
        for sym, t in lst:
            label = sym if sym != ' ' else '␠'
            dot.edge(str(s), str(t), label=label)
    
    dot.render(filename, cleanup=True)


def visualize_dfa(dfa: DFA, filename: str = 'dfa') -> None:
    """
    Visualiza un autómata finito determinista
    
    Args:
        dfa: El AFD a visualizar
        filename: Nombre base del archivo (sin extensión)
    """
    if not GRAPHVIZ_AVAILABLE:
        print(f"⚠️  No se puede generar {filename}.png (Graphviz no disponible)")
        return
    
    dot = Digraph(format='png')
    dot.attr(rankdir='LR')
    
    # Estados
    for state in dfa.states:
        if state in dfa.accept_states:
            dot.node(str(state), shape='doublecircle')
        else:
            dot.node(str(state), shape='circle')
    
    # Flecha inicial
    dot.node('start', shape='point', width='0')
    dot.edge('start', str(dfa.start))
    
    # Transiciones
    for from_state, transitions in dfa.transitions.items():
        for symbol, to_state in transitions.items():
            display_symbol = '␣' if symbol == ' ' else symbol
            dot.edge(str(from_state), str(to_state), label=display_symbol)
    
    dot.render(filename, cleanup=True)
