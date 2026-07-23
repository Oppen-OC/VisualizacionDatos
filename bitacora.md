# Bitácora — Airbnb Madrid

Registro de fases, decisiones e iteraciones del trabajo. Documento complementario: el de la
entrega es [`documento.md`](documento.md).

**Datos:** [Inside Airbnb](http://insideairbnb.com/), Madrid, junio de 2026 — 22.708 anuncios,
1,4 M de reseñas, 8,3 M de filas de calendario, 128 barrios.
**Herramientas:** Python 3.11 · pandas · SciPy · Matplotlib · Plotly · Streamlit · Jupyter.
**Fechas:** 10 – 23 de julio de 2026.

---

## 1. Datos y limpieza · 10 jul
`notebooks/01_exploracion_limpieza.ipynb`

Primera decisión, de arquitectura: convertir los CSV a **Parquet**, para no releer 750 MB de
texto en cada iteración. Los tiempos de carga bajan de minutos a segundos.

| Problema | Decisión | Motivo |
|---|---|---|
| `price` venía como texto (`"$1,234.00"`) | Convertir a numérico | Imposible operar de otro modo |
| 15,5 % de anuncios sin precio | **No imputar**, excluir de los análisis de precio | La ausencia no es aleatoria: son anuncios inactivos (3,1 reseñas/año frente a 18,8). Imputar habría inventado mercado |
| 11.070 filas repetidas en `reviews` por (anuncio, fecha) | **No deduplicar** | Verificado contra `reviews_full`: 0 ids repetidos. Son reseñas distintas del mismo día |
| Precios de hasta 36.883 €/noche | Recortar el 1 % superior, sólo en análisis de precio | Distorsionaban medias y escalas |
| 12 columnas de metadatos de host vacías | Eliminar | Sin información |
| `minimum_nights >= 365` | Marcar `is_blocked_placeholder` | Son calendarios bloqueados, no alquileres |

> **Aprendizaje:** tratar los faltantes según *su causa*, no con una regla automática. El 15,5 %
> de precios ausentes resultó ser una señal —anuncios dormidos—, no ruido.

---

## 2. Análisis exploratorio · 12 – 17 jul
`notebooks/02_analisis_exploratorio.ipynb`

Diez hallazgos planteados como pregunta → evidencia. Los principales: el precio lo determina la
**capacidad** (r ≈ 0,60) y no la calidad (r ≈ 0,09); el sobreprecio del centro se agota a ~3 km;
la demanda de 2025 cuadruplica la de 2019 tras caer un 69 % en 2020; octubre es el pico y agosto
el valle; un tercio de la oferta es de anfitriones con más de 20 anuncios; los Superhosts cobran
casi lo mismo pero reciben ~2,6× reseñas al mes.

> **Iteración:** los primeros perfiles estacionales usaban medias mensuales crudas, dominadas por
> el crecimiento de 4× del periodo. Se rehízo **des-tendenciando** —% del año que cae en cada mes,
> promediado entre años— y el mes pico cambió.

---

## 3. Cuadro de mando · 12 jul
`app.py`, `scripts/prepare_dashboard_data.py`

Se elige **Streamlit** por su integración directa con pandas. Estructura inicial: 4 pestañas
(mapa, precio, demanda, anfitriones) y filtros laterales.

**Problema de rendimiento:** cargar `reviews_full.parquet` (223 MB) y el calendario (8,3 M filas)
hacía la app inusable. **Solución:** un script de pre-agregación reduce todo a 4 ficheros de ~2 MB
en `data/dashboard/`; la app nunca toca los datos crudos.

**Dos iteraciones de rediseño.** La primera, porque el resultado "parecía una plantilla": se
rehace la capa visual con enfoque de *data journalism* —serif de titular, grotesca de interfaz,
fondo de papel, cabecera tipo periódico, línea de sumario en lugar de `st.metric`, sin emojis—.
La segunda, porque los gráficos seguían pareciendo ajenos a la página: se unifican con helpers
(`base_layout`, `barras_v`, `barras_h`, `lineas`) sobre fondo transparente, sin rejillas y con
etiquetas directas en vez de ejes de valores.

> **Incidencias técnicas:** (1) Streamlit envuelve los encabezados en un `<span>` hijo y la regla
> `span { font-family: sans }` los dejaba en sans; hubo que forzar `h1 span … h5 span`.
> (2) Fijar el título de Plotly a `None` renderizaba la cadena literal `undefined`: se usa
> `title=dict(text='')`. (3) Los títulos serif se recortaban dentro del lienzo de Plotly, así que
> se sacaron a HTML sobre el gráfico.

---

## 4. Segunda vuelta analítica · 19 – 23 jul
`notebooks/03_hosts_profesionales.ipynb`

**Motivación:** casi todos los hallazgos de la fase 2 eran esperables. Se replantea con más
exigencia: **correlaciones parciales** en vez de simples, y **tamaño de efecto** (r²) en vez de
sólo significancia.

### El error detectado

Al reexaminar la relación precio-rating con r² se vio que el notebook 02 **se contradecía a sí
mismo**: en su sección 1 concluía que el rating apenas correlaciona con el precio, pero en la 4
presentaba el mismo dato como *"hallazgo contraintuitivo"* y lo proponía como tarjeta de dato
sorpresa. El dashboard heredó esa propuesta, con un gráfico de eje truncado (4,35–4,85) que
agrandaba una diferencia de ~0,1 puntos sobre 5.

El fallo de origen: **leer un gradiente sin medir su magnitud**. El precio explica el **0,83 %**
de la varianza del rating. El efecto es real —sobrevive al control por barrio y tipo— pero
irrelevante. Se sustituyó el recuadro por un **ranking de tamaños de efecto**.

> **Aprendizaje:** con n = 16.000 casi todo es significativo. Y un eje truncado convierte una
> diferencia trivial en un titular.

### El hallazgo principal

El ranking reveló que lo que predice la nota no es el alojamiento sino el **anfitrión**, con un
signo inesperado:

| Factor | r | Varianza explicada |
|---|---|---|
| Es Superhost | +0,280 | 7,8 % |
| **Anuncios del host (log)** | **−0,191** | **3,7 %** |
| Nº de reseñas | +0,132 | 1,8 % |
| Precio (log) | +0,091 | 0,8 % |

Cuantos más anuncios gestiona un anfitrión, **peor** lo valoran. El efecto resiste los controles
—−0,191 sin control, −0,189 dentro de barrio × tipo, −0,173 añadiendo antigüedad—, así que no es
composición ni anuncios más nuevos.

El desglose por subnota muestra **dónde** se rompe: comunicación −0,25, calidad-precio −0,25,
check-in −0,19, precisión −0,18, limpieza −0,15 y **ubicación −0,07**. La caída se concentra en
lo que depende de una persona; la ubicación —lo único que el anfitrión no puede cambiar— apenas
se mueve y funciona como control interno. Además no cobran prima por escala: el precio por plaza
baja de 45 € a 40 €, también dentro del mismo barrio y tipo.

**Límite explícito:** es correlación, no causalidad. Es igual de compatible con que perfiles
distintos de anfitrión acaben en escalas distintas.

### Incorporación al dashboard

Se amplía `prepare_dashboard_data.py` con las subnotas y la ocupación estimada, y se añade la
pestaña **"Hosts profesionales"**: *slope chart* de subnotas —el gráfico que muestra el
mecanismo, no sólo el efecto—, precio por persona y un recuadro con los límites.

> **Decisión de honestidad visual:** se descartó un gráfico de ocupación por tamaño de anfitrión.
> Su mediana cruda no es monótona (los particulares incluyen muchos anuncios inactivos) y sólo se
> ordena tras el control estadístico; en bruto habría inducido a error. El dato se menciona en
> texto, no en gráfico.

---

## 5. Separar exploración de conclusión · 23 jul

El error de la fase 4 dejó a la vista un problema de fondo: las conclusiones estaban
**duplicadas** en los notebooks y en el dashboard, así que cuando una cambió las dos se
contradijeron y sólo se corrigió una. Se separaron los papeles:

| Pieza | Papel |
|---|---|
| Notebooks | **Exploración**: código, salidas y notas de método |
| Dashboard | **Conclusiones**: qué significan los datos |
| `documento.md` · bitácora | Diseño y proceso |

Se retiró de los tres notebooks el texto interpretativo —bloques "Hallazgo", apartados "Para el
dashboard", resúmenes finales— y se neutralizaron los titulares que afirmaban un resultado
(*"La demanda se ha cuadruplicado"* → *"Demanda anual"*). El texto bajó un 57 %, 81 % y 85 %.
**El código, las salidas y los 17 gráficos quedaron intactos:** desaparece la interpretación, no
el análisis.

---

## Cronología

| Fecha | Hito |
|---|---|
| 10 jul | Limpieza y conversión a Parquet |
| 12 jul | Análisis exploratorio, dashboard v1 y los dos rediseños |
| 17 jul | Revisión del notebook 02 |
| 19 jul | Segunda vuelta analítica, corrección del hallazgo precio-rating, nueva pestaña |
| 23 jul | Notebook 03, documento de diseño y reorganización de los notebooks |

## Decisiones metodológicas clave

1. **No imputar los precios ausentes:** la ausencia era informativa.
2. **No deduplicar las reseñas repetidas:** se verificó que eran distintas.
3. **Des-tendenciar la estacionalidad:** las medias crudas seguían al crecimiento.
4. **Usar r², no sólo r:** cambió la interpretación del hallazgo del precio.
5. **Correlación parcial** antes de dar por bueno cualquier patrón.
6. **Precio por persona** además del absoluto, para comparar alojamientos de distinto tamaño.
7. **Pre-agregar los datos** del dashboard en vez de cargar los ficheros completos.
8. **No graficar métricas cuyo dato crudo induce a error**, aunque apoyen la narrativa.
