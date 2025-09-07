"""
Preprocesamiento de expresiones regulares
"""


def expand_plus_question(expr: str) -> str:
    """Expande + y ? a sus formas equivalentes con * y |"""
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


def insert_concatenation(expr: str):
    """Inserta operadores de concatenación explícitos '.' donde sea necesario"""
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
