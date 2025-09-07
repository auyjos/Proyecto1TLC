"""
Simulación de autómatas (AFN y AFD)
"""
from typing import Set

from ..models.dfa import DFA
from ..models.nfa import NFA


def epsilon_closure(states, transitions):
    """Calcula la cerradura épsilon de un conjunto de estados"""
    stack = list(states)
    visited = set(states)
    while stack:
        s = stack.pop()
        for sym, t in transitions.get(s, []):
            if sym == 'ε' and t not in visited:
                visited.add(t); stack.append(t)
    return visited


def move(states, sym, transitions):
    """Calcula el conjunto de estados alcanzables con un símbolo dado"""
    out = set()
    for s in states:
        for a, t in transitions.get(s, []):
            if a == sym:
                out.add(t)
    return out


def simulate_nfa(nfa: NFA, w: str) -> bool:
    """
    Simula un AFN con una cadena de entrada
    
    Args:
        nfa: El autómata finito no determinista
        w: La cadena de entrada
        
    Returns:
        bool: True si la cadena es aceptada, False caso contrario
    """
    if w == 'ε':  # permitir 'ε' como cadena vacía
        w = ''
    cur = epsilon_closure({nfa.start}, nfa.transitions)
    for ch in w:
        cur = epsilon_closure(move(cur, ch, nfa.transitions), nfa.transitions)
        if not cur:
            break
    cur = epsilon_closure(cur, nfa.transitions)
    return nfa.accept in cur


def simulate_dfa(dfa: DFA, word: str) -> bool:
    """
    Simula un AFD con una cadena de entrada
    
    Args:
        dfa: El autómata finito determinista
        word: La cadena de entrada
        
    Returns:
        bool: True si la cadena es aceptada, False caso contrario
    """
    if not dfa.states:
        return False
    
    current_state = dfa.start
    
    for symbol in word:
        next_state = dfa.get_transition(current_state, symbol)
        
        if next_state is None:
            return False
        
        current_state = next_state
    
    return current_state in dfa.accept_states
