"""
Módulo CLI para el procesamiento de expresiones regulares.

Contiene todas las funciones relacionadas con la interfaz de línea de comandos,
incluyendo procesamiento de expresiones, archivos, modo interactivo y argumentos CLI.
"""

import argparse
import os
import sys
from typing import Optional, Tuple

# Imports relativos a la estructura del proyecto
if __name__ == "__main__":
    # Para ejecución directa del módulo
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.algorithms.dfa_operations import (minimize_dfa,
                                           subset_construction_wrapper)
from src.algorithms.simulation import simulate_dfa, simulate_nfa
from src.algorithms.thompson import thompson_from_ast
from src.parsing.ast_builder import build_syntax_tree
from src.parsing.preprocessor import expand_plus_question, insert_concatenation
from src.parsing.shunting_yard import shunting_yard
from src.utils.dfa_validator import (analyze_dfa_structure,
                                     create_simple_dfa_names,
                                     validate_dfa_for_regex)
from src.utils.validation import _collect_states, renumber_nfa, validate_nfa
from src.visualization.graphs import (visualize_dfa, visualize_nfa,
                                      visualize_tree)


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
        dfa = subset_construction_wrapper(nfa)
        
        # Paso 4: AFD → AFD minimizado
        dfa_min = minimize_dfa(dfa)
        
        if verbose:
            print(f"AFN: {len(_collect_states(nfa.transitions))} estados")
            print(f"AFD: {len(dfa.states)} estados") 
            print(f"AFD minimizado: {len(dfa_min.states)} estados")
        
        # VALIDACIÓN DEL DFA ORIGINAL
        print("\n" + "="*60)
        print("🔍 VALIDACIÓN DEL DFA ORIGINAL (SIN MINIMIZAR)")
        print("="*60)
        
        # Crear versión con nombres simples para análisis del DFA original
        simple_dfa_orig, _ = create_simple_dfa_names(dfa)
        
        # Análisis del DFA original
        print(f"\nDFA Original: {len(dfa.states)} estados")
        analyze_dfa_structure(simple_dfa_orig)
        
        # Validación funcional del DFA original
        is_valid_orig = validate_dfa_for_regex(simple_dfa_orig, expr)
        
        # VALIDACIÓN DEL DFA MINIMIZADO
        print("\n" + "="*60)
        print("🔍 VALIDACIÓN DEL DFA MINIMIZADO")
        print("="*60)
        
        # Crear versión con nombres simples para análisis
        simple_dfa_min, _ = create_simple_dfa_names(dfa_min)
        
        # Análisis estructural del DFA minimizado
        print(f"\nDFA Minimizado: {len(dfa_min.states)} estados")
        analyze_dfa_structure(simple_dfa_min)
        
        # Validación funcional del DFA minimizado
        is_valid_min = validate_dfa_for_regex(simple_dfa_min, expr)
        
        if not is_valid_orig and not is_valid_min:
            print("\n❌ ADVERTENCIA: Tanto el DFA original como el minimizado fallan!")
        elif not is_valid_orig:
            print("\n❌ ADVERTENCIA: El DFA original falla pero el minimizado está correcto!")
        elif not is_valid_min:
            print("\n❌ ADVERTENCIA: El DFA minimizado falla pero el original está correcto!")
        else:
            print("\n✅ Ambos DFAs están correctos!")
        
        print("\n" + "="*60)
        
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
                print("  ADVERTENCIA: Los autómatas no son equivalentes!")
            else:
                print("✓ Todos los autómatas son equivalentes")
            
            # Resultado final claro
            resultado = "PERTENECE" if nfa_result else "NO PERTENECE"
            simbolo = "✓" if nfa_result else "✗"
            print(f"\n{simbolo} RESULTADO: La cadena '{word}' {resultado} al lenguaje de la expresión regular '{expr}'")
        
        if not no_graphs:
            print(f"Archivos: tree_simplified_{idx}.png, nfa_{idx}.png, dfa_{idx}.png, dfa_min_{idx}.png")
        
        return True
        
    except Exception as e:
        print(f" Error procesando '{expr}': {e}")
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
    
    print(f"\n Resumen: {success_count}/{total_count} expresiones procesadas exitosamente")
    return success_count, total_count


def procesar_archivo_con_cadenas(regex_path, strings_path, cross_test=False, verbose=False, no_graphs=False, outdir="outputs"):
    """
    Procesa archivo de expresiones regulares con archivo de cadenas.
    
    Si cross_test=True: Cada expresión se prueba con cada cadena (modo matriz)
    Si cross_test=False: La i-ésima expresión se prueba con la i-ésima cadena
    """
    # Cargar expresiones regulares
    with open(regex_path, encoding='utf-8') as f:
        expressions = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # Cargar cadenas
    with open(strings_path, encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    
    success_count = 0
    total_count = 0
    
    if cross_test:
        print(f"\n=== MODO PRUEBA CRUZADA ===")
        print(f"Probando {len(expressions)} expresiones × {len(words)} cadenas = {len(expressions) * len(words)} combinaciones\n")
        
        # Crear tabla de resultados
        results = []
        headers = ["Expresión"] + [f"'{w}'" for w in words]
        
        for i, expr in enumerate(expressions):
            print(f"\n--- Expresión {i+1}/{len(expressions)}: {expr} ---")
            row = [expr]
            
            for j, word in enumerate(words):
                total_count += 1
                print(f"  Probando con '{word}'...")
                
                try:
                    # Procesamiento silencioso para la matriz
                    expr2 = expand_plus_question(expr)
                    tokens = insert_concatenation(expr2)
                    postfix, _ = shunting_yard(tokens)
                    root = build_syntax_tree(postfix)
                    nfa = thompson_from_ast(root)
                    nfa = renumber_nfa(nfa, make_accept_last=True)
                    
                    # Solo simulamos en AFN para rapidez
                    result = simulate_nfa(nfa, word)
                    row.append("✓" if result else "✗")
                    
                    if result:
                        success_count += 1
                        print(f"    ✓ ACEPTA")
                    else:
                        print(f"    ✗ RECHAZA")
                        
                except Exception as e:
                    row.append("ERROR")
                    print(f"    ERROR: {e}")
            
            results.append(row)
        
        # Mostrar tabla resumen
        print(f"\n=== TABLA RESUMEN ===")
        print(f"{'Expresión':<30} | " + " | ".join([f"{w:<8}" for w in words]))
        print("-" * (32 + len(words) * 11))
        
        for row in results:
            expr_short = (row[0][:27] + "...") if len(row[0]) > 30 else row[0]
            print(f"{expr_short:<30} | " + " | ".join([f"{r:<8}" for r in row[1:]]))
    
    else:
        print(f"\n=== MODO SECUENCIAL ===")
        print(f"Procesando {max(len(expressions), len(words))} pares expresión-cadena\n")
        
        max_pairs = max(len(expressions), len(words))
        
        for i in range(max_pairs):
            expr = expressions[i] if i < len(expressions) else expressions[-1]  # Reusar última expresión
            word = words[i] if i < len(words) else words[-1]  # Reusar última cadena
            
            total_count += 1
            
            if procesar_expresion_completa(expr, word, i+1, verbose, no_graphs, outdir):
                success_count += 1
    
    print(f"\n Resumen: {success_count}/{total_count} pruebas exitosas")
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


def create_parser():
    """Crea parser de argumentos CLI"""
    parser = argparse.ArgumentParser(
        description="Proyecto 1 - Teoría de la Computación: AFN/AFD desde expresiones regulares",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python Proyecto1.py --regex "(b|b)*abb(a|b)*" --word "babbaaaa"
  python Proyecto1.py --regex-file expresiones.txt --word-file cadena.txt
  python Proyecto1.py --regex-file expresiones.txt --word-file cadena.txt --cross-test
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
    parser.add_argument("--word-file", "--strings-file", help="Archivo con cadenas a verificar (una por línea)")
    parser.add_argument("--cross-test", action="store_true", help="Probar cada expresión con cada cadena (modo matriz)")
    parser.add_argument("--epsilon", default="ε", help="Símbolo para épsilon (default: ε)")
    
    # Opciones de salida
    parser.add_argument("--outdir", default="outputs", help="Directorio de salida (default: outputs)")
    parser.add_argument("--no-graphs", action="store_true", help="No generar gráficos")
    
    # Opciones adicionales
    parser.add_argument("--verbose", "-v", action="store_true", help="Modo verboso")
    
    return parser


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
        print(" Error: Debe especificar --regex, --regex-file o --interactive")
        parser.print_help()
        return
    
    # Validar combinaciones
    if args.word and args.word_file:
        print(" Error: No se puede especificar tanto --word como --word-file")
        parser.print_help()
        return
    
    if args.cross_test and not (args.regex_file and args.word_file):
        print(" Error: --cross-test requiere tanto --regex-file como --word-file")
        parser.print_help()
        return
    
    # Crear directorio de salida
    if not args.no_graphs:
        os.makedirs(args.outdir, exist_ok=True)
    
    # Procesar expresión individual
    if args.regex:
        # Determinar palabra a usar
        word = args.word
        if args.word_file:
            with open(args.word_file, encoding='utf-8') as f:
                words = [line.strip() for line in f if line.strip()]
                word = words[0] if words else None
        
        success = procesar_expresion_completa(
            args.regex, 
            word, 
            1, 
            args.verbose, 
            args.no_graphs, 
            args.outdir
        )
        
        if success:
            print(f"\n Expresión procesada exitosamente")
            if not args.no_graphs:
                print(f" Archivos guardados en: {os.path.abspath(args.outdir)}")
        else:
            print(f"\n Error procesando la expresión")
            sys.exit(1)
    
    # Procesar archivo de expresiones
    elif args.regex_file:
        if not os.path.exists(args.regex_file):
            print(f" Error: El archivo '{args.regex_file}' no existe")
            sys.exit(1)
        
        if args.word_file:
            if not os.path.exists(args.word_file):
                print(f" Error: El archivo '{args.word_file}' no existe")
                sys.exit(1)
            
            # Usar nueva función con archivo de cadenas
            success_count, total_count = procesar_archivo_con_cadenas(
                args.regex_file,
                args.word_file,
                args.cross_test,
                args.verbose,
                args.no_graphs,
                args.outdir
            )
        else:
            # Usar función original
            success_count, total_count = procesar_archivo(
                args.regex_file, 
                None,  # strings_path 
                args.verbose, 
                args.no_graphs, 
                args.outdir
            )
        
        if not args.no_graphs and success_count > 0:
            print(f" Archivos guardados en: {os.path.abspath(args.outdir)}")
