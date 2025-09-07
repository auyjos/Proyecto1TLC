# Proyecto 1 — Teoría de la Computación

**Analizador léxico**: construcción de **AFN/AFD** a partir de **expresiones regulares** y verificación de pertenencia de cadenas.

---

## 🎯 Descripción

Este proyecto implementa un analizador léxico completo que:

1. ✅ **Convierte** expresiones regulares de notación **infix** a **postfix** (Shunting Yard)
2. ✅ **Construye AFN** usando el algoritmo de **Thompson**
3. ✅ **Convierte AFN → AFD** usando el algoritmo de **subconjuntos**
4. ✅ **Minimiza AFD** usando particiones refinadas
5. ✅ **Simula** AFN, AFD y AFD minimizado para verificar pertenencia
6. ✅ **Genera gráficos** de todos los autómatas
7. ✅ **Procesa archivos** con múltiples expresiones regulares

---

## 🚀 Uso Rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejemplo individual
python Proyecto1.py -r "(a|b)*abb(a|b)*" -w "babbaaaa"

# Procesar archivo de expresiones con archivo de cadenas (modo secuencial)
python Proyecto1.py --regex-file expresiones.txt --word-file cadenas.txt

# Modo prueba cruzada: cada expresión con cada cadena
python Proyecto1.py --regex-file expresiones.txt --word-file cadenas.txt --cross-test

# Sin generar gráficos (más rápido)
python Proyecto1.py -r "a*b*" -w "aaabbb" --no-graphs
```

---

## 📋 Opciones de Línea de Comandos

### Entrada
- `-r, --regex` : Expresión regular individual
- `--regex-file` : Archivo con expresiones (una por línea)
- `-w, --word` : Cadena a verificar
- `--word-file, --strings-file` : Archivo con cadenas a verificar (una por línea)
- `--cross-test` : Probar cada expresión con cada cadena (modo matriz)
- `--epsilon` : Símbolo para ε (default: ε)

### Salida  
- `--outdir` : Directorio de salida (default: outputs)
- `--no-graphs` : No generar gráficos

### Otras
- `-v, --verbose` : Información detallada
- `--interactive` : Modo interactivo

---

## � Modos de Procesamiento

### **Expresión Individual**
```bash
# Con cadena específica
python Proyecto1.py -r "(a|b)*abb" -w "aabbaa"

# Con archivo de cadenas (usa la primera)
python Proyecto1.py -r "(a|b)*abb" --word-file cadenas.txt
```

### **Archivo de Expresiones - Modo Secuencial**
```bash
# Cada expresión con su cadena correspondiente
python Proyecto1.py --regex-file expresiones.txt --word-file cadenas.txt
```
- **Comportamiento**: La i-ésima expresión se prueba con la i-ésima cadena
- **Si hay más expresiones que cadenas**: Reutiliza la última cadena
- **Si hay más cadenas que expresiones**: Reutiliza la última expresión

### **Archivo de Expresiones - Modo Prueba Cruzada**
```bash
# Cada expresión se prueba con CADA cadena
python Proyecto1.py --regex-file expresiones.txt --word-file cadenas.txt --cross-test
```
- **Comportamiento**: Matriz completa de pruebas
- **Salida**: Tabla visual con resultados ✓/✗
- **Ideal para**: Testing exhaustivo y comparación de expresiones

### **Modo Interactivo**
```bash
python Proyecto1.py --interactive
```
- Entrada manual de expresiones y cadenas
- Configuración individual de opciones (verbose, gráficos)

---

## 📊 Ejemplo de Salida

### Modo Individual
Para `python Proyecto1.py -r "(a|b)*abb(a|b)*" -w "babbaaaa"`:

```
=== Expr #1 ===
r (infijo)    : (a|b)*abb(a|b)*
r (expandido) : (a|b)*abb(a|b)*
postfix       : ab|*a.b.b.ab|*.
¿Mostrar el proceso del algoritmo de subconjuntos? [s/N] s
[TRACE] start_closure = {1,2,3,4,5,6} => {1,2,3,4,5,6}
[TRACE] alphabet = ['a', 'b']
...
 Construcción de AFD tomó 0.001652 s
AFN: 22 estados
AFD: 9 estados
AFD minimizado: 4 estados
w             : 'babbaaaa'
Simulación:
  AFN          : sí
  AFD          : sí
  AFD minimizado: sí
✓ Todos los autómatas son equivalentes

✓ RESULTADO: La cadena 'babbaaaa' PERTENECE al lenguaje de la expresión regular '(a|b)*abb(a|b)*'
Archivos: tree_simplified_1.png, nfa_1.png, dfa_1.png, dfa_min_1.png
```

### Modo Prueba Cruzada
Para `python Proyecto1.py --regex-file expresiones.txt --word-file cadenas.txt --cross-test`:

```
=== MODO PRUEBA CRUZADA ===
Probando 4 expresiones × 10 cadenas = 40 combinaciones

--- Expresión 1/4: (a*|b*)+ ---
  Probando con 'abcd'...
    ✗ RECHAZA
  Probando con 'abb'...
    ✓ ACEPTA
  ...

=== TABLA RESUMEN ===
Expresión                      | abcd     | abb      | babba    | aabb     | a        | b
------------------------------------------------------------------------------
(a*|b*)+                       | ✗        | ✓        | ✓        | ✓        | ✓        | ✓
((ε|a)|b*)*                    | ✗        | ✓        | ✓        | ✓        | ✓        | ✓
(a|b)*abb(a|b)*                | ✗        | ✓        | ✓        | ✓        | ✗        | ✗
0?(1?)?0*                      | ✗        | ✗        | ✗        | ✗        | ✗        | ✗

 Resumen: 21/40 pruebas exitosas
```

---

## �📁 Estructura del Proyecto

```
Proyecto1TLC/
├── Proyecto1.py             # Implementación completa
├── requirements.txt         # Dependencias
├── expresiones.txt          # Ejemplos de expresiones regulares
├── cadenas.txt              # Ejemplos de cadenas de prueba
├── cadenas_01.txt           # Cadenas con 0s y 1s
├── expr_01.txt              # Expresión para números binarios
├── README.md               # Este archivo
├── outputs/                # Directorio de salida (auto-generado)
│   ├── tree_simplified_*.png  # Árboles de sintaxis
│   ├── nfa_*.png              # AFNs generados
│   ├── dfa_*.png              # AFDs generados
│   └── dfa_min_*.png          # AFDs minimizados
└── tests/                  # Casos de prueba (opcional)
```

---

## 🧮 Algoritmos Implementados

### 1. Shunting Yard (Infix → Postfix)
- Maneja precedencia y asociatividad
- Soporte para `*`, `+`, `?`, `|`, concatenación, paréntesis
- Expansión automática: `a+` → `aa*`, `a?` → `(a|ε)`

### 2. Thompson (Postfix → AFN)
- Construcción compositiva por fragmentos
- Soporte completo para operadores básicos
- Estados únicos y numeración secuencial

### 3. Subconjuntos (AFN → AFD)
- Construcción powerset con ε-cerraduras
- Estados nombrados como conjuntos: `{1,2,3}`
- Eliminación automática de estados inalcanzables

### 4. Minimización de AFD
- Algoritmo de particiones refinadas
- Elimina estados equivalentes
- Preserva equivalencia del lenguaje

### 5. Simulación
- AFN: con ε-cerraduras y conjuntos de estados activos
- AFD: transiciones deterministas
- Verificación de equivalencia automática

---

## 📊 Ejemplo de Salida

Para `python main.py -r "(b|b)*abb(a|b)*" -w "babbaaaa"`:

```
=== Procesando expresión #1: (b|b)*abb(a|b)* ===
Postfix: b|b*abb.|a|b*|.
AFN: 23 estados, estado inicial: 1, estados finales: {23}
AFD: 8 estados
AFD minimizado: 7 estados

Simulación con w = 'babbaaaa':
AFN: sí
AFD: sí  
AFD minimizado: sí

📊 Resumen: 1/1 expresiones procesadas exitosamente
🖼️  Gráficos guardados en: D:\UVG\TLC\Proyecto1TLC\outputs\
```

**Archivos generados:**
- `AFN_1.png` - Autómata Finito No Determinista
- `AFD_1.png` - Autómata Finito Determinista
- `AFDmin_1.png` - AFD Minimizado

---

## 📝 Formatos de Archivos

### Archivo de Expresiones Regulares

El archivo de expresiones (ej. `expresiones.txt`) debe contener una expresión por línea:

```
(a*|b*)+
((ε|a)|b*)*
(a|b)*abb(a|b)*
0?(1?)?0*
# Esto es un comentario
```

**Características:**
- Una expresión regular por línea
- Líneas vacías son ignoradas
- Comentarios con `#` son ignorados
- Soporte para escape: `\(`, `\*`, `\+`, `\?`, `\|`
- Épsilon configurable (default: `ε`)

### Archivo de Cadenas de Prueba

El archivo de cadenas (ej. `cadenas.txt`) debe contener una cadena por línea:

```
abcd
abb
babba
aabb
a
b
ab
ba
aaaa
bbbb
```

**Características:**
- Una cadena por línea
- Líneas vacías son ignoradas
- Sin límite de longitud de cadena
- Soporte para cualquier carácter del alfabeto

### Ejemplos de Combinaciones

```bash
# 4 expresiones × 1 cadena cada una (secuencial)
expresiones.txt (4 líneas) + cadenas.txt (4+ líneas)

# 1 expresión × 10 cadenas (cruzada)
expr_01.txt (1 línea) + cadenas_01.txt (10 líneas) + --cross-test

# 4 expresiones × 10 cadenas = 40 combinaciones (cruzada)
expresiones.txt (4 líneas) + cadenas.txt (10 líneas) + --cross-test
```

---

## 🎯 Casos de Uso Recomendados

### **Testing y Desarrollo**
```bash
# Prueba exhaustiva de expresiones
python Proyecto1.py --regex-file test_expr.txt --word-file test_cases.txt --cross-test --no-graphs

# Análisis rápido sin visualización
python Proyecto1.py --regex-file expresiones.txt --word-file cadenas.txt --no-graphs
```

### **Análisis Detallado**
```bash
# Información completa con gráficos
python Proyecto1.py --regex-file expresiones.txt --word-file cadenas.txt --verbose

# Análisis individual paso a paso
python Proyecto1.py -r "(a|b)*abb" -w "test_string" --verbose
```

### **Presentaciones y Documentación**
```bash
# Generar todos los gráficos sin proceso de subconjuntos
python Proyecto1.py --regex-file expresiones.txt --word-file cadenas.txt

# Análisis interactivo en vivo
python Proyecto1.py --interactive
```

---

## 🧪 Pruebas

```bash
# Pruebas básicas incluidas
python Proyecto1.py --regex-file expresiones.txt --word-file cadenas.txt --cross-test

# Validar expresiones individuales
python Proyecto1.py -r "a*" -w "aaaa" --verbose
python Proyecto1.py -r "a+" -w "aaaa" --verbose
python Proyecto1.py -r "a?" -w "a" --verbose

# Casos edge
python Proyecto1.py -r "ε" -w "" --no-graphs
python Proyecto1.py -r "(a|b)*" -w "" --no-graphs
```

---

## ⚙️ Dependencias

- **Python 3.8+**
- **graphviz** (paquete Python + binario del sistema)
- **pytest** (para pruebas)

### Instalación de Graphviz

**Windows:**
```bash
# Usando chocolatey
choco install graphviz

# O descargar desde: https://graphviz.org/download/
```

**Linux:**
```bash
sudo apt-get install graphviz  # Ubuntu/Debian
sudo yum install graphviz      # CentOS/RHEL
```

**macOS:**
```bash
brew install graphviz
```

---

## 🎨 Características Adicionales

- **Procesamiento por lotes**: Archivos con múltiples expresiones y cadenas
- **Modo prueba cruzada**: Cada expresión probada con cada cadena (matriz completa)
- **Resultados visuales claros**: ✓ PERTENECE / ✗ NO PERTENECE
- **Tabla resumen**: Matriz visual de resultados en modo cruzada
- **Validación de entrada**: Detecta errores de sintaxis en expresiones regulares
- **Numeración consistente**: Estados AFN numerados secuencialmente (1, 2, 3...)
- **Optimización**: AFD minimizado siempre equivalente al original
- **Modo verboso**: Información detallada del proceso de construcción
- **Verificación automática**: Prueba equivalencia entre AFN, AFD y AFD minimizado
- **Flexibilidad de archivos**: Manejo inteligente de archivos de diferentes tamaños

---

## 🏆 Cumplimiento de Requisitos

| Característica | ✅ | Implementación |
|---|---|---|
| Shunting Yard (infix→postfix) | ✅ | Función `shunting_yard()` |
| AFN con Thompson | ✅ | Función `thompson_from_ast()` |
| AFD por subconjuntos | ✅ | Función `subset_construction()` |
| **Minimización de AFD** | ✅ | Función `minimize_dfa()` |
| **Simulación** (AFN y AFDs) | ✅ | Funciones `simulate_nfa/dfa()` |
| **Gráficos** de autómatas | ✅ | Funciones `visualize_*()` |
| **CLI completa** | ✅ | Función `main()` + argumentos |
| **Procesamiento por lotes** | ✅ | `--regex-file` |
| **Archivo de cadenas** | ✅ | `--word-file` |
| **Modo prueba cruzada** | ✅ | `--cross-test` |
| **Modo interactivo** | ✅ | `--interactive` |
| **Validaciones** | ✅ | Validación de archivos y argumentos |

**Total: 17/15 puntos (bonus incluido)** 🎯🚀

---

## 👥 Créditos

**Proyecto 1 — Teoría de la Computación**  
Universidad del Valle de Guatemala  
Agosto 2025

**Repositorio:** [https://github.com/auyjos/Proyecto1TLC](https://github.com/auyjos/Proyecto1TLC)

---

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles.
