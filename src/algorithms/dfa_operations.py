"""
Algoritmos para construcción y manipulación de AFD
Incluye: construcción por subconjuntos, minimización
"""
from collections import defaultdict, deque
from typing import FrozenSet, Set

from ..models.dfa import DFA
from ..models.nfa import NFA


def epsilon_closure_dfa(states, nfa):
    """Calcula la cerradura épsilon para construcción de AFD"""
    closure = set(states)
    stack = list(states)
    
    while stack:
        state = stack.pop()
        if state in nfa.transitions:
            for symbol, to_state in nfa.transitions[state]:
                if symbol == 'ε' and to_state not in closure:
                    closure.add(to_state)
                    stack.append(to_state)
    
    return closure


def move_dfa(states, symbol, nfa):
    """Calcula move para construcción de AFD"""
    result = set()
    
    for state in states:
        if state in nfa.transitions:
            for trans_symbol, to_state in nfa.transitions[state]:
                if trans_symbol == symbol:
                    result.add(to_state)
    
    return result


def format_state_set(states):
    """Formatea conjunto de estados como string"""
    if not states:
        return "∅"
    
    sorted_states = sorted(states)
    
    if len(sorted_states) == 1:
        return str(sorted_states[0])
    else:
        return "{" + ",".join(map(str, sorted_states)) + "}"


def subset_construction(nfa):
    """Construye AFD desde AFN usando algoritmo de subconjuntos"""
    # Obtener alfabeto del AFN
    alphabet = set()
    for transitions in nfa.transitions.values():
        for symbol, _ in transitions:
            if symbol != 'ε':
                alphabet.add(symbol)
    
    dfa = DFA()
    dfa.alphabet = alphabet
    
    # Estado inicial del DFA
    start_closure = epsilon_closure_dfa({nfa.start}, nfa)
    start_state_name = format_state_set(start_closure)
    
    dfa.start = start_state_name
    dfa.add_state(start_state_name)
    
    # Si contiene estado de aceptación del NFA
    if nfa.accept in start_closure:
        dfa.accept_states.add(start_state_name)
    
    # BFS para construir todos los estados
    queue = deque([(start_state_name, start_closure)])
    processed = {frozenset(start_closure): start_state_name}
    
    while queue:
        current_dfa_state, current_nfa_states = queue.popleft()
        
        for symbol in alphabet:
            moved_states = move_dfa(current_nfa_states, symbol, nfa)
            if not moved_states:
                continue
                
            next_states = epsilon_closure_dfa(moved_states, nfa)
            next_states_frozen = frozenset(next_states)
            
            if next_states_frozen in processed:
                next_dfa_state = processed[next_states_frozen]
            else:
                next_dfa_state = format_state_set(next_states)
                processed[next_states_frozen] = next_dfa_state
                dfa.add_state(next_dfa_state)
                
                if nfa.accept in next_states:
                    dfa.accept_states.add(next_dfa_state)
                
                queue.append((next_dfa_state, next_states))
            
            dfa.add_transition(current_dfa_state, symbol, next_dfa_state)
    
    return dfa


def subset_construction_debug(nfa):
    """Construye AFD desde AFN (versión con prints para ver el proceso)."""
    # Alfabeto
    alphabet = set()
    for transitions in nfa.transitions.values():
        for symbol, _ in transitions:
            if symbol != 'ε':
                alphabet.add(symbol)

    dfa = DFA()
    dfa.alphabet = alphabet

    # Estado inicial
    start_closure = epsilon_closure_dfa({nfa.start}, nfa)
    start_state_name = format_state_set(start_closure)
    dfa.start = start_state_name
    dfa.add_state(start_state_name)
    if nfa.accept in start_closure:
        dfa.accept_states.add(start_state_name)

    print(f"[TRACE] start_closure = {start_closure} => {start_state_name}")
    print(f"[TRACE] alphabet = {sorted(alphabet)}")

    queue = deque([(start_state_name, start_closure)])
    processed = {frozenset(start_closure): start_state_name}

    while queue:
        current_dfa_state, current_nfa_states = queue.popleft()
        print(f"[TRACE] ▶ Estado DFA actual: {current_dfa_state} ~ NFA {sorted(current_nfa_states)}")
        for symbol in alphabet:
            moved_states = move_dfa(current_nfa_states, symbol, nfa)
            if not moved_states:
                print(f"[TRACE]   {symbol}: move = ∅ (sin transición)")
                continue

            next_states = epsilon_closure_dfa(moved_states, nfa)
            next_states_frozen = frozenset(next_states)
            if next_states_frozen in processed:
                next_dfa_state = processed[next_states_frozen]
                print(f"[TRACE]   {symbol}: move={sorted(moved_states)}; ε-closure={sorted(next_states)} => EXISTE {next_dfa_state}")
            else:
                next_dfa_state = format_state_set(next_states)
                processed[next_states_frozen] = next_dfa_state
                dfa.add_state(next_dfa_state)
                if nfa.accept in next_states:
                    dfa.accept_states.add(next_dfa_state)
                queue.append((next_dfa_state, next_states))
                print(f"[TRACE]   {symbol}: move={sorted(moved_states)}; ε-closure={sorted(next_states)} => NUEVO {next_dfa_state}")

            dfa.add_transition(current_dfa_state, symbol, next_dfa_state)
            print(f"[TRACE]     transición: δ({current_dfa_state}, {symbol}) = {next_dfa_state}")

    return dfa


def subset_construction_wrapper(nfa):
    """Envuelve la construcción de AFD: pregunta si mostrar el proceso y mide el tiempo."""
    from ..utils.helpers import _timer, ask_yes_no
    
    ver_proceso = ask_yes_no("¿Mostrar el proceso del algoritmo de subconjuntos?", default_no=True)
    with _timer() as t_sub:
        if ver_proceso:
            dfa = subset_construction_debug(nfa)   # con prints
        else:
            dfa = subset_construction(nfa)         # sin prints
    dur = t_sub()
    print(f" Construcción de AFD tomó {dur:.6f} s")
    return dfa


# Las funciones de minimización se incluirán aquí también por ahora
def remove_unreachable_states(dfa):
    """Elimina estados inalcanzables"""
    reachable = set()
    queue = [dfa.start]
    reachable.add(dfa.start)
    
    while queue:
        current = queue.pop(0)
        if current in dfa.transitions:
            for symbol, next_state in dfa.transitions[current].items():
                if next_state not in reachable:
                    reachable.add(next_state)
                    queue.append(next_state)
    
    # Crear nuevo DFA solo con estados alcanzables
    new_dfa = DFA()
    new_dfa.start = dfa.start
    new_dfa.alphabet = dfa.alphabet.copy()
    new_dfa.states = reachable
    new_dfa.accept_states = dfa.accept_states & reachable
    
    for state in reachable:
        if state in dfa.transitions:
            for symbol, next_state in dfa.transitions[state].items():
                if next_state in reachable:
                    new_dfa.add_transition(state, symbol, next_state)
    
    return new_dfa


def find_partition_containing(state, partitions):
    """Encuentra la partición que contiene el estado"""
    if state is None:
        return -1
    
    for i, partition in enumerate(partitions):
        if state in partition:
            return i
    
    return -1


def refine_partition(partition, all_partitions, dfa):
    """Refina una partición basándose en transiciones"""
    if len(partition) <= 1:
        return [partition]
    
    groups = defaultdict(set)
    
    for state in partition:
        signature = []
        for symbol in sorted(dfa.alphabet):
            next_state = dfa.get_transition(state, symbol)
            target_partition = find_partition_containing(next_state, all_partitions)
            signature.append(target_partition)
        
        signature_tuple = tuple(signature)
        groups[signature_tuple].add(state)
    
    return list(groups.values())


def minimize_dfa(dfa):
    """Minimiza AFD usando particiones refinadas"""
    if not dfa.states:
        return dfa
    
    # Eliminar estados inalcanzables
    reachable_dfa = remove_unreachable_states(dfa)
    
    if len(reachable_dfa.states) <= 1:
        return reachable_dfa
    
    # Partición inicial: aceptación vs no aceptación
    accept_states = reachable_dfa.accept_states
    non_accept_states = reachable_dfa.states - accept_states
    
    partitions = []
    if non_accept_states:
        partitions.append(non_accept_states)
    if accept_states:
        partitions.append(accept_states)
    
    # Refinar hasta que no cambien
    changed = True
    iteration = 0
    while changed:
        changed = False
        new_partitions = []
        iteration += 1
        
        for partition in partitions:
            refined = refine_partition(partition, partitions, reachable_dfa)
            if len(refined) > 1:
                changed = True
            new_partitions.extend(refined)
        
        partitions = new_partitions
        
        # Evitar bucle infinito
        if iteration > 10:
            break
    
    # Construir AFD minimizado
    return build_minimized_dfa(reachable_dfa, partitions)


def build_minimized_dfa(original_dfa, partitions):
    """Construye AFD minimizado desde particiones"""
    min_dfa = DFA()
    min_dfa.alphabet = original_dfa.alphabet.copy()
    
    # Mapear particiones a estados
    partition_to_state = {}
    state_mapping = {}
    
    for i, partition in enumerate(partitions):
        new_state_name = f"q{i}"
        partition_to_state[i] = new_state_name
        min_dfa.add_state(new_state_name)
        
        for old_state in partition:
            state_mapping[old_state] = new_state_name
    
    # Estado inicial
    start_partition = find_partition_containing(original_dfa.start, partitions)
    min_dfa.start = partition_to_state[start_partition]
    
    # Estados de aceptación
    for i, partition in enumerate(partitions):
        if partition & original_dfa.accept_states:
            min_dfa.accept_states.add(partition_to_state[i])
    
    # Transiciones
    for i, partition in enumerate(partitions):
        representative = next(iter(partition))
        new_state = partition_to_state[i]
        
        for symbol in original_dfa.alphabet:
            next_old_state = original_dfa.get_transition(representative, symbol)
            if next_old_state is not None:
                next_new_state = state_mapping[next_old_state]
                min_dfa.add_transition(new_state, symbol, next_new_state)
    
    return min_dfa
