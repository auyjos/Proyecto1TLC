"""
Definición del Autómata Finito Determinista (AFD/DFA)
"""
from typing import Dict, Set, Union


class DFA:
    """Autómata Finito Determinista"""
    
    def __init__(self):
        self.states = set()                    # Set[Union[int, str]]
        self.alphabet = set()                  # Set[str]
        self.transitions = {}                  # Dict[Union[int, str], Dict[str, Union[int, str]]]
        self.start: Union[int, str, None] = None      # Union[int, str, None]
        self.accept_states = set()             # Set[Union[int, str]]
    
    def add_state(self, state):
        self.states.add(state)
        if state not in self.transitions:
            self.transitions[state] = {}
    
    def add_transition(self, from_state, symbol, to_state):
        self.states.add(from_state)
        self.states.add(to_state)
        self.alphabet.add(symbol)
        
        if from_state not in self.transitions:
            self.transitions[from_state] = {}
        self.transitions[from_state][symbol] = to_state
    
    def get_transition(self, state, symbol):
        if state in self.transitions and symbol in self.transitions[state]:
            return self.transitions[state][symbol]
        return None
