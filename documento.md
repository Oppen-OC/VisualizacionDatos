# El mercado de Airbnb en Madrid

### Documento de diseño del dashboard

Visualización de Datos · Trabajo de evaluación
Datos: [Inside Airbnb](http://insideairbnb.com/) — Madrid, extracción de junio de 2026
Implementación: Streamlit (Python)

---

## 1. El problema abordado

El alquiler turístico de corta duración ha pasado, en poco más de una década, de ser un
intercambio entre particulares a convertirse en un **sector con operadores profesionales**.
En ciudades tensionadas como Madrid, esa transformación tiene consecuencias directas sobre el
precio de la vivienda, la convivencia vecinal y el cumplimiento de la normativa turística.

El debate público sobre el asunto suele apoyarse en **intuiciones y anécdotas**: que el centro
es carísimo, que los pisos caros son mejores, que los profesionales dan un servicio más
cuidado. Existen datos públicos para contrastar esas afirmaciones, pero están dispersos en
tres ficheros que suman cerca de **diez millones de filas**, un volumen que no se explora con
una hoja de cálculo.

**El problema concreto que aborda este trabajo:** no hay una vista única que permita responder,
sobre datos reales y de forma interactiva, a las cuatro preguntas que estructuran ese debate:

1. **¿Dónde** se concentra la oferta y cómo varía el precio geográficamente?
2. **¿Qué determina** realmente el precio de un anuncio?
3. **¿Cómo evoluciona** la demanda y qué estacionalidad tiene?
4. **¿Quién opera** la oferta, y qué consecuencias tiene su profesionalización?

El dashboard convierte esos diez millones de filas en respuestas comprobables, y —esto resultó
ser lo más valioso— permite **desmentir con datos** dos creencias extendidas: que pagar más
compra una experiencia mejor valorada, y que un operador profesional ofrece un servicio
superior. Ninguna de las dos se sostiene.

---

## 2. Usuarios del dashboard

El dashboard está diseñado para un perfil de usuario **analítico**, no para el viajero. No es
una herramienta de reserva ni de búsqueda de alojamiento: no permite contactar anuncios ni
comparar disponibilidad para unas fechas concretas.

### Usuario principal — Técnico de administración pública

Personal del área de urbanismo o turismo de un ayuntamiento, encargado de fundamentar o evaluar
la regulación del alquiler turístico.

| Necesita saber | Dónde lo resuelve |
|---|---|
| Dónde se concentra la presión turística | Mapa coroplético por barrio |
| Qué proporción de la oferta declara licencia y en qué zonas | Métrica de licencias en el mapa + desglose por distrito |
| Si el mercado está profesionalizado y en qué grado | Pestañas "Quién manda" y "Hosts profesionales" |
| Si la demanda crece o se estabiliza, y cuándo satura | Serie histórica + estacionalidad + calendario futuro |

Es el usuario que motiva las decisiones de diseño más restrictivas: necesita cifras
**defendibles**, no impactantes, porque puede tener que justificarlas públicamente.

### Usuario secundario A — Periodista de datos o investigador

Busca una narrativa respaldada por evidencia y, sobre todo, hallazgos **no evidentes**. Es el
destinatario natural de los recuadros de "dato que sorprende" y del ranking de tamaños de
efecto, que muestran qué explica realmente la valoración de un alojamiento.

Necesita además poder **verificar** lo que se le muestra: de ahí que cada afirmación fuerte del
dashboard vaya acompañada de su magnitud y de una nota sobre los factores de confusión
descartados.

### Usuario secundario B — Anfitrión particular

Quiere situar su alojamiento en el mercado: si su precio está alineado con su barrio y tipo, y
cómo compite frente a los grandes gestores. Los filtros laterales (distrito, tipo de
alojamiento, tamaño del anfitrión) le permiten reducir el conjunto a su situación concreta.

Para este usuario, el hallazgo sobre hosts profesionales tiene lectura práctica: su ventaja
competitiva no es el precio —los profesionales cobran menos por plaza— sino el **trato
personal**, que es justo lo que se degrada al escalar.

### Fuera del alcance

El **viajero** no es usuario de esta herramienta. Sus preguntas ("¿dónde me alojo el próximo
puente?") requieren búsqueda por fechas, fotos y contacto, funciones que corresponden a la
plataforma comercial y no a un cuadro de mando analítico.

---

## 3. Objetivos de diseño

### O1. Responder de un vistazo, ampliar bajo demanda

Cada pestaña abre con la respuesta —un titular afirmativo que enuncia el hallazgo, no una
etiqueta neutra— y desarrolla el detalle debajo. El usuario que solo mira los titulares se
lleva las conclusiones correctas; el que quiere comprobarlas encuentra las cifras.

Por eso los títulos son *"El precio lo marca el tamaño, no la calidad"* en lugar de
*"Correlaciones con el precio"*.

### O2. Separar lo que explica de lo que solo acompaña

Objetivo central y el que más condicionó el resultado final. Un dashboard que muestra
correlaciones sin su magnitud **induce a error**: con 16.000 anuncios, casi cualquier relación
resulta estadísticamente significativa aunque sea irrelevante.

Decisiones derivadas:

- Mostrar **tamaño de efecto** (varianza explicada), no solo la existencia de correlación.
- Contrastar factores entre sí en un mismo gráfico, para que el usuario vea cuál pesa más.
- Comparar siempre **dentro del mismo barrio y tipo** antes de dar por bueno un patrón.

### O3. No exagerar visualmente

Un eje truncado convierte una diferencia de 0,1 puntos sobre 5 en un titular. Durante el
desarrollo esto produjo un error real —descrito en la bitácora— que obligó a rehacer un bloque
completo de la pestaña de precio.

Regla adoptada: **si el dato crudo induce a error, no se grafica**. Se aplicó al descartar un
gráfico de ocupación por tamaño de anfitrión cuya mediana no es monótona y solo se ordena tras
el control estadístico; el dato se menciona en texto.

### O4. Permitir que cada usuario acote su ámbito

Cuatro filtros globales (distrito, tipo de alojamiento, tamaño del anfitrión, solo Superhosts)
que afectan a todas las vistas simultáneamente, de modo que la comparación se mantiene coherente
entre pestañas.

### O5. Un sistema visual único, legible y accesible

- **Paleta validada para daltonismo**: un azul como color de magnitud, una rampa secuencial de
  un solo tono para el mapa, y el par azul/rojo reservado **exclusivamente** para polaridad
  (positivo/negativo). El color nunca es decorativo.
- **Retícula editorial** de una sola columna con anchura máxima de lectura, jerarquía tipográfica
  serif/grotesca, y gráficos sin marco que se funden con el fondo.
- **Etiquetas directas** sobre las barras en lugar de ejes de valores, y un solo eje Y por
  gráfico (nunca ejes duales, que permiten sugerir correlaciones inexistentes).

### O6. Declarar las limitaciones en el propio dashboard

Las advertencias metodológicas viven en la interfaz, no en un anexo: el 15,5 % de anuncios sin
precio, las reseñas como *aproximación* de estancias, y que "declara licencia" no significa
licencia verificada. Un usuario que va a fundamentar una decisión debe conocer los límites del
dato mientras lo mira.

---

## 4. Datos que utiliza

### Origen

[Inside Airbnb](http://insideairbnb.com/), proyecto independiente y sin ánimo de lucro que
extrae y publica periódicamente información pública de los anuncios reales de la plataforma,
ciudad por ciudad, con el fin de permitir el estudio del impacto del alquiler turístico. Los
datos son de dominio público y su uso no requiere autorización.

**Extracción utilizada:** Madrid, junio de 2026.

### Volumen y contenido

| Fichero | Volumen | Contenido |
|---|---|---|
| `listings` | 22.708 anuncios × 90 columnas | Precio, capacidad, tipo, ubicación, valoraciones, datos del anfitrión, licencia |
| `reviews` | 1.419.360 reseñas (2010 – 2026) | Anuncio, fecha, autor y texto |
| `calendar` | 8.334.782 filas (jun 2026 – jul 2027) | Disponibilidad diaria y noches mínimas por anuncio |
| `neighbourhoods.geojson` | 128 barrios | Geometrías para el mapa coroplético |

### Preparación

El detalle completo está en `notebooks/01_exploracion_limpieza.ipynb` y en la bitácora. Las
decisiones con impacto sobre lo que se visualiza:

| Situación | Decisión | Motivo |
|---|---|---|
| 15,5 % de anuncios sin precio | **No imputar**, excluir de los análisis de precio | La ausencia no es aleatoria: son anuncios inactivos (3,1 reseñas/año frente a 18,8). Imputar habría inventado oferta inexistente |
| 11.070 reseñas duplicadas por (anuncio, fecha) | **No deduplicar** | Verificado: son reseñas distintas de dos huéspedes el mismo día. Deduplicar habría infracontado la demanda |
| Precios atípicos hasta 36.883 €/noche | Recorte del 1 % superior en análisis de precio | Distorsionaban medias y escalas |
| `minimum_nights ≥ 365` | Marcados como calendario bloqueado | No son alquileres reales |

### Datos que consume la aplicación

El dashboard **no lee los ficheros originales**. Un script de preparación
(`scripts/prepare_dashboard_data.py`) los pre-agrega a cuatro ficheros de ~2 MB en
`data/dashboard/`:

| Fichero | Contenido |
|---|---|
| `anuncios.parquet` | Una fila por anuncio, solo las columnas que usa la interfaz |
| `resenas_mes.parquet` | Reseñas por mes × distrito × tipo |
| `ocupacion.parquet` | Disponibilidad por fecha × distrito × tipo |
| `barrios.geojson` | Geometrías del mapa |

La razón es de diseño, no solo técnica: cargar 223 MB de reseñas y 8,3 millones de filas de
calendario hacía la aplicación **inutilizable de forma interactiva**, y un dashboard que tarda
en responder deja de ser una herramienta de exploración.

### Limitaciones conocidas

- Las **reseñas son una aproximación** de las estancias, no un registro de reservas: solo
  reseña una parte de los huéspedes, por lo que subestiman la ocupación real.
- En el calendario, "no disponible" **mezcla reservado y bloqueado** por el anfitrión: la
  ocupación calculada es un techo, no una cifra exacta.
- "Declara licencia" significa que el anuncio publica un número de registro; **no se ha podido
  verificar su validez** contra el registro oficial.
- Los datos son una **fotografía de un momento** (junio de 2026). Las series históricas
  proceden de las reseñas acumuladas, no de extracciones sucesivas.

---

## 5. Mockup

Boceto del diseño realizado a mano sobre papel, previo a la implementación:
**[`mockup.pdf`](mockup.pdf)** — una página por sección.

El boceto es deliberadamente poco detallado: no fija estilos ni colores, sino **qué
información mostrar, qué espacio ocupa cada bloque** y, al pie de cada página, anotaciones
sueltas con dudas y cosas a comprobar. Esas anotaciones acabaron dirigiendo buena parte del
desarrollo.

| Página | Sección esbozada | Bloques previstos |
|---|---|---|
| 1 | Mapa | Mapa de Madrid con `geojson`, filtros y métricas de cabecera |
| 2 | Influencias sobre el precio | Correlación de variables con precio · precio por tipo · precio por distancia · correlación calidad-precio |
| 3 | Demanda | Histórico de reseñas por año · meses de más y menos demanda · demanda en un año |
| 4 | Ofertadores de piso | Nº de anuncios · disponibilidad · media de rating · Superhost frente al resto · declaración por zona |
| 5 | Host profesionales | Calidad del piso frente a nº de anuncios · influencia del Superhost en el precio |

### Del boceto a la implementación

La **arquitectura se mantuvo intacta**: las cinco secciones del boceto son las cinco pestañas
finales, en el mismo orden. También sobrevivió sin cambios la fila de tres gráficos de
"Ofertadores de piso" (nº de anuncios · disponibilidad · rating), que comparten eje para poder
compararse.

Lo que cambió, y por qué:

| Del boceto | En la implementación | Motivo |
|---|---|---|
| "Ventanas con progreso que muestren un **flujo** de los hallazgos" | Cinco pestañas en orden narrativo, cada una abierta por un titular afirmativo | La idea de flujo se conservó; las "ventanas con progreso" habrían añadido navegación sin aportar información |
| Anotación: *"las métricas de arriba son MUY importantes, deberían ser globales"* | Línea de sumario en la cabecera y **cuatro filtros que afectan a las cinco pestañas** | La anotación se cumplió literalmente: es el origen de los filtros globales |
| Anotación: *"falta añadir algo aparte del mapa"* | Tablas con los cinco barrios extremos bajo el mapa | El mapa responde "dónde", pero no da los valores concretos |
| "Histograma vertical" + *"¿puedo meter algo más bonito que un histograma?"* | Barras **horizontales** ordenadas, con etiquetas directas | Los nombres de las variables son largos: en horizontal se leen sin girar la cabeza |
| "Correlación entre calidad y precio", anotada como *"esperable"* | Bloque **"La intuición, a prueba"** + ranking de factores por varianza explicada | Al medir el tamaño del efecto, la correlación *esperable* resultó explicar **menos del 1 %**. El bloque pasó de mostrar una relación a **contrastar una hipótesis** |
| "Usar gráficas de puntos" en demanda | Serie con área y barras des-tendenciadas | Los puntos no transmiten continuidad temporal; el área sí, y el desplome de 2020 se lee mejor |
| "Histograma de declaración de piso por zona" + *"usar algo que no sea un histograma"* | Barras horizontales por distrito, con línea de media | Permite ordenar los distritos y situarlos respecto al promedio |
| "Influencia del Superhost en el precio", en la última sección | Trasladado a **"Quién manda"** | Agrupar todo lo relativo al distintivo Superhost en una sola sección |
| "Comparativa de calidad del piso y nº de anuncios" | ***Slope chart*** de las subnotas por tamaño de anfitrión | El boceto pedía el *efecto*; el gráfico final muestra además el **mecanismo**: qué aspectos concretos se degradan y cuál no |

La anotación más certera es la de la página 5: *"¿esto contradice lo de antes?"*. Sí lo hacía.
La contradicción entre la correlación "esperable" de la página 2 y los hallazgos sobre
anfitriones profesionales de la página 5 resultó ser **el hallazgo principal del trabajo**, y
obligó a rehacer el bloque de precio.

---

## 6. Contenido del dashboard

| Sección | Responde a | Visualización principal |
|---|---|---|
| **El mapa** | ¿Dónde se concentra la oferta? | Coroplético por barrio con selector de métrica |
| **Qué fija el precio** | ¿Qué determina el precio? | Barras de correlación + ranking de tamaños de efecto |
| **La demanda** | ¿Cómo evoluciona? | Serie histórica + estacionalidad des-tendenciada + calendario futuro |
| **Quién manda** | ¿Quién opera la oferta? | Composición por tamaño de anfitrión, Superhosts y licencias |
| **Hosts profesionales** | ¿Qué consecuencias tiene profesionalizarse? | *Slope chart* de subnotas + precio por persona |

---

## 7. Documentación complementaria

| Documento | Contenido |
|---|---|
| `bitacora.md` | Fases del trabajo, iteraciones y decisiones, incluida la corrección de un hallazgo erróneo |
| `notebooks/01_exploracion_limpieza.ipynb` | Limpieza y validación |
| `notebooks/02_analisis_exploratorio.ipynb` | Análisis exploratorio (10 hallazgos) |
| `notebooks/03_hosts_profesionales.ipynb` | Desarrollo del hallazgo principal |
| `README.md` | Instalación y ejecución |
