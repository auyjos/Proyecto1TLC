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

# Ejemplo individual del proyecto
python main.py -r "(b|b)*abb(a|b)*" -w "babbaaaa"

# Procesar archivo de expresiones
python main.py --regex-file expresiones.txt --outdir outputs/

# Sin generar gráficos (más rápido)
python main.py -r "a*b*" -w "aaabbb" --no-graphs
```

---

## 📋 Opciones de Línea de Comandos

### Entrada
- `-r, --regex` : Expresión regular individual
- `--regex-file` : Archivo con expresiones (una por línea)
- `-w, --word` : Cadena a verificar (opcional)
- `--epsilon` : Símbolo para ε (default: ε)

### Salida  
- `--outdir` : Directorio de salida (default: outputs)
- `--format` : Formato de imágenes: png|svg (default: png)
- `--no-graphs` : No generar gráficos
- `--save-info` : Guardar información en archivo de texto

### Otras
- `-v, --verbose` : Información detallada
- `--test-equivalence` : Probar equivalencia entre autómatas

---

## 📁 Estructura del Proyecto

```
Proyecto1TLC/
├── main.py                  # Punto de entrada principal
├── Proyecto1.py             # Implementación original (legacy)
├── requirements.txt         # Dependencias
├── expresiones.txt          # Ejemplos de expresiones regulares
├── README.md               # Este archivo
├── src/                    # Código fuente modular
│   ├── __init__.py
│   ├── cli.py              # Interfaz de línea de comandos
│   ├── types.py            # Estructuras de datos (NFA, DFA)
│   ├── parser_infix.py     # Infix → Postfix (Shunting Yard)
│   ├── thompson.py         # Construcción de AFN (Thompson)
│   ├── subset_construction.py # AFN → AFD (Subconjuntos)
│   ├── minimize.py         # Minimización de AFD
│   ├── simulate.py         # Simulación de autómatas
│   └── graphviz_utils.py   # Generación de gráficos
├── tests/                  # Pruebas unitarias
│   ├── __init__.py
│   ├── test_parser.py      # Pruebas del parser
│   ├── test_thompson.py    # Pruebas de Thompson
│   └── test_simulate.py    # Pruebas de simulación
└── outputs/                # Directorio de salida (generado)
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

## 🧪 Pruebas

```bash
# Ejecutar todas las pruebas
python -m pytest tests/ -v

# Pruebas específicas
python -m pytest tests/test_parser.py -v
python -m pytest tests/test_thompson.py -v
python -m pytest tests/test_simulate.py -v
```

---

## 📝 Formato de Archivo de Expresiones

El archivo `expresiones.txt` debe contener una expresión regular por línea:

```
(a*|b*)+
((ε|a)|b*)*
(a|b)*abb(a|b)*
a+b?c*
# Esto es un comentario
(0|1)*1(0|1)*
```

- Líneas vacías y comentarios (`#`) son ignorados
- Soporte para escape: `\(`, `\*`, etc.
- Épsilon configurable (default: `ε`)

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

- **Validación de entrada**: Detecta errores de sintaxis en expresiones regulares
- **Numeración consistente**: Estados AFN numerados secuencialmente (1, 2, 3...)
- **Optimización**: AFD minimizado siempre equivalente al original
- **Formato flexible**: Salida en PNG o SVG
- **Modo verboso**: Información detallada del proceso de construcción
- **Verificación automática**: Prueba equivalencia entre autómatas

---

## 🏆 Cumplimiento de Requisitos

| Característica | ✅ | Implementación |
|---|---|---|
| Shunting Yard (infix→postfix) | ✅ | `src/parser_infix.py` |
| AFN con Thompson | ✅ | `src/thompson.py` |
| AFD por subconjuntos | ✅ | `src/subset_construction.py` |
| **Minimización de AFD** | ✅ | `src/minimize.py` |
| **Simulación** (AFN y AFDs) | ✅ | `src/simulate.py` |
| **Gráficos** de autómatas | ✅ | `src/graphviz_utils.py` |
| **CLI completa** | ✅ | `main.py` + `src/cli.py` |
| **Procesamiento por lotes** | ✅ | `--regex-file` |
| **Pruebas unitarias** | ✅ | `tests/` |

**Total: 15/15 puntos** 🎯

---

## 👥 Créditos

**Proyecto 1 — Teoría de la Computación**  
Universidad del Valle de Guatemala  
Agosto 2025

**Repositorio:** [https://github.com/auyjos/Proyecto1TLC](https://github.com/auyjos/Proyecto1TLC)

---

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles.
