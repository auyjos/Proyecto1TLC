#!/usr/bin/env python3
"""
Proyecto 1 — Teoría de la Computación
Analizador léxico completo: AFN/AFD desde expresiones regulares

Implementa:
1. Shunting Yard (infix → postfix)
2. Thompson (postfix → AFN)
3. Subconjuntos (AFN → AFD) 
4. Minimización (AFD → AFD mínimo)
5. Simulación (AFN, AFD, AFD mínimo)
6. CLI completa con entrada interactiva

Uso:
    python Proyecto1.py --regex "(b|b)*abb(a|b)*" --word "babbaaaa"
    python Proyecto1.py --regex-file expresiones.txt
    python Proyecto1.py --interactive
"""
import argparse
import os
import sys
from collections import defaultdict, deque
from typing import Dict, FrozenSet, List, Set, Tuple, Union

try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    print("⚠️  Graphviz no disponible. Los gráficos no se generarán.")


# ===================== Estructuras de datos ===============================
class NFA:
    def __init__(self, start, accept, transitions):
        self.start = start            # int
        self.accept = accept          # int
        self.transitions = transitions# dict[int, list[(symbol, int)]]

class DFA:
    """Autómata Finito Determinista"""
    def __init__(self):
        self.states = set()                    # Set[Union[int, str]]
        self.alphabet = set()                  # Set[str]
        self.transitions = {}                  # Dict[Union[int, str], Dict[str, Union[int, str]]]
        self.start = None                      # Union[int, str]
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


# ===================== Paso 0: desugar + y ? (recursivo) =====================
def expand_plus_question(expr: str) -> str:
    i, n, out = 0, len(expr), ""

    def is_escaped(pos):
        cnt, k = 0, pos - 1
        while k >= 0 and expr[k] == '\\':
            cnt += 1
            k -= 1
        return (cnt % 2) == 1

    while i < n:
        if expr[i] == '\\' and i + 1 < n:        # \X
            token = expr[i:i+2]; i += 2
        elif expr[i] == '(' and not is_escaped(i):  # ( ... )
            start, depth = i, 1
            i += 1
            while i < n and depth > 0:
                if expr[i] == '(' and not is_escaped(i): depth += 1
                elif expr[i] == ')' and not is_escaped(i): depth -= 1
                i += 1
            inner = expr[start+1:i-1]
            token = "(" + expand_plus_question(inner) + ")"
        else:                                     # literal
            token = expr[i]; i += 1

        if i < n and not is_escaped(i) and expr[i] in ['+', '?']:
            op = expr[i]; i += 1
            if op == '+':      out += token + token + '*'
            else:              out += f"({token}|ε)"
        else:
            out += token
    return out


# ===================== Paso 1: insertar concatenación explícita '.' =========
def insert_concatenation(expr: str):
    tokens, i = [], 0
    while i < len(expr):
        if expr[i] == '\\' and i + 1 < len(expr):
            tokens.append(expr[i:i+2]); i += 2
        else:
            tokens.append(expr[i]); i += 1

    result = []
    for j, tok in enumerate(tokens):
        if j > 0:
            prev = tokens[j-1]
            if prev not in ['|', '('] and tok not in ['|', ')', '*', '+', '?']:
                result.append('.')
        result.append(tok)
    return result


# ===================== Paso 2: Shunting-Yard (infix → postfix) ==============
def precedence(op: str):
    if op in ('*', '+', '?'): return 3
    if op == '.':             return 2
    if op == '|':             return 1
    return 0

def shunting_yard(tokens):
    output, stack, pasos = [], [], []
    for token in tokens:
        if token.startswith('\\') or (len(token) == 1 and (token.isalnum() or token in ['_', '[', ']', '{', '}', 'ε'])):
            output.append(token); pasos.append((f"operand {token}", output.copy(), stack.copy()))
        elif token == '(':
            stack.append(token); pasos.append(("push (", output.copy(), stack.copy()))
        elif token == ')':
            while stack and stack[-1] != '(':
                op = stack.pop(); output.append(op)
                pasos.append(("pop for )", output.copy(), stack.copy()))
            if stack and stack[-1] == '(':
                stack.pop(); pasos.append(("pop (", output.copy(), stack.copy()))
            else:
                pasos.append(("ignore unmatched )", output.copy(), stack.copy()))
        elif token in ['|', '.', '*', '+', '?']:
            while stack and precedence(stack[-1]) >= precedence(token):
                if stack[-1] == '(': break
                op = stack.pop(); output.append(op)
                pasos.append((f"pop op {op}", output.copy(), stack.copy()))
            stack.append(token); pasos.append((f"push op {token}", output.copy(), stack.copy()))
        else:
            pasos.append((f"ignore {token}", output.copy(), stack.copy()))
    while stack:
        op = stack.pop(); output.append(op)
        pasos.append((f"pop end {op}", output.copy(), stack.copy()))
    return output, pasos


# ===================== Paso 3: AST ==========================================
class RegexNode:
    def __init__(self, value, left=None, right=None):
        self.value, self.left, self.right = value, left, right

def build_syntax_tree(postfix_tokens):
    stack = []
    for tok in postfix_tokens:
        if tok in ('*', '+', '?'):
            child = stack.pop(); stack.append(RegexNode(tok, left=child))
        elif tok in ('.', '|'):
            r = stack.pop(); l = stack.pop()
            stack.append(RegexNode(tok, left=l, right=r))
        else:
            stack.append(RegexNode(tok))
    return stack.pop()


# ===================== Paso 4: Thompson (AST → AFN) =========================
def _merge_trans(ta, tb):
    for s, lst in tb.items():
        ta.setdefault(s, []).extend(lst)

def thompson_from_ast(root):
    counter = {'id': 0}
    def new_state():
        counter['id'] += 1
        return counter['id']

    def lit_symbol(tok):
        # '\X' → 'X'; 'ε' se queda como 'ε'
        if tok == 'ε': return 'ε'
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

        if v == '+':   # por si no se desazucara (uno o más)
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


# ===================== Paso 5: simulación de AFN ============================
def epsilon_closure(states, transitions):
    stack = list(states)
    visited = set(states)
    while stack:
        s = stack.pop()
        for sym, t in transitions.get(s, []):
            if sym == 'ε' and t not in visited:
                visited.add(t); stack.append(t)
    return visited

def move(states, sym, transitions):
    out = set()
    for s in states:
        for a, t in transitions.get(s, []):
            if a == sym:
                out.add(t)
    return out

def simulate_nfa(nfa: NFA, w: str) -> bool:
    if w == 'ε':  # permitir 'ε' como cadena vacía
        w = ''
    cur = epsilon_closure({nfa.start}, nfa.transitions)
    for ch in w:
        cur = epsilon_closure(move(cur, ch, nfa.transitions), nfa.transitions)
        if not cur:
            break
    cur = epsilon_closure(cur, nfa.transitions)
    return nfa.accept in cur


# ===================== Paso 6: AFD por subconjuntos =========================
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


# ===================== Paso 7: Minimización de AFD ==========================
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


# ===================== Paso 8: Simulación de AFD ============================
def simulate_dfa(dfa, word):
    """Simula AFD con una cadena"""
    if not dfa.states:
        return False
    
    current_state = dfa.start
    
    for symbol in word:
        next_state = dfa.get_transition(current_state, symbol)
        
        if next_state is None:
            return False
        
        current_state = next_state
    
    return current_state in dfa.accept_states


# ===================== Validación y renumeración =============================
def _collect_states(transitions):
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
    from collections import deque
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
    from collections import deque

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


# ===================== Render: Árbol, AFN y AFD ============================
def visualize_tree(root, filename='tree'):
    if not GRAPHVIZ_AVAILABLE:
        print(f"⚠️  No se puede generar {filename}.png (Graphviz no disponible)")
        return
        
    dot = Digraph(format='png')
    dot.attr(rankdir='TB')
    cnt = 0
    def visit(node):
        nonlocal cnt
        nid = f"n{cnt}"; cnt += 1
        dot.node(nid, label=node.value)
        if node.left:
            lid = visit(node.left); dot.edge(lid, nid)
        if node.right:
            rid = visit(node.right); dot.edge(rid, nid)
        return nid
    visit(root)
    dot.render(filename, cleanup=True)

def visualize_nfa(nfa: NFA, filename='nfa'):
    if not GRAPHVIZ_AVAILABLE:
        print(f"⚠️  No se puede generar {filename}.png (Graphviz no disponible)")
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

def visualize_dfa(dfa: DFA, filename='dfa'):
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


# ===================== Pipeline completo ===================================
def procesar_expresion_completa(expr, word=None, idx=1, verbose=False, no_graphs=False, outdir="outputs"):
    """
    Procesa una expresión regular completa: AFN → AFD → AFD minimizado
    """
    print(f"\n=== Expr #{idx} ===")
    print(f"r (infijo)    : {expr}")
    
    try:
        # Paso 1: Parseo: desugar → concat → postfix → AST
        expr2 = expand_plus_question(expr)
        if verbose:
            print(f"r (expandido) : {expr2}")
        
        tokens = insert_concatenation(expr2)
        postfix, _ = shunting_yard(tokens)
        if verbose:
            print(f"postfix       : {''.join(postfix)}")
        
        root = build_syntax_tree(postfix)
        
        # Paso 2: Thompson → AFN
        nfa = thompson_from_ast(root)
        
        # Validaciones + renumeración
        issues = validate_nfa(nfa)
        if issues and verbose:
            print("Validaciones del AFN:")
            for msg in issues:
                print("  -", msg)
        nfa = renumber_nfa(nfa, make_accept_last=True)
        
        # Paso 3: AFN → AFD por subconjuntos
        dfa = subset_construction(nfa)
        
        # Paso 4: AFD → AFD minimizado
        dfa_min = minimize_dfa(dfa)
        
        if verbose:
            print(f"AFN: {len(_collect_states(nfa.transitions))} estados")
            print(f"AFD: {len(dfa.states)} estados") 
            print(f"AFD minimizado: {len(dfa_min.states)} estados")
        
        # Generar gráficos
        if not no_graphs:
            os.makedirs(outdir, exist_ok=True)
            visualize_tree(root, filename=f"{outdir}/tree_simplified_{idx}")
            visualize_nfa(nfa, filename=f"{outdir}/nfa_{idx}")
            visualize_dfa(dfa, filename=f"{outdir}/dfa_{idx}")
            visualize_dfa(dfa_min, filename=f"{outdir}/dfa_min_{idx}")
        
        # Obtener palabra si no se proporciona
        if word is None:
            word = input(f"w para la expresión {idx} ('{expr}'): ").strip()
        
        # Simulación en todos los autómatas
        if word is not None:
            print(f"w             : {word!r}")
            
            # Simular AFN
            nfa_result = simulate_nfa(nfa, word)
            
            # Simular AFD
            dfa_result = simulate_dfa(dfa, word)
            
            # Simular AFD minimizado
            dfa_min_result = simulate_dfa(dfa_min, word)
            
            print("Simulación:")
            print(f"  AFN          : {'sí' if nfa_result else 'no'}")
            print(f"  AFD          : {'sí' if dfa_result else 'no'}")
            print(f"  AFD minimizado: {'sí' if dfa_min_result else 'no'}")
            
            # Verificar equivalencia
            if not (nfa_result == dfa_result == dfa_min_result):
                print("⚠️  ADVERTENCIA: Los autómatas no son equivalentes!")
            else:
                print("✓ Todos los autómatas son equivalentes")
        
        if not no_graphs:
            print(f"Archivos: tree_simplified_{idx}.png, nfa_{idx}.png, dfa_{idx}.png, dfa_min_{idx}.png")
        
        return True
        
    except Exception as e:
        print(f"❌ Error procesando '{expr}': {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def procesar_archivo(regex_path, strings_path=None, verbose=False, no_graphs=False, outdir="outputs"):
    """Procesa archivo de expresiones regulares"""
    strings = None
    if strings_path:
        with open(strings_path, encoding='utf-8') as g:
            strings = [line.rstrip('\n') for line in g]

    success_count = 0
    total_count = 0

    with open(regex_path, encoding='utf-8') as f:
        idx = 1
        for k, linea in enumerate(f):
            expr = linea.strip()
            if not expr or expr.startswith('#'):
                continue

            total_count += 1
            word = strings[k] if strings and k < len(strings) else None
            
            if procesar_expresion_completa(expr, word, idx, verbose, no_graphs, outdir):
                success_count += 1
            idx += 1
    
    print(f"\n📊 Resumen: {success_count}/{total_count} expresiones procesadas exitosamente")
    return success_count, total_count


def modo_interactivo():
    """Modo interactivo para entrada de expresiones y palabras"""
    print("=== MODO INTERACTIVO ===")
    print("Ingrese expresiones regulares (Enter vacío para salir)")
    
    idx = 1
    while True:
        try:
            expr = input(f"\nExpresión regular #{idx}: ").strip()
            if not expr:
                break
            
            word = input(f"Palabra a verificar (opcional): ").strip()
            word = word if word else None
            
            verbose = input("¿Modo verboso? (s/N): ").strip().lower() == 's'
            no_graphs = input("¿Sin gráficos? (s/N): ").strip().lower() == 's'
            
            procesar_expresion_completa(expr, word, idx, verbose, no_graphs)
            idx += 1
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Adiós!")
            break
        except EOFError:
            break


# ===================== CLI y main ==========================================
def create_parser():
    """Crea parser de argumentos CLI"""
    parser = argparse.ArgumentParser(
        description="Proyecto 1 - Teoría de la Computación: AFN/AFD desde expresiones regulares",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python Proyecto1.py --regex "(b|b)*abb(a|b)*" --word "babbaaaa"
  python Proyecto1.py --regex-file expresiones.txt
  python Proyecto1.py --interactive
  python Proyecto1.py -r "a*" -w "aaa" --verbose --no-graphs
        """
    )
    
    # Modos de entrada (mutuamente exclusivos)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-r", "--regex", help="Expresión regular individual")
    group.add_argument("--regex-file", help="Archivo con expresiones regulares (una por línea)")
    group.add_argument("--interactive", action="store_true", help="Modo interactivo")
    
    # Entrada opcional
    parser.add_argument("-w", "--word", help="Cadena a verificar")
    parser.add_argument("--epsilon", default="ε", help="Símbolo para épsilon (default: ε)")
    
    # Opciones de salida
    parser.add_argument("--outdir", default="outputs", help="Directorio de salida (default: outputs)")
    parser.add_argument("--no-graphs", action="store_true", help="No generar gráficos")
    
    # Opciones adicionales
    parser.add_argument("--verbose", "-v", action="store_true", help="Modo verboso")
    
    return parser


# ===================== main ==================================================
def main():
    """Función principal"""
    parser = create_parser()
    
    # Si no hay argumentos, usar modo interactivo
    if len(sys.argv) == 1:
        modo_interactivo()
        return
    
    args = parser.parse_args()
    
    # Modo interactivo
    if args.interactive:
        modo_interactivo()
        return
    
    # Validar entrada
    if not args.regex and not args.regex_file:
        print("❌ Error: Debe especificar --regex, --regex-file o --interactive")
        parser.print_help()
        return
    
    # Crear directorio de salida
    if not args.no_graphs:
        os.makedirs(args.outdir, exist_ok=True)
    
    # Procesar expresión individual
    if args.regex:
        success = procesar_expresion_completa(
            args.regex, 
            args.word, 
            1, 
            args.verbose, 
            args.no_graphs, 
            args.outdir
        )
        
        if success:
            print(f"\n✅ Expresión procesada exitosamente")
            if not args.no_graphs:
                print(f"📁 Archivos guardados en: {os.path.abspath(args.outdir)}")
        else:
            print(f"\n❌ Error procesando la expresión")
            sys.exit(1)
    
    # Procesar archivo de expresiones
    elif args.regex_file:
        if not os.path.exists(args.regex_file):
            print(f"❌ Error: El archivo '{args.regex_file}' no existe")
            sys.exit(1)
        
        success_count, total_count = procesar_archivo(
            args.regex_file, 
            None,  # strings_path 
            args.verbose, 
            args.no_graphs, 
            args.outdir
        )
        
        if not args.no_graphs and success_count > 0:
            print(f"📁 Archivos guardados en: {os.path.abspath(args.outdir)}")


if __name__ == '__main__':
    # Compatibilidad con uso original
    if len(sys.argv) >= 2 and not sys.argv[1].startswith('-'):
        # Modo original: python Proyecto1.py expresiones.txt [cadenas.txt]
        regex_path = sys.argv[1]
        strings_path = sys.argv[2] if len(sys.argv) == 3 else None
        
        if not os.path.exists(regex_path):
            print(f"❌ Error: El archivo '{regex_path}' no existe")
            sys.exit(1)
        
        procesar_archivo(regex_path, strings_path, verbose=True, no_graphs=False)
    else:
        main()
