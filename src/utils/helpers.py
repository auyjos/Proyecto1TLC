"""
Funciones auxiliares y utilidades
"""
import sys as _sys
import time
from contextlib import contextmanager


@contextmanager
def _timer():
    start = time.perf_counter()
    yield lambda: (time.perf_counter() - start)


def ask_yes_no(prompt: str, default_no: bool = True) -> bool:
    """Pregunta s/n. True si 's', False si 'n' o vacío según default."""
    if not _sys.stdin.isatty():
        return not default_no
    suf = "[s/N]" if default_no else "[S/n]"   # <--- aquí estaba el error
    try:
        ans = input(f"{prompt} {suf} ").strip().lower()
    except EOFError:
        return not default_no
    if ans in ("s", "si", "sí", "y", "yes"): return True
    if ans in ("n", "no"): return False
    return not default_no
