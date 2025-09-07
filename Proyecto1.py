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
import os
import sys

# Importar la funcionalidad CLI
from src.cli.commands import main, procesar_archivo

if __name__ == '__main__':
    # Compatibilidad con uso original
    if len(sys.argv) >= 2 and not sys.argv[1].startswith('-'):
        # Modo original: python Proyecto1.py expresiones.txt [cadenas.txt]
        regex_path = sys.argv[1]
        strings_path = sys.argv[2] if len(sys.argv) == 3 else None
        
        if not os.path.exists(regex_path):
            print(f" Error: El archivo '{regex_path}' no existe")
            sys.exit(1)
        
        procesar_archivo(regex_path, strings_path, verbose=True, no_graphs=False)
    else:
        main()
