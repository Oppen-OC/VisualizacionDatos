# Bitácora del trabajo — Airbnb Madrid

Registro de fases, decisiones e iteraciones del proyecto de análisis de datos y
cuadro de mando sobre el mercado de Airbnb en Madrid.

**Fuente de datos:** [Inside Airbnb](http://insideairbnb.com/) — Madrid, scrape de junio de 2026.
**Herramientas:** Python 3.11 · pandas 3.0 · NumPy · SciPy · Matplotlib · Plotly · Streamlit · Jupyter.
**Cronología:** 10 – 23 de julio de 2026 (fechas verificables en los timestamps de los artefactos).

---

## Ficha técnica del dataset

| Fichero | Volumen | Uso |
|---|---|---|
| `listings.csv` / `listings_1.csv` | 22.708 anuncios, 90 columnas | Análisis principal |
| `calendar.csv` | 8.334.782 filas (jun 2026 → jul 2027) | Ocupación futura |
| `reviews.csv` / `reviews_1.csv` | 1.419.360 reseñas (desde 2010) | Proxy de demanda |
| `neighbourhoods.geojson` | 128 barrios | Mapa coroplético |

---

## Fase 1 — Adquisición y comprensión de los datos
**10 de julio**

- Descarga del volcado de Madrid de Inside Airbnb y revisión del diccionario de campos.
- Inspección inicial de tipos, cardinalidades y valores faltantes.
- Decisión de arquitectura: convertir los CSV a **Parquet** (`data/processed/`) para que el
  análisis no relea 750 MB de texto en cada iteración. Reduce los tiempos de carga de minutos
  a segundos.

## Fase 2 — Limpieza y validación
**10 de julio** · `notebooks/01_exploracion_limpieza.ipynb`

Decisiones de limpieza, cada una con su justificación:

| Problema detectado | Decisión | Razón |
|---|---|---|
| `price` venía como texto (`"$1,234.00"`) | Conversión a numérico | Imposible operar de otro modo |
| **15,5%** de anuncios sin precio (3.538 de 22.835 en el fichero resumen; 3.536 de 22.708 en el de detalle, que es el que usa el análisis) | **No imputar**; excluir de los análisis de precio | La ausencia **no es aleatoria**: son anuncios inactivos (3,1 reseñas/año de media frente a 18,8; 26 días disponibles frente a 222). Imputar habría inventado un mercado que no existe |
| **11.070** filas duplicadas en `reviews` por (anuncio, fecha) | **No deduplicar** | Verificado contra `reviews_full`: mismo nº de filas y **0 ids de reseña repetidos**. Son reseñas distintas de dos huéspedes el mismo día. Deduplicar habría infracontado la demanda |
| Outliers de precio hasta 36.883 €/noche | Recorte del 1% superior sólo en análisis de precio | Distorsionaban medias y escalas de los gráficos |
| 12 columnas de metadatos de host completamente vacías | Eliminadas | Sin información |
| `minimum_nights >= 365` | Marcados con `is_blocked_placeholder` | No son alquileres reales, son calendarios bloqueados |

> **Aprendizaje de la fase:** tratar los faltantes según *su causa* y no con una regla
> automática. El 15,5% de precios ausentes resultó ser una señal (anuncios dormidos), no ruido.

## Fase 3 — Análisis exploratorio
**12 – 17 de julio** · `notebooks/02_analisis_exploratorio.ipynb`

Diez hallazgos, cada uno planteado como pregunta → evidencia → implicación para el dashboard.
Los principales:

1. El precio lo determina la **capacidad** (r ≈ 0,60), no la calidad (rating r ≈ 0,09).
2. El sobreprecio del centro se agota a ~3 km de la Puerta del Sol.
3. La demanda de 2025 cuadruplica la de 2019; caída del 69% en 2020.
4. Estacionalidad **des-tendenciada**: octubre es el pico, agosto el valle.
5. Un tercio de la oferta pertenece a anfitriones con más de 20 anuncios.
6. Los Superhosts cobran casi lo mismo pero reciben ~2,6× reseñas al mes.

> **Iteración metodológica:** los primeros perfiles estacionales usaban medias mensuales
> crudas, que estaban dominadas por el crecimiento del 4× del periodo (los meses de años
> recientes pesaban más). Se rehízo el cálculo **des-tendenciando**: porcentaje del año que
> cae en cada mes, promediado entre años. El pico cambió de resultado.

## Fase 4 — Cuadro de mando v1
**12 de julio** · `app.py`, `scripts/prepare_dashboard_data.py`

- Elección de **Streamlit** por integración directa con pandas y despliegue trivial.
- **Problema de rendimiento:** cargar `reviews_full.parquet` (223 MB) y el calendario
  (8,3M filas) en la app la hacía inusable.
- **Solución:** script de pre-agregación (`prepare_dashboard_data.py`) que reduce todo a
  4 ficheros de ~2 MB en `data/dashboard/`. La app nunca toca los datos crudos.
- Estructura inicial: 4 pestañas (mapa, precio, demanda, hosts) + filtros laterales.

### Iteración 4.1 — Rediseño editorial
**12 de julio**

El resultado inicial "parecía una plantilla". Se rehízo la capa visual con un enfoque de
*data journalism*: tipografía serif de titular (Newsreader) + grotesca de interfaz (Libre
Franklin), fondo de papel cálido, cabecera tipo periódico, línea de sumario en HTML
sustituyendo a `st.metric`, notas de análisis en cursiva y eliminación de todos los emojis.

> **Incidencia técnica:** Streamlit envuelve el texto de los encabezados en un `<span>` hijo,
> y la regla base `span { font-family: sans }` lo sobrescribía, dejando los titulares en
> sans. Hubo que añadir explícitamente `h1 span … h5 span` con `!important`.

### Iteración 4.2 — Rediseño de los gráficos
**12 de julio**

Los gráficos seguían pareciendo ajenos a la página. Se unificaron con helpers
(`base_layout`, `barras_v`, `barras_h`, `lineas`): fondo transparente, sin rejillas por
defecto, etiquetas directas en las barras en lugar de ejes de valores.

> **Dos incidencias técnicas:** (1) fijar el título de Plotly a `None` hacía que Streamlit
> renderizara la cadena literal `undefined`; hubo que usar `title=dict(text='')`. (2) Los
> títulos serif se recortaban por arriba dentro del lienzo de Plotly, así que se sacaron a
> HTML sobre el gráfico (`titulo_grafico`).

## Fase 5 — Segunda vuelta analítica: buscar lo no obvio
**19 – 23 de julio** · `notebooks/03_hosts_profesionales.ipynb`

**Motivación:** revisando los hallazgos de la fase 3, casi todos eran **esperables** (a más
capacidad, más precio; el centro es más caro). Faltaba un hallazgo que contradijera la
intuición. Se planteó una segunda vuelta con exigencia metodológica mayor: **correlaciones
parciales** en lugar de correlaciones simples, y **tamaño de efecto** (r²) en lugar de sólo
significancia.

Líneas exploradas: confusores del par precio-rating, comportamiento de anfitriones,
disponibilidad y bloqueo estratégico, geografía, texto de reseñas, precio por persona y
patrones de esquiva regulatoria.

### Iteración 5.1 — Corrección de un error del dashboard

Al reexaminar la relación precio-rating con r² se detectó que el propio notebook 02 se
**contradecía a sí mismo**, y que el error se había propagado al dashboard:

- En su sección 1, el notebook 02 concluía correctamente: *"los ratings apenas correlacionan
  (r ≈ 0,09): pagar más no compra una experiencia mejor valorada"*.
- Pero en su sección 4, al mirar el detalle por cuartiles, lo presentaba como *"hallazgo
  contraintuitivo"*: *"no existe el efecto caro = clavada"*, y lo proponía como **tarjeta de
  dato sorpresa** para el dashboard.
- El dashboard heredó esa propuesta en un recuadro destacado, apoyado en un gráfico de
  cuartiles con el eje Y recortado (4,35–4,85) que agrandaba visualmente una diferencia de
  ~0,1 puntos sobre 5.

El fallo de origen fue **leer un gradiente sin medir su magnitud**: las medias por cuartil
subían, pero nunca se comprobó cuánta varianza explicaban.

**Verificación:** el precio explica el **0,83%** de la varianza del rating. El efecto es
real —sobrevive al control por barrio y tipo (r pasa de +0,091 a +0,096)— pero
**prácticamente irrelevante**.

**Corrección aplicada**, en las tres piezas afectadas:

1. **Dashboard:** se sustituyó el recuadro y el gráfico de cuartiles por un **ranking de
   tamaños de efecto** que muestra qué explica realmente la nota.
2. **Notebook 02:** se añadió una **errata** en la sección 4 y se marcó la fila
   correspondiente de la tabla de conclusiones. El análisis original se conserva sin
   modificar, para que la revisión quede trazable.
3. **Guion de la presentación:** se reescribió el pasaje que repetía la afirmación errónea.

> **Aprendizaje:** un resultado estadísticamente significativo con n = 16.000 puede ser
> irrelevante en magnitud. Y un eje truncado convierte una diferencia trivial en un titular.

### Iteración 5.2 — El hallazgo principal

El ranking de tamaños de efecto reveló que los factores que sí predicen la nota no son del
alojamiento sino del **anfitrión**, y uno con signo inesperado:

| Factor | r | Varianza explicada |
|---|---|---|
| Es Superhost | +0,280 | 7,8% |
| **Anuncios del host (log)** | **−0,191** | **3,7%** |
| Nº de reseñas | +0,132 | 1,8% |
| Precio (log) | +0,091 | 0,8% |

**Hallazgo:** cuantos más anuncios gestiona un anfitrión, **peor** lo valoran — lo contrario
de lo que sugiere la intuición sobre operadores profesionales.

Controles aplicados para descartar explicaciones alternativas:

| Control | r resultante |
|---|---|
| Sin control | −0,191 |
| Dentro de barrio × tipo de alojamiento | −0,189 |
| Añadiendo antigüedad del anuncio | −0,173 |

El efecto **resiste**: no es composición (no es que los profesionales estén en peores zonas)
ni antigüedad.

**Descomposición por aspecto** — dónde se rompe exactamente la experiencia:

| Aspecto | Caída (1 anuncio → 21+) |
|---|---|
| Comunicación | −0,25 |
| Calidad-precio | −0,25 |
| Check-in | −0,19 |
| Precisión del anuncio | −0,18 |
| Limpieza | −0,15 |
| **Ubicación** | **−0,07** |

La caída se concentra en lo que depende de una **persona**. La ubicación —lo único que el
anfitrión no puede modificar— apenas se mueve, y funciona como control interno: si se tratara
de un sesgo general contra los profesionales, caería igual que el resto.

Además, **no cobran prima por escala**: el precio por plaza baja de forma monótona
(45 € → 40 €), también dentro del mismo barrio y tipo (r = −0,11).

**Límite explícito:** es correlación, no causalidad. No se demuestra que profesionalizarse
degrade un alojamiento; es igual de compatible con que perfiles distintos de anfitrión acaben
en escalas distintas.

### Iteración 5.3 — Incorporación al dashboard

- Ampliación de `prepare_dashboard_data.py` para incluir las subnotas
  (`rating_limpieza`, `rating_checkin`, `rating_comunicacion`, `rating_precision`) y la
  ocupación estimada; regeneración de `anuncios.parquet`.
- Nueva pestaña **"Hosts profesionales"** con línea de sumario, *slope chart* de subnotas
  (el gráfico que muestra el mecanismo, no sólo el efecto), precio por persona y un recuadro
  con los límites metodológicos.
- **Decisión de honestidad visual:** se descartó incluir un gráfico de ocupación por tamaño
  de anfitrión. La mediana cruda no es monótona (los particulares incluyen muchos anuncios
  inactivos) y sólo se ordena tras el control estadístico; representarla en bruto habría
  inducido a error. El dato se menciona en texto, no en gráfico.
- Verificación de la app con `streamlit.testing.v1.AppTest`: 0 excepciones, 15 gráficos.

## Fase 6 — Documentación y entregables
**19 – 23 de julio**

- `guion.md` — guion de la presentación (~3 min), ajustado a 532 palabras tras cronometrar.
  Incluye la corrección del hallazgo erróneo y la nueva sección.
- `README.md` — instrucciones de instalación y ejecución.
- `notebooks/03_hosts_profesionales.ipynb` — documentación reproducible del hallazgo final.
- `bitacora.md` — este documento.

---

## Resumen cronológico

| Fecha | Hito |
|---|---|
| 10 jul | Limpieza y conversión a Parquet (notebook 01) |
| 12 jul | Análisis exploratorio, dashboard v1, rediseño editorial y de gráficos |
| 17 jul | Revisión y reejecución del notebook 02 |
| 19 jul | Segunda vuelta analítica; corrección del hallazgo precio-rating; nueva pestaña; guion; README |
| 23 jul | Notebook 03 (hallazgo de hosts profesionales) y bitácora |

## Decisiones metodológicas clave

1. **No imputar los precios ausentes.** La ausencia era informativa (anuncios inactivos).
2. **No deduplicar las reseñas repetidas.** Verificado que eran distintas.
3. **Des-tendenciar la estacionalidad.** Las medias crudas estaban dominadas por el crecimiento.
4. **Usar r², no sólo r.** Cambió la interpretación del hallazgo del precio.
5. **Correlación parcial** (control por barrio × tipo) antes de dar por bueno cualquier patrón.
6. **Precio por persona** además del precio absoluto, para comparar alojamientos de distinto tamaño.
7. **Pre-agregar los datos del dashboard** en lugar de cargar los ficheros completos.
8. **No graficar métricas cuyo dato crudo induce a error** aunque apoyen la narrativa.

## Estructura final de entregables

```
app.py                              Dashboard (5 pestañas)
guion.md                            Guion de presentación (~3 min)
bitacora.md                         Este documento
README.md                           Instalación y ejecución
requirements.txt                    Dependencias
notebooks/01_exploracion_limpieza.ipynb
notebooks/02_analisis_exploratorio.ipynb
notebooks/03_hosts_profesionales.ipynb
scripts/prepare_dashboard_data.py
data/                               Crudos, procesados y pre-agregados
```
