"""
Módulo de validación de autómatas para verificar la correctitud de DFAs y NFAs
"""

from ..models.dfa import DFA


def validate_dfa_for_regex(dfa, regex_pattern, test_cases=None):
    """
    Valida que un DFA reconozca correctamente un patrón de expresión regular
    """
    if test_cases is None:
        # Casos de prueba específicos para (a|b)*abb(a|b)*
        if regex_pattern == "(a|b)*abb(a|b)*":
            test_cases = [
                # Casos que DEBEN ser aceptados
                ("abb", True),
                ("abba", True), 
                ("abbb", True),
                ("aabb", True),
                ("babb", True),
                ("ababa", False),  # No contiene "abb"
                ("abab", False),   # No contiene "abb"
                ("aa", False),     # No contiene "abb" 
                ("bb", False),     # No contiene "abb"
                ("", False),       # Vacía, no contiene "abb"
                ("abbabb", True),  # Contiene "abb"
                ("babbaaaa", True), # Nuestro caso de prueba
                ("aabbbaaa", True), # Contiene "abb"
                ("aabaa", False), # No contiene "abb" - solo tiene aa-ba-aa, a-ab-aa, ab-aa, ba-aa
            ]
        else:
            test_cases = []  # Lista vacía para otros patrones
    
    print(f"\n🔍 VALIDACIÓN DEL DFA para: {regex_pattern}")
    print(f"Estados del DFA: {len(dfa.states)}")
    print(f"Estado inicial: {dfa.start}")
    print(f"Estados de aceptación: {sorted(dfa.accept_states)}")
    
    errors = []
    correct = 0
    
    for word, expected in test_cases:
        result = simulate_dfa_simple(dfa, word)
        status = "✓" if result == expected else "✗"
        
        if result != expected:
            errors.append(f"  {status} '{word}': esperado {expected}, obtuvo {result}")
        else:
            correct += 1
        
        print(f"  {status} '{word}' -> {result} ({'esperado' if result == expected else 'ERROR'})")
    
    print(f"\nResumen: {correct}/{len(test_cases)} casos correctos")
    
    if errors:
        print("\n❌ ERRORES ENCONTRADOS:")
        for error in errors:
            print(error)
        return False
    else:
        print("\n✅ DFA VÁLIDO - Todos los casos pasaron")
        return True


def simulate_dfa_simple(dfa, word):
    """Simulación simple de DFA para validación"""
    current_state = dfa.start
    
    for char in word:
        next_state = dfa.get_transition(current_state, char)
        if next_state is None:
            return False  # Transición no definida
        current_state = next_state
    
    return current_state in dfa.accept_states


def analyze_dfa_structure(dfa):
    """Analiza la estructura de un DFA para detectar problemas"""
    print(f"\n📊 ANÁLISIS ESTRUCTURAL DEL DFA")
    
    # Verificar que el estado inicial existe
    if dfa.start not in dfa.states:
        print(f"❌ ERROR: Estado inicial {dfa.start} no está en el conjunto de estados")
    
    # Verificar que los estados de aceptación existen
    for accept_state in dfa.accept_states:
        if accept_state not in dfa.states:
            print(f"❌ ERROR: Estado de aceptación {accept_state} no está en el conjunto de estados")
    
    # Analizar transiciones
    print(f"Transiciones por estado:")
    for state in sorted(dfa.states):
        if state in dfa.transitions and dfa.transitions[state]:
            transitions_list = []
            for symbol, to_state in dfa.transitions[state].items():
                transitions_list.append(f"{symbol} → {to_state}")
            print(f"  {state}: {', '.join(transitions_list)}")
        else:
            print(f"  {state}: [sin transiciones salientes]")
    
    # Verificar completitud del DFA
    missing_transitions = []
    for state in dfa.states:
        for symbol in dfa.alphabet:
            if state not in dfa.transitions or symbol not in dfa.transitions[state]:
                missing_transitions.append(f"δ({state}, {symbol})")
    
    if missing_transitions:
        print(f"\n⚠️  Transiciones faltantes (DFA incompleto): {missing_transitions}")
    else:
        print("\n✅ DFA completo - todas las transiciones definidas")


def create_simple_dfa_names(dfa):
    """
    Crea un DFA con nombres simples (q0, q1, q2, ...) manteniendo la funcionalidad
    """
    # Mapeo de estados complejos a nombres simples
    state_mapping = {}
    
    # Crear mapeo comenzando con el estado inicial como q0
    counter = 0
    state_mapping[dfa.start] = f"q{counter}"
    counter += 1
    
    # Mapear el resto de estados
    for state in sorted(dfa.states):
        if state not in state_mapping:
            state_mapping[state] = f"q{counter}"
            counter += 1
    
    # Crear nuevo DFA con estructura actual
    simplified_dfa = DFA()
    
    # Establecer estados simples
    for simple_name in state_mapping.values():
        simplified_dfa.add_state(simple_name)
    
    # Establecer alfabeto
    simplified_dfa.alphabet = dfa.alphabet.copy()
    
    # Establecer estado inicial
    simplified_dfa.start = state_mapping[dfa.start]
    
    # Convertir transiciones usando la estructura actual
    for from_state in dfa.transitions:
        simple_from = state_mapping[from_state]
        for symbol, to_state in dfa.transitions[from_state].items():
            simple_to = state_mapping[to_state]
            simplified_dfa.add_transition(simple_from, symbol, simple_to)
    
    # Convertir estados de aceptación
    for state in dfa.accept_states:
        simplified_dfa.accept_states.add(state_mapping[state])
    
    print("\n🔄 MAPEO DE ESTADOS:")
    for complex_state, simple_state in state_mapping.items():
        accept_mark = " (ACEPTA)" if complex_state in dfa.accept_states else ""
        print(f"  {complex_state} → {simple_state}{accept_mark}")
    
    return simplified_dfa, state_mapping
