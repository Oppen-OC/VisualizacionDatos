# El mercado de Airbnb en Madrid

### Documento de diseño del dashboard

Visualización de Datos · Trabajo de evaluación
Datos: [Inside Airbnb](http://insideairbnb.com/) — Madrid, extracción de junio de 2026
Implementación: Streamlit (Python)

---

## 1. El problema abordado

El alquiler turístico de corta duración ha pasado, en poco más de una década, de ser un
intercambio entre particulares a convertirse en un **sector con operadores profesionales**. En
ciudades tensionadas como Madrid, esa transformación afecta al precio de la vivienda, a la
convivencia vecinal y al cumplimiento de la normativa turística.

El debate público suele apoyarse en **intuiciones**: que el centro es carísimo, que los pisos
caros son mejores, que los profesionales dan un servicio más cuidado. Hay datos públicos para
contrastarlas, pero están repartidos en tres ficheros que suman cerca de **diez millones de
filas**, un volumen que no se explora con una hoja de cálculo.

**El problema concreto:** no existe una vista única que responda, sobre datos reales y de forma
interactiva, a las cuatro preguntas que estructuran ese debate:

1. **¿Dónde** se concentra la oferta y cómo varía el precio geográficamente?
2. **¿Qué determina** realmente el precio de un anuncio?
3. **¿Cómo evoluciona** la demanda y qué estacionalidad tiene?
4. **¿Quién opera** la oferta, y qué consecuencias tiene su profesionalización?

El dashboard convierte esas filas en respuestas comprobables y permite **desmentir con datos**
dos creencias extendidas: que pagar más compra una experiencia mejor valorada, y que un operador
profesional ofrece un servicio superior. Ninguna se sostiene.

---

## 2. Usuarios del dashboard

Perfil **analítico**, no viajero: no es una herramienta de reserva ni de búsqueda de alojamiento.

| Perfil | Qué necesita | Dónde lo resuelve |
|---|---|---|
| **Técnico de administración pública** *(principal)* — urbanismo o turismo municipal, encargado de fundamentar o evaluar la regulación | Dónde se concentra la presión turística · qué proporción de la oferta declara licencia y dónde · grado de profesionalización · si la demanda crece o satura | Mapa coroplético · métrica de licencias y desglose por distrito · pestañas "Quién manda" y "Hosts profesionales" · serie histórica y calendario futuro |
| **Periodista de datos o investigador** | Hallazgos no evidentes, y poder **verificarlos** | Ranking de tamaños de efecto · cada afirmación fuerte acompañada de su magnitud y de los factores de confusión descartados |
| **Anfitrión particular** | Situar su alojamiento: si su precio encaja en su barrio y tipo, y cómo compite con los grandes gestores | Filtros laterales para acotar a su caso · hallazgo sobre anfitriones profesionales |

El **usuario principal** motiva las decisiones de diseño más restrictivas: necesita cifras
*defendibles*, no impactantes, porque puede tener que justificarlas públicamente.

**Fuera del alcance:** el viajero. Sus preguntas ("¿dónde me alojo el próximo puente?") exigen
búsqueda por fechas, fotos y contacto — funciones de la plataforma comercial, no de un cuadro de
mando analítico.

---

## 3. Objetivos de diseño

**O1 · Responder de un vistazo, ampliar bajo demanda.** Cada pestaña abre con la respuesta —un
titular afirmativo, no una etiqueta neutra— y desarrolla el detalle debajo. Quien solo lee los
titulares se lleva las conclusiones correctas; quien quiere comprobarlas encuentra las cifras.
De ahí *"El precio lo marca el tamaño, no la calidad"* en lugar de *"Correlaciones con el precio"*.

**O2 · Separar lo que explica de lo que solo acompaña.** El objetivo que más condicionó el
resultado. Mostrar correlaciones sin su magnitud **induce a error**: con 16.000 anuncios casi
cualquier relación es significativa aunque sea irrelevante. De aquí salen tres decisiones:
mostrar **tamaño de efecto** y no solo la existencia de correlación; contrastar los factores
entre sí en un mismo gráfico; y comparar siempre **dentro del mismo barrio y tipo** antes de dar
por bueno un patrón.

**O3 · No exagerar visualmente.** Un eje truncado convierte una diferencia de 0,1 puntos sobre 5
en un titular; durante el desarrollo esto produjo un error real que obligó a rehacer un bloque
entero de la pestaña de precio. Regla adoptada: **si el dato crudo induce a error, no se
grafica**. Se aplicó al descartar un gráfico de ocupación por tamaño de anfitrión cuya mediana
no es monótona y solo se ordena tras el control estadístico.

**O4 · Permitir que cada usuario acote su ámbito.** Cuatro filtros globales —distrito, tipo de
alojamiento, tamaño del anfitrión y solo Superhosts— que afectan a todas las vistas a la vez,
de modo que la comparación sigue siendo coherente al cambiar de pestaña.

**O5 · Un sistema visual único, legible y accesible.** Paleta **validada para daltonismo**: un
azul como color de magnitud, una rampa secuencial de un solo tono para el mapa y el par
azul/rojo reservado **en exclusiva** para polaridad. El color nunca es decorativo. Retícula
editorial de columna única con anchura máxima de lectura, jerarquía tipográfica serif/grotesca y
gráficos sin marco que se funden con el fondo. Etiquetas directas sobre las barras en lugar de
ejes de valores, y un solo eje Y por gráfico —nunca ejes duales, que permiten sugerir
correlaciones inexistentes—.

**O6 · Declarar las limitaciones en el propio dashboard.** Las advertencias viven en la interfaz,
no en un anexo: el 15,5 % de anuncios sin precio, las reseñas como *aproximación* de estancias y
que "declara licencia" no significa licencia verificada. Quien va a fundamentar una decisión debe
conocer los límites del dato mientras lo mira.

---

## 4. Datos que utiliza

**Origen.** [Inside Airbnb](http://insideairbnb.com/), proyecto independiente y sin ánimo de
lucro que extrae y publica información pública de los anuncios reales de la plataforma, ciudad
por ciudad, para permitir el estudio del impacto del alquiler turístico. Datos publicados con
licencia CC BY 4.0. Extracción utilizada: **Madrid, junio de 2026**.

| Fichero | Volumen | Contenido |
|---|---|---|
| `listings` | 22.708 anuncios × 90 columnas | Precio, capacidad, tipo, ubicación, valoraciones, anfitrión, licencia |
| `reviews` | 1.419.360 reseñas (2010 – 2026) | Anuncio, fecha, autor y texto |
| `calendar` | 8.334.782 filas (jun 2026 – jul 2027) | Disponibilidad diaria y noches mínimas |
| `neighbourhoods.geojson` | 128 barrios | Geometrías para el mapa |

**Preparación.** Detalle completo en `notebooks/01_exploracion_limpieza.ipynb` y en la bitácora.
Las decisiones que afectan a lo que se visualiza:

| Situación | Decisión | Motivo |
|---|---|---|
| 15,5 % de anuncios sin precio | **No imputar**, excluir de los análisis de precio | La ausencia no es aleatoria: son anuncios inactivos (3,1 reseñas/año frente a 18,8). Imputar habría inventado oferta inexistente |
| 11.070 reseñas duplicadas por (anuncio, fecha) | **No deduplicar** | Son reseñas distintas de dos huéspedes el mismo día. Deduplicar habría infracontado la demanda |
| Precios atípicos hasta 36.883 €/noche | Recorte del 1 % superior en análisis de precio | Distorsionaban medias y escalas |
| `minimum_nights ≥ 365` | Marcados como calendario bloqueado | No son alquileres reales |

**Lo que consume la aplicación.** El dashboard **no lee los ficheros originales**: un script
(`scripts/prepare_dashboard_data.py`) los pre-agrega a cuatro ficheros de ~2 MB en
`data/dashboard/` — `anuncios.parquet` (una fila por anuncio), `resenas_mes.parquet`,
`ocupacion.parquet` y `barrios.geojson`. La razón es de diseño y no solo técnica: cargar 223 MB
de reseñas y 8,3 millones de filas de calendario hacía la aplicación **inutilizable de forma
interactiva**, y un dashboard que tarda en responder deja de ser una herramienta de exploración.

**Limitaciones conocidas.**

- Las **reseñas son una aproximación** de las estancias, no un registro de reservas: solo reseña
  una parte de los huéspedes, así que subestiman la ocupación real.
- En el calendario, "no disponible" **mezcla reservado y bloqueado** por el anfitrión: la
  ocupación es un techo, no una cifra exacta.
- "Declara licencia" significa que el anuncio publica un número de registro; **no se ha podido
  verificar su validez** contra el registro oficial.
- Los datos son una **fotografía de un momento** (junio de 2026). Las series históricas proceden
  de las reseñas acumuladas, no de extracciones sucesivas.

---

## 5. Mockup

Boceto a mano, una página por sección: **[`mockup.pdf`](mockup.pdf)**. No fija estilos ni
colores, solo qué mostrar y dónde, con anotaciones al pie.

Las cinco secciones del boceto son las cinco pestañas finales, en el mismo orden. El detalle
llegó después, con los datos delante. Dos anotaciones marcaron el rumbo: *"las métricas de
arriba deberían ser globales"* originó los cuatro filtros globales; y *"¿esto contradice lo de
antes?"* (página 5) anticipó el hallazgo principal — la correlación precio-calidad, anotada como
*"esperable"* en la página 2, resultó explicar menos del 1 % y se rehízo como ranking de
factores.

---

## 6. El dashboard

| Sección | Responde a | Visualización principal |
|---|---|---|
| **El mapa** | ¿Dónde se concentra la oferta? | Coroplético por barrio con selector de métrica |
| **Qué fija el precio** | ¿Qué determina el precio? | Barras de correlación + ranking de tamaños de efecto |
| **La demanda** | ¿Cómo evoluciona? | Serie histórica + estacionalidad des-tendenciada + calendario futuro |
| **Quién manda** | ¿Quién opera la oferta? | Composición por tamaño de anfitrión, Superhosts y licencias |
| **Hosts profesionales** | ¿Qué consecuencias tiene profesionalizarse? | *Slope chart* de subnotas + precio por persona |

**Documentación complementaria:** `bitacora.md` (fases, iteraciones y decisiones, incluida la
corrección de un hallazgo erróneo), los tres notebooks de `notebooks/` y `README.md` con las
instrucciones de instalación.

Los notebooks son **material exploratorio**: contienen el código, sus salidas y las notas de
método, pero no la interpretación. Las conclusiones viven en el dashboard, que es el entregable
pensado para comunicarlas.
