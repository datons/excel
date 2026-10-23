# Auditar el libro y la macro

`uv run scripts/describe.py <libro>` imprime las hojas (tamaño, cabecera, fórmulas con sus patrones), los nombres definidos y el código VBA de cada módulo. Léelo entero antes de proponer nada.

## Qué debe quedar en docs/<process>.md

- **Propósito**: qué responde el proceso y quién lo usa, en una frase.
- **Entradas**: cada hoja, rango o celda que lee, con su significado, unidad y tipo.
- **Parámetros**: las celdas que el usuario cambia (coeficientes, fechas, opciones).
- **Salidas**: dónde escribe y qué significa cada columna.
- **Reglas**: el cálculo paso a paso, en lenguaje del negocio.
- **Casos especiales**: qué hace con vacíos, ceros, fechas raras, filas que faltan.
- **Rarezas**: comportamientos que un port ingenuo cambiaría sin querer (lista de abajo).
- **Plan**: módulos y orden de migración, y qué casos de referencia vas a sacar.

## La propuesta: docs/<process>-proposal.html

El usuario confirma la migración sobre esta página, no sobre un plan en el chat. Debe poder revisarse de un vistazo y abrirse sin conexión: un único fichero HTML con el CSS dentro, los diagramas en SVG dentro del propio fichero y sin librerías, fuentes ni CDN externos (en muchas redes corporativas están bloqueados). Ábrela al terminar (`open` en macOS, `start` en Windows).

- **Árbol del proyecto**: las carpetas y ficheros de «Dónde va cada cosa» que vas a crear o cambiar, marcando cuáles son nuevos.
- **Modelo de datos**: cada entrada y cada salida como una tabla con sus columnas, tipo, unidad y origen (hoja y rango del libro, o la tabla de la que se exporta). Señala las claves y cómo se unen las tablas.
- **Diagrama del proceso**: de las entradas a las salidas, paso a paso, con las reglas y las rarezas en el punto donde actúan.
- **Casos de referencia**: cada caso que vas a sacar de Excel, normal o límite, con sus entradas y el resultado esperado si el usuario lo conoce. Son lo que demostrará que la migración es correcta.
- **Pantallas**: solo si se va a hacer el paso 6 o el usuario lo pide, una maqueta de la pantalla del formulario con sus campos y validaciones.
- **Plan**: módulos y orden de migración, y lo que queda fuera.

Datos de ejemplo, nunca de clientes ni personales: la propuesta se comparte.

## Rarezas típicas de VBA y Excel

- **`Round` de VBA** redondea al par (2,5 → 2), igual que `round` de Python sobre el valor binario; `ROUND` de las fórmulas de Excel redondea hacia arriba (2,5 → 3). Comprueba cuál usa el proceso antes de elegir `round` o `Decimal.quantize(ROUND_HALF_UP)`.
- **Redondear por línea y luego sumar** no da lo mismo que sumar y redondear al final.
- **Celdas vacías**: `IsEmpty` distingue vacío de cero, pero una fórmula sobre una celda vacía devuelve 0. Lee siempre el dato original, no la columna calculada.
- **Búsquedas que no encuentran**: muchas macros devuelven 0 en silencio. Mantén el 0 para que los tests cuadren, pero hazlo visible (una lista de avisos en el resultado).
- **Fechas**: Excel guarda números de serie; `openpyxl` devuelve `datetime`. Los días con 23 o 25 horas (cambio de hora) rompen los bucles que asumen 24.
- **Tipos de VBA**: `Integer` es de 16 bits (desborda en 32.767), `Long` de 32; la división `\` es entera; `Variant` mezcla texto y número.
- **Estado oculto**: hojas ocultas, nombres definidos, celdas con formato que cambia el valor mostrado pero no el guardado.
- **Rendimiento**: búsquedas fila a fila dentro de bucles. No lo optimices en el port hasta que los tests pasen.

## Codificación del código VBA

El editor de VBA lee los `.bas` en la codificación local (MacRoman en Mac, cp1252 en Windows). Si exportas o reescribes un módulo, déjalo en ASCII: cualquier acento aparece corrupto en el otro sistema.

## Macros grandes

Si el código no cabe cómodo en el contexto, trocea por módulos: lista cada procedimiento con lo que lee, escribe y llama; migra primero las hojas del árbol de llamadas y sube. Cada módulo migrado lleva sus casos y sus tests antes de pasar al siguiente.
