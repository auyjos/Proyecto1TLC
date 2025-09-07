"""
Funciones de validación y renumeración de autómatas
"""
from collections import deque
from typing import List, Set

from ..models.nfa import NFA


# Función auxiliar exportada para uso en otras partes
def _collect_states(transitions):
    """Recopila todos los estados de las transiciones"""
    states = set(transitions.keys())
    for lst in transitions.values():
        for _, t in lst:
            states.add(t)
    return states


def validate_nfa(nfa: NFA):
    """
    Devuelve lista de strings con advertencias/errores.
    (No detiene ejecución; imprime en consola en la orquestación).
    """
    issues = []
    T = nfa.transitions
    states = _collect_states(T)

    # 1) start/accept presentes
    if nfa.start not in states:
        issues.append(f"El estado inicial {nfa.start} no aparece en transiciones.")
    if nfa.accept not in states:
        issues.append(f"El estado de aceptación {nfa.accept} no aparece en transiciones.")

    # 2) grados
    indeg = {s: 0 for s in states}
    outdeg = {s: 0 for s in states}
    for s, lst in T.items():
        outdeg[s] += len(lst)
        for _, t in lst:
            indeg[t] = indeg.get(t, 0) + 1
    if indeg.get(nfa.start, 0) != 0:
        issues.append(f"El estado inicial {nfa.start} tiene indegree={indeg.get(nfa.start, 0)} (esperado 0).")
    if outdeg.get(nfa.accept, 0) != 0:
        issues.append(f"El estado de aceptación {nfa.accept} tiene outdegree={outdeg.get(nfa.accept, 0)} (esperado 0).")

    # 3) alcanzabilidad desde start
    q = deque([nfa.start])
    seen = {nfa.start}
    while q:
        s = q.popleft()
        for _, t in T.get(s, []):
            if t not in seen:
                seen.add(t); q.append(t)
    unreachable = states - seen
    if unreachable:
        issues.append(f"Hay estados inalcanzables desde {nfa.start}: {sorted(unreachable)}")

    # 4) accept alcanzable
    if nfa.accept not in seen:
        issues.append(f"El estado de aceptación {nfa.accept} NO es alcanzable desde {nfa.start}.")

    return issues


def renumber_nfa(nfa: NFA, make_accept_last: bool = True) -> NFA:
    """
    Renumera estados con BFS desde start para que:
      - start -> 1
      - (opcional) accept -> último
    Mantiene la estructura del AFN.
    """
    T = nfa.transitions
    states = _collect_states(T)

    # Orden BFS desde start (para layout natural)
    q = deque([nfa.start])
    seen = {nfa.start}
    order = []
    while q:
        s = q.popleft()
        order.append(s)
        # orden determinista por estética (símbolo, destino)
        for sym, t in sorted(T.get(s, []), key=lambda x: (x[0], x[1])):
            if t not in seen:
                seen.add(t); q.append(t)

    # Si hubiera estados aislados, añadirlos al final
    for s in sorted(states):
        if s not in seen:
            order.append(s)

    # Forzar accept al final si se pide
    if make_accept_last and nfa.accept in order:
        order = [s for s in order if s != nfa.accept] + [nfa.accept]

    mapping = {old: i+1 for i, old in enumerate(order)}

    T2 = {}
    for s, lst in T.items():
        ns = mapping[s]
        for sym, t in lst:
            T2.setdefault(ns, []).append((sym, mapping[t]))

    return NFA(start=mapping[nfa.start], accept=mapping[nfa.accept], transitions=T2)
