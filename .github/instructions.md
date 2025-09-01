# Proyecto 1 — Teoría de la Computación

Analizador léxico (parte inicial): construcción de **AFN/AFD** a partir de **expresiones regulares** y verificación de pertenencia de cadenas.

> Fuente de requisitos oficiales: curso “Teoría de la Computación”, Agosto 2025 — Proyecto 1. fileciteturn0file0

---

## 1) Descripción y objetivos

Este proyecto recopila trabajo de laboratorios previos y añade componentes nuevos para completar la parte inicial de un analizador léxico. El programa debe:

1. **Convertir** una expresión regular `r` de **notación infix** a **notación postfix** (algoritmo **Shunting Yard**).
2. **Construir un AFN** a partir de la ER en postfix (**Thompson**).
3. **Convertir AFN → AFD** (algoritmo de **subconjuntos**).
4. **Minimizar el AFD** (algoritmo de **minimización de estados**; se sugiere **Hopcroft** o particiones refinadas).
5. **Simular** AFN y AFD(s) sobre una cadena `w` e indicar si `w ∈ L(r)`.

El sistema también debe **leer un archivo de texto** con **una ER por línea** y procesar cada una.

---

## 2) Alcance funcional (requisitos obligatorios)

* **Entrada interactiva/CLI**: admite al menos (a) una ER `r` y (b) una cadena `w`.
* **Transformación**: infix → postfix usando Shunting Yard.
* **Construcción de AFN**: algoritmo de Thompson, estados, transiciones (incluye ε-transiciones) y estado(s) de aceptación.
* **AFD por subconjuntos**: construcción *powerset* desde el AFN, con cerraduras-ε y etiquetado de estados.
* **Minimización de AFD**: generar un AFD mínimo equivalente.
* **Verificación de pertenencia**: simular AFN y AFD(s) con `w` y reportar **“sí”** (acepta) o **“no”** (rechaza).
* **Procesamiento por lotes**: leer **archivo de texto** (una ER por línea) y repetir el pipeline para cada ER.
* **Símbolo ε**: seleccionable por quien programa (debe ser **razonable**, no un carácter común que interfiera con otras partes del proyecto).
* **Repositorio**: el proyecto debe vivir en un **repositorio de GitHub**.

---

## 3) Salidas requeridas

1. **Imágenes de grafos** para:

   * **AFN** (desde Thompson)
   * **AFD** (por subconjuntos) y **AFD minimizado**

   Cada imagen **debe** mostrar: estado inicial, estados adicionales, estado(s) de aceptación y **todas** las transiciones con sus símbolos.

2. **Resultados de simulación**:

   * Para el **AFN** y para **cada AFD** (original y minimizado), indicar si `w ∈ L(r)` → imprimir **“sí”** o **“no”**.

3. **Procesamiento de archivo**:

   * Para cada línea (ER) en el archivo de entrada, generar sus salidas correspondientes (imágenes + resultado de simulación, y/o un resumen tabular).

---

## 4) Especificación de Entrada/Salida

### Entrada

* `r`: expresión regular en **notación infix**. Ejemplo del enunciado:

  * `r = (b|b)*abb(a|b)*`
* `w`: cadena a verificar. Ejemplo del enunciado:

  * `w = babbaaaa`
* **Archivo de ERs**: texto plano (`.txt`), **una ER por línea** (sin la cadena `w` obligatoria; puedes definir un modo de solo construcción de autómatas o admitir `w` opcional por CLI).

**Nota sobre `ε`**: define un token único (p. ej. `ε`, `eps` o `#`) y **documenta** su uso. Evita letras/dígitos comunes.

### Salida

* Archivos de imagen **(PNG/SVG)** de los grafos de AFN, AFD y AFD minimizado.
* Mensajes de consola/archivo con el veredicto de pertenencia por autómata: `sí`/`no`.
* (Opcional) Un **reporte** por ER (por ejemplo, `report_<indice>.md` o `csv`) con métricas: nº de estados, nº de transiciones, tiempo de construcción.

---

## 5) Interfaz de línea de comandos (sugerida)

```bash
# Caso unitario con ER y cadena
python main.py --regex "(b|b)*abb(a|b)*" --word "babbaaaa" \
               --epsilon "ε" \
               --outdir outputs/caso1

# Procesamiento por archivo (una ER por línea)
python main.py --regex-file data/expresiones.txt --epsilon "ε" --outdir outputs/lote

# Bandera para omitir imágenes (si solo deseas simular)
python main.py --regex "a(b|c)*" --word "abcb" --no-graphs
```

**Parámetros recomendados**:

* `--regex` / `-r` : ER en infix.
* `--word` / `-w` : cadena `w` (opcional si solo construyes autómatas).
* `--regex-file` : ruta a archivo con ERs por línea.
* `--epsilon` : símbolo/tokens para ε (por defecto `ε`).
* `--outdir` : carpeta de salida (imágenes y reportes).
* `--format` : `png` o `svg`.
* `--no-graphs` : no generar imágenes.
* `--verbose` : logs detallados.

---

## 6) Estructura del repositorio (sugerida)

```
Proyecto1/
├─ README.md
├─ requirements.txt
├─ src/
│  ├─ cli.py                # parsing de argumentos
│  ├─ parser_infix.py       # tokenizer + shunting yard → postfix
│  ├─ thompson.py           # ER (postfix) → AFN
│  ├─ subset_construction.py# AFN → AFD
│  ├─ minimize.py           # AFD → AFD mínimo (Hopcroft / particiones)
│  ├─ simulate.py           # simulaciones AFN/AFD
│  ├─ graphviz_utils.py     # render de grafos
│  └─ types.py              # estructuras de datos
├─ data/
│  └─ expresiones.txt       # ERs de ejemplo (una por línea)
├─ outputs/
│  └─ ...                   # imágenes y reportes generados
├─ tests/
│  ├─ test_parser.py
│  ├─ test_thompson.py
│  ├─ test_subset.py
│  ├─ test_minimize.py
│  └─ test_simulate.py
└─ main.py
```

---

## 7) Detalle de algoritmos requeridos

### 7.1 Shunting Yard (infix → postfix)

* Maneja **precedencia** y **asociatividad** de operadores (p. ej., `*`, concatenación `·` implícita, `|`, paréntesis).
* Sugerencia: **explicitar concatenación** en un paso previo (insertar `·`).
* Soporta **cerradura Kleene** `*`, **opcional** `?`, **uno o más** `+` (si decides incluirlos; documenta el set soportado).

### 7.2 Thompson (postfix → AFN)

* Cada símbolo genera un fragmento básico.
* Operadores:

  * **Concatenación**: conecta aceptación de A con inicio de B.
  * **Alternativa `|`**: nuevo inicio con ε a A y B; nuevas ε desde aceptaciones a un nuevo final.
  * **Kleene `*`**: lazo ε desde final a inicio, y ε desde inicio a final; admite cadena vacía.
  * (Si implementas `+`, `?` ajusta los fragmentos en consecuencia.)
* Produce **estado inicial**, **conjunto de aceptaciones** y **transiciones** etiquetadas (incluye ε).

### 7.3 Subconjuntos (AFN → AFD)

* Usa **ε-cerradura** para construir estados deterministas como conjuntos de estados del AFN.
* Genera transiciones deterministas para cada símbolo del alfabeto.
* Marca como aceptaciones los subconjuntos que contengan algún estado de aceptación del AFN.

### 7.4 Minimización de AFD

* Implementa **refinamiento de particiones** (Hopcroft) o algoritmo clásico de **tabla de indistinguibilidad**.
* Asegura **equivalencia** con el AFD original.

### 7.5 Simulación

* **AFN**: recorrido con ε-cerraduras + avance por símbolo.
* **AFD/AFD mínimo**: transición determinista; `sí` si se termina en estado de aceptación.
* Reporta para **cada autómata**: `sí` / `no`.

---

## 8) Generación de imágenes de grafos

* Utiliza **Graphviz** (`dot`) o librerías (p. ej., `graphviz`, `pydot`) para renderizar.
* Convenciones sugeridas:

  * Estado inicial con **flecha entrante** desde nodo fantasma.
  * Estados de aceptación con **doble círculo**.
  * Etiquetas de transición como `a`, `b`, `ε`.
* Nombres de archivo:

  * `AFN_<hash|indice>.{png,svg}`
  * `AFD_<hash|indice>.{png,svg}`
  * `AFDmin_<hash|indice>.{png,svg}`

---

## 9) Validaciones y manejo de errores

* **Tokenización** robusta: rechaza símbolos no válidos en la ER.
* **Paréntesis** balanceados, operadores en posiciones válidas, alfabeto consistente.
* **Símbolo ε** consistente y documentado.
* **Archivo de ERs**: ignora líneas vacías/comentarios (`# ...`).
* Mensajes claros: indica la causa en errores de sintaxis o construcción.

---

## 10) Pruebas (sugerencias)

* Unitaria por módulo (parser, Thompson, subconjuntos, minimización, simulación).
* Casos clásicos:

  * `a*b*`, `(a|b)*`, `ab|a`, `a(b|c)*`, `ε`, `∅` (si la soportas), `a+`, `a?`.
* Verifica equivalencias: AFD vs AFDmin aceptan lo mismo.
* Compara simulación AFN vs AFD con múltiples `w`.

---

## 11) Ejemplo mínimo (tomado del enunciado)

* `r = (b|b)*abb(a|b)*`
* `w = babbaaaa`
* Salidas esperadas:

  * Imágenes: `AFN`, `AFD`, `AFDmin`.
  * Simulación: imprimir **“sí”**/**“no”** para AFN, AFD y AFDmin.

> Este ejemplo se menciona explícitamente en el enunciado del proyecto. fileciteturn0file0

---

## 12) Ponderación oficial

| Característica                | Puntos |
| ----------------------------- | -----: |
| Shunting Yard (infix→postfix) |      3 |
| AFN con Thompson              |      3 |
| AFD por subconjuntos          |      3 |
| **Minimización de AFD**       |      3 |
| **Simulación** (AFN y AFDs)   |      3 |
| **Total**                     | **15** |

> Tabla reproducida del enunciado oficial. fileciteturn0file0

---

## 13) Dependencias y entorno (sugerido)

* **Python 3.10+**
* `graphviz` (binario del sistema) y `pip install graphviz` o `pydot`
* `pytest` para pruebas

Archivo `requirements.txt` ejemplo:

```
graphviz
pydot
pytest
```

---

## 14) Cómo correr

```bash
# Instalar dependencias
pip install -r requirements.txt

# Construir y simular para una ER/cadena\ npython main.py -r "(b|b)*abb(a|b)*" -w "babbaaaa" --epsilon "ε" --outdir outputs/caso1

# Procesar archivo de ERs
python main.py --regex-file data/expresiones.txt --outdir outputs/lote
```

---

## 15) Notas de implementación

* Define claramente el **alfabeto** permitido en la ER.
* Documenta cualquier **extensión** soportada (p. ej., `+`, `?`).
* Asegura que la **concatenación** esté explícita en el parser antes del Shunting Yard.
* En gráficos, usa nombres deterministas para estados del AFD minimizado (p. ej., `q0, q1, ...`).

---

## 16) Licencia y crédito

* Incluye una **licencia** (MIT/GPL-3.0) en el repositorio.
* Agradecimientos al curso y docentes.

**Referencia del enunciado**: Proyecto 1 — Teoría de la Computación (Agosto, 2025). fileciteturn0file0
