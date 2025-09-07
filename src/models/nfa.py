"""
Definición del Autómata Finito No Determinista (AFN/NFA)
"""
from typing import Dict, List, Tuple


class NFA:
    """Autómata Finito No Determinista"""
    
    def __init__(self, start, accept, transitions):
        self.start = start            # int
        self.accept = accept          # int
        self.transitions = transitions# dict[int, list[(symbol, int)]]
