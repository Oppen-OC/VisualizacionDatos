# Airbnb Madrid — Dashboard

Análisis del mercado de Airbnb en Madrid y cuadro de mando interactivo, a partir
de los datos públicos de [Inside Airbnb](http://insideairbnb.com/) (scrape de
junio de 2026). Trabajo universitario.

El dashboard, hecho con **Streamlit**, muestra qué fija el precio, la evolución de
la demanda, quién opera la oferta y el peaje de calidad de los hosts profesionales.

## Requisitos

- Python **3.11** o superior
- ~500 MB libres para el entorno virtual (pandas, plotly, streamlit)

## Instalación

Desde la raíz del proyecto, crear un entorno virtual e instalar las dependencias.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Si PowerShell bloquea la activación, ejecutar una vez:
> `Set-ExecutionPolicy -Scope Process RemoteSigned`

## Ejecutar el dashboard

```bash
streamlit run app.py
```

Abrir el navegador en **http://localhost:8501**. Usar los filtros de la barra
lateral (barrio, tipo de alojamiento, tipo de anfitrión) para explorar los datos.

## Estructura

```
app.py                           Dashboard de Streamlit
requirements.txt                 Dependencias
guion.md                         Guion de la presentación (~3 min)
bitacora.md                      Bitácora: fases, decisiones e iteraciones
data/
  dashboard/                     Datos pre-agregados que carga la app (~2 MB)
  processed/                     Parquet intermedios (limpios)
  *.csv                          Datos crudos de Inside Airbnb
notebooks/
  01_exploracion_limpieza.ipynb  Limpieza de datos
  02_analisis_exploratorio.ipynb Análisis exploratorio y hallazgos
  03_hosts_profesionales.ipynb   El hallazgo final: qué explica la nota
scripts/
  prepare_dashboard_data.py      Pre-agrega processed/ -> dashboard/
```

## Datos

La app solo lee `data/dashboard/` (ya generado), así que **no necesita** los CSV
crudos ni recalcular nada para funcionar.

Para regenerar los datos del dashboard desde los Parquet procesados (opcional):

```bash
python scripts/prepare_dashboard_data.py
```

**Notas:** el 15,5 % de anuncios no publica precio y se excluye de los análisis de
precio (no se imputa); las reseñas se usan como aproximación de las estancias;
"declara licencia" significa que el anuncio publica un número de registro, no que
se haya verificado.
