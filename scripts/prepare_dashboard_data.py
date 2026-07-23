# -*- coding: utf-8 -*-
"""Pre-agrega los parquet de data/processed/ a ficheros pequeños para el dashboard.

El dashboard NO debe cargar reviews_full.parquet (223 MB) ni el calendario crudo
(8,3M filas). Este script genera en data/dashboard/:

  - anuncios.parquet       una fila por anuncio, sólo las columnas que usa la app (~1 MB)
  - resenas_mes.parquet    reseñas por mes x distrito x tipo de alojamiento
  - ocupacion.parquet      % no disponible por fecha x distrito x tipo (con nº de anuncios)
  - barrios.geojson        copia del geojson de barrios para el mapa

Uso:  python scripts/prepare_dashboard_data.py   (desde la raíz del repo)
"""
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / 'data' / 'processed'
OUT = RAIZ / 'data' / 'dashboard'
OUT.mkdir(parents=True, exist_ok=True)

SOL_LAT, SOL_LON = 40.41678, -3.70379

# ---------------------------------------------------------------- anuncios
full = pd.read_parquet(PROC / 'listings_full.parquet')

anuncios = pd.DataFrame({
    'id': full['id'],
    'nombre': full['name'],
    'barrio': full['neighbourhood_cleansed'].astype(str),
    'distrito': full['neighbourhood_group_cleansed'].astype(str),
    'lat': full['latitude'],
    'lon': full['longitude'],
    'tipo': full['room_type'].astype(str),
    'precio': full['price'],
    'capacidad': full['accommodates'],
    'dormitorios': full['bedrooms'],
    'noches_min': full['minimum_nights'],
    'disponibilidad_365': full['availability_365'],
    'n_resenas': full['number_of_reviews'],
    'resenas_mes': full['reviews_per_month'],
    'rating': full['review_scores_rating'],
    'rating_valor': full['review_scores_value'],
    'rating_ubicacion': full['review_scores_location'],
    'rating_limpieza': full['review_scores_cleanliness'],
    'rating_checkin': full['review_scores_checkin'],
    'rating_comunicacion': full['review_scores_communication'],
    'rating_precision': full['review_scores_accuracy'],
    'ocupacion_est': full['estimated_occupancy_l365d'],
    'anuncios_del_host': full['calculated_host_listings_count'],
    'superhost': full['host_is_superhost'] == 't',
    'con_licencia': full['license'].notna(),
    'bloqueado': full['is_blocked_placeholder'],
})
anuncios['tipo_host'] = pd.cut(
    anuncios['anuncios_del_host'], [0, 1, 5, 20, 10_000],
    labels=['1 anuncio', '2-5', '6-20', '21+'],
).astype(str).replace('nan', 'desconocido')
anuncios['dist_km'] = np.sqrt(
    ((anuncios['lat'] - SOL_LAT) * 111.32) ** 2
    + ((anuncios['lon'] - SOL_LON) * 111.32 * np.cos(np.radians(SOL_LAT))) ** 2
)
anuncios.to_parquet(OUT / 'anuncios.parquet', index=False)
print(f'anuncios.parquet:    {len(anuncios):,} filas')

clave = anuncios.set_index('id')[['distrito', 'tipo']]

# ---------------------------------------------------------------- reseñas por mes
reviews = pd.read_parquet(PROC / 'reviews.parquet')
rm = reviews.join(clave, on='listing_id')
rm = rm.dropna(subset=['distrito'])
rm['mes'] = rm['date'].dt.to_period('M').dt.to_timestamp()
resenas_mes = (rm.groupby(['mes', 'distrito', 'tipo'], observed=True)
               .size().rename('n').reset_index())
resenas_mes.to_parquet(OUT / 'resenas_mes.parquet', index=False)
print(f'resenas_mes.parquet: {len(resenas_mes):,} filas '
      f'({resenas_mes.n.sum():,} reseñas agregadas)')

# ---------------------------------------------------------------- ocupación futura
cal = pd.read_parquet(PROC / 'calendar.parquet',
                      columns=['listing_id', 'date', 'available'])
cal = cal.join(clave, on='listing_id').dropna(subset=['distrito'])
ocupacion = (cal.groupby(['date', 'distrito', 'tipo'], observed=True)['available']
             .agg(n='size', disponibles='sum').reset_index())
ocupacion['no_disponibles'] = ocupacion['n'] - ocupacion['disponibles']
ocupacion = ocupacion.drop(columns='disponibles')
# recortamos el borde final del scrape, donde quedan pocos anuncios y el dato es ruido
ocupacion = ocupacion[ocupacion['date'] <= '2027-05-31']
ocupacion.to_parquet(OUT / 'ocupacion.parquet', index=False)
print(f'ocupacion.parquet:   {len(ocupacion):,} filas')

# ---------------------------------------------------------------- geojson
shutil.copy(RAIZ / 'data' / 'neighbourhoods.geojson', OUT / 'barrios.geojson')
print('barrios.geojson:     copiado')

for f in sorted(OUT.iterdir()):
    print(f'  {f.name}: {f.stat().st_size / 1e6:.2f} MB')
