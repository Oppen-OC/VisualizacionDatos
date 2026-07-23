# -*- coding: utf-8 -*-
"""Dashboard Airbnb Madrid — hallazgos del análisis exploratorio.

Datos: Inside Airbnb (scrape jun 2026), pre-agregados por scripts/prepare_dashboard_data.py.
Ejecutar:  streamlit run app.py

Estética: editorial / data-journalism. Tipografía serif de titular (Newsreader) +
grotesca de interfaz (Libre Franklin), papel cálido, cifras en línea de sumario,
notas de análisis en cursiva. La lógica de datos y la paleta de gráficos (validada
para daltonismo) no cambian respecto a la versión anterior.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------- paleta
# Tinta y papel cálidos (editorial); el azul de datos es el de la paleta validada.
INK, INK2, MUTED = '#1d1b16', '#57534a', '#8a857a'
GRID, BASE = '#e4dfd3', '#cec8ba'
PAPER, SURFACE = '#f4f1ea', '#fbfaf6'      # fondo de página / superficie de gráfico
BLUE, BLUE_L, BLUE_D = '#2a78d6', '#9ec5f4', '#104281'
RED, AQUA = '#e34948', '#1baf7a'
SEQ = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b']

SERIF = '"Newsreader", Georgia, "Times New Roman", serif'
SANS = '"Libre Franklin", system-ui, -apple-system, "Segoe UI", sans-serif'

DATOS = Path(__file__).parent / 'data' / 'dashboard'
MESES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
         'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

st.set_page_config(page_title='Airbnb Madrid — el reportaje', layout='wide')


# ----------------------------------------------------------------- estilo (CSS)
def inyectar_estilo():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=Libre+Franklin:wght@400;500;600;700&display=swap');

    /* ---- base ---- */
    .stApp {{ background: {PAPER}; }}
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
    input, textarea, select, button, .stMarkdown, p, span, div, label, li, td, th {{
        font-family: {SANS};
        color: {INK};
    }}
    [data-testid="stHeader"] {{ background: transparent; }}
    .block-container {{ padding-top: 2.2rem; padding-bottom: 4rem; max-width: 1180px; }}

    /* ---- titulares serif ---- */
    /* el texto del titular vive en un <span> hijo, que la regla base pondría en
       sans; por eso hay que forzar serif también en h*+span. */
    h1, h2, h3, h4, h5,
    h1 span, h2 span, h3 span, h4 span, h5 span {{
        font-family: {SERIF} !important; color: {INK}; letter-spacing: -0.01em; font-weight: 600;
    }}
    /* subtítulos de sección: un punto más contenidos */
    [data-testid="stHeadingWithActionElements"] h3 {{ font-size: 1.55rem; margin-top: 0.2rem; }}

    /* ---- cabecera / masthead ---- */
    .kicker {{
        font-family: {SANS}; font-weight: 600; font-size: 0.72rem;
        letter-spacing: 0.18em; text-transform: uppercase; color: {BLUE_D};
        margin-bottom: 0.55rem;
    }}
    .masthead-title {{
        font-family: {SERIF}; font-weight: 600; font-size: 3.05rem; line-height: 1.03;
        color: {INK}; margin: 0 0 0.5rem 0; letter-spacing: -0.02em;
    }}
    .dek {{
        font-family: {SERIF}; font-style: italic; font-size: 1.24rem; line-height: 1.45;
        color: {INK2}; max-width: 40rem; margin: 0 0 0.2rem 0; font-weight: 400;
    }}
    .rule {{ border: none; border-top: 1px solid {BASE}; margin: 1.5rem 0 1.2rem 0; }}
    .rule-thin {{ border: none; border-top: 1px solid {GRID}; margin: 1.4rem 0; }}

    /* ---- línea de sumario (stats) ---- */
    .statstrip {{ display: flex; flex-wrap: wrap; gap: 0; margin: 0.2rem 0 0.4rem 0; }}
    .stat {{ padding: 0.1rem 1.9rem; }}
    .stat + .stat {{ border-left: 1px solid {BASE}; }}
    .stat:first-child {{ padding-left: 0; }}
    .stat-label {{
        font-family: {SANS}; font-weight: 600; font-size: 0.68rem; letter-spacing: 0.12em;
        text-transform: uppercase; color: {MUTED}; margin-bottom: 0.28rem;
    }}
    .stat-num {{
        font-family: {SERIF}; font-weight: 500; font-size: 2.15rem; line-height: 1;
        color: {INK}; font-variant-numeric: lining-nums;
    }}
    .stat-num small {{ font-size: 1.05rem; color: {INK2}; font-weight: 400; }}
    .stat-note {{
        font-family: {SANS}; font-size: 0.74rem; color: {BLUE_D}; margin-top: 0.35rem;
        font-weight: 500;
    }}

    /* ---- nota de análisis (aside editorial) ---- */
    .nota {{
        font-family: {SERIF}; font-style: italic; font-size: 1.0rem; line-height: 1.5;
        color: {INK2}; border-left: 2px solid {BLUE}; padding: 0.05rem 0 0.05rem 0.9rem;
        margin: 0.1rem 0 0.6rem 0; max-width: 34rem;
    }}
    .nota b {{ font-style: normal; font-weight: 600; color: {INK}; }}

    /* ---- títulos de gráfico (HTML sobre el gráfico, no dentro de plotly) ---- */
    .chart-title {{
        font-family: {SERIF}; font-weight: 600; font-size: 1.16rem; line-height: 1.22;
        color: {INK}; letter-spacing: -0.01em; margin: 0.2rem 0 0.05rem 0;
    }}
    .chart-sub {{
        font-family: {SANS}; font-size: 0.78rem; color: {MUTED}; margin: 0 0 0.25rem 0;
    }}

    /* ---- callout destacado (premisa → evidencia → conclusión) ---- */
    .callout {{
        background: {SURFACE}; border: 1px solid {BASE}; border-top: 3px solid {BLUE};
        padding: 1.2rem 1.4rem; border-radius: 2px;
    }}
    .callout .k {{
        font-family: {SANS}; font-weight: 600; font-size: 0.7rem; letter-spacing: 0.14em;
        text-transform: uppercase; color: {BLUE_D}; margin-bottom: 0.6rem;
    }}
    .callout p {{
        font-family: {SERIF}; font-size: 1.12rem; line-height: 1.5; color: {INK};
        margin: 0;
    }}
    /* callouts que encadenan varios párrafos (premisa → evidencia → conclusión) */
    .callout p + p {{ margin-top: 0.72rem; }}
    .callout p b:first-child {{ color: {BLUE_D}; }}

    /* ---- pestañas como navegación de secciones ---- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem; border-bottom: 1px solid {BASE}; margin-bottom: 1.4rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: {SANS}; font-weight: 600; font-size: 0.78rem; letter-spacing: 0.1em;
        text-transform: uppercase; color: {MUTED}; padding: 0.2rem 0 0.7rem 0;
        background: transparent;
    }}
    .stTabs [aria-selected="true"] {{ color: {INK} !important; }}
    .stTabs [data-baseweb="tab-highlight"] {{ background: {INK}; height: 2px; }}
    .stTabs [data-baseweb="tab-border"] {{ background: transparent; }}

    /* ---- sidebar ---- */
    [data-testid="stSidebar"] {{ background: {PAPER}; border-right: 1px solid {BASE}; }}
    [data-testid="stSidebar"] .block-container {{ padding-top: 1.5rem; }}

    /* ---- pie ---- */
    .pie {{
        font-family: {SANS}; font-size: 0.76rem; color: {MUTED}; line-height: 1.6;
        border-top: 1px solid {BASE}; padding-top: 1rem; margin-top: 1.5rem;
    }}
    .pie a {{ color: {INK2}; }}
    </style>
    """, unsafe_allow_html=True)


def fmt(n, dec=0):
    """1234567 -> '1.234.567' (formato es-ES)."""
    return f'{n:,.{dec}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def nota(texto, col=st):
    """Aside editorial en cursiva serif (sustituye a los antiguos st.caption)."""
    col.markdown(f'<p class="nota">{texto}</p>', unsafe_allow_html=True)


def titulo_grafico(col, titulo, subtitulo=None):
    """Título (serif) + subtítulo (sans) sobre el gráfico, con la tipografía de la
    página. Se renderiza como HTML en la columna, justo antes del st.plotly_chart,
    para que use el mismo sistema tipográfico que los titulares y no lo recorte plotly."""
    html = f'<div class="chart-title">{titulo}</div>'
    if subtitulo:
        html += f'<div class="chart-sub">{subtitulo}</div>'
    col.markdown(html, unsafe_allow_html=True)


def base_layout(fig, altura=380):
    """Lienzo editorial: fondo transparente (se funde con el papel), sin rejilla ni
    ejes por defecto, sin título (lo pone titulo_grafico en HTML). Cada gráfico vuelve
    a activar sólo lo que necesita con los helpers barras_v / barras_h / lineas."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family=SANS, color=INK2, size=12.5),
        title=dict(text=''),
        margin=dict(l=6, r=16, t=18, b=6),
        height=altura, showlegend=fig.layout.showlegend,
        hoverlabel=dict(bgcolor='#ffffff', bordercolor=BASE,
                        font_family=SANS, font_color=INK, font_size=12.5),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False, ticks='',
                     tickfont=dict(color=MUTED, size=12),
                     title_font=dict(color=MUTED, size=12))
    fig.update_yaxes(showgrid=False, zeroline=False, showline=False, ticks='',
                     tickfont=dict(color=MUTED, size=12),
                     title_font=dict(color=MUTED, size=12))
    return fig


def barras_v(fig, ymax):
    """Barras verticales con etiqueta directa: se elimina el eje de valores (Y) y se
    deja sólo una línea de base bajo las categorías."""
    fig.update_yaxes(visible=False, range=[0, ymax * 1.20])
    fig.update_xaxes(showline=True, linecolor=BASE, linewidth=1.2,
                     tickfont=dict(color=INK2, size=12.5))
    return fig


def barras_h(fig, cero=False):
    """Barras horizontales con etiqueta directa: se elimina el eje X."""
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(tickfont=dict(color=INK2, size=12.5))
    if cero:
        fig.add_vline(x=0, line_color=BASE, line_width=1)
    return fig


def lineas(fig):
    """Series temporales / de tendencia: sólo rejilla horizontal muy tenue."""
    fig.update_yaxes(showgrid=True, gridcolor=GRID, tickfont=dict(color=MUTED, size=12))
    fig.update_xaxes(showline=True, linecolor=BASE, linewidth=1,
                     tickfont=dict(color=INK2, size=12))
    return fig


@st.cache_data
def cargar():
    anuncios = pd.read_parquet(DATOS / 'anuncios.parquet')
    resenas = pd.read_parquet(DATOS / 'resenas_mes.parquet')
    ocupacion = pd.read_parquet(DATOS / 'ocupacion.parquet')
    with open(DATOS / 'barrios.geojson', encoding='utf-8') as f:
        geo = json.load(f)
    return anuncios, resenas, ocupacion, geo


inyectar_estilo()
anuncios, resenas, ocupacion, geo = cargar()

# ----------------------------------------------------------------- sidebar
st.sidebar.markdown('<div class="kicker">Filtros</div>', unsafe_allow_html=True)

distritos_sel = st.sidebar.multiselect(
    'Distrito', sorted(anuncios.distrito.unique()),
    placeholder='Todos los distritos')
tipos_sel = st.sidebar.multiselect(
    'Tipo de alojamiento', sorted(anuncios.tipo.unique()),
    placeholder='Todos los tipos')
host_sel = st.sidebar.selectbox(
    'Tamaño del host (nº de anuncios que gestiona)',
    ['Todos', '1 anuncio', '2-5', '6-20', '21+'])
solo_super = st.sidebar.toggle('Sólo Superhosts')

with st.sidebar.expander('Notas sobre los datos'):
    st.markdown(
        '- El **15,5% de los anuncios no publica precio** (hoteles y anuncios sin '
        'disponibilidad): se cuentan como oferta pero quedan fuera de los análisis de precio, '
        'donde además se recorta el 1% superior (outliers de hasta 36.883 €/noche).\n'
        '- Las **reseñas** se usan como *proxy* de estancias.\n'
        '- En el calendario, "no disponible" mezcla **reservado y bloqueado**: es un techo '
        'de ocupación.\n'
        '- "Con licencia" significa que el anuncio **declara** un nº de registro (o exención); '
        'no podemos verificar su validez.')

# filtros
f = anuncios
if distritos_sel:
    f = f[f.distrito.isin(distritos_sel)]
if tipos_sel:
    f = f[f.tipo.isin(tipos_sel)]
if host_sel != 'Todos':
    f = f[f.tipo_host == host_sel]
if solo_super:
    f = f[f.superhost]

rf = resenas
of = ocupacion
if distritos_sel:
    rf = rf[rf.distrito.isin(distritos_sel)]
    of = of[of.distrito.isin(distritos_sel)]
if tipos_sel:
    rf = rf[rf.tipo.isin(tipos_sel)]
    of = of[of.tipo.isin(tipos_sel)]

if f.empty:
    st.warning('Ningún anuncio cumple los filtros seleccionados.')
    st.stop()

# base de precios: con precio y sin el 1% superior global
CORTE_P99 = anuncios.precio.quantile(0.99)
fp = f[f.precio.notna() & (f.precio < CORTE_P99)]

# ----------------------------------------------------------------- masthead
st.markdown(
    '<div class="kicker">Inside Airbnb · Madrid · scrape de junio 2026</div>'
    '<div class="masthead-title">El mercado de Airbnb en Madrid</div>'
    '<p class="dek">Qué determina el precio de un anuncio, cómo se ha disparado la '
    'demanda tras la pandemia y quién opera realmente la oferta de la ciudad.</p>'
    '<hr class="rule">',
    unsafe_allow_html=True)

# ----------------------------------------------------------------- línea de sumario
r2019 = rf[rf.mes.dt.year == 2019].n.sum()
r2025 = rf[rf.mes.dt.year == 2025].n.sum()
precio_med = f'{fmt(fp.precio.median())}<small> €/noche</small>' if len(fp) else '—'
nota_resenas = (f'<div class="stat-note">↑ {r2025 / r2019:.1f}× vs 2019 (pre-COVID)</div>'
                if r2019 else '')

st.markdown(
    '<div class="statstrip">'
    f'<div class="stat"><div class="stat-label">Anuncios</div>'
    f'<div class="stat-num">{fmt(len(f))}</div></div>'
    f'<div class="stat"><div class="stat-label">Precio mediano</div>'
    f'<div class="stat-num">{precio_med}</div></div>'
    f'<div class="stat"><div class="stat-label">Declaran licencia</div>'
    f'<div class="stat-num">{f.con_licencia.mean() * 100:.0f}<small> %</small></div></div>'
    f'<div class="stat"><div class="stat-label">Reseñas en 2025</div>'
    f'<div class="stat-num">{fmt(r2025)}</div>{nota_resenas}</div>'
    '</div><hr class="rule">',
    unsafe_allow_html=True)

tab_mapa, tab_precio, tab_demanda, tab_hosts, tab_pro = st.tabs(
    ['El mapa', 'Qué fija el precio', 'La demanda', 'Quién manda', 'Hosts profesionales'])

# ================================================================= MAPA
with tab_mapa:
    st.markdown('### Dónde se concentra —y se encarece— la oferta')
    METRICAS = {
        'Precio mediano (€/noche)': ('precio_mediano', SEQ),
        'Nº de anuncios': ('n_anuncios', SEQ),
        '% que declara licencia': ('pct_licencia', SEQ),
        'Rating medio': ('rating_medio', SEQ),
    }
    c_sel, c_nota = st.columns([1, 2], vertical_alignment='center')
    metrica = c_sel.selectbox('Métrica', list(METRICAS), label_visibility='collapsed')
    with c_nota:
        nota('El premium del centro se agota a ~3&nbsp;km de la Puerta del Sol; '
             'sólo se pintan barrios con 10 o más anuncios tras los filtros.')

    por_barrio = f.groupby('barrio').agg(
        n_anuncios=('id', 'size'),
        precio_mediano=('precio', 'median'),
        pct_licencia=('con_licencia', 'mean'),
        rating_medio=('rating', 'mean'),
        distrito=('distrito', 'first'),
    ).reset_index()
    por_barrio['pct_licencia'] *= 100
    por_barrio = por_barrio[por_barrio.n_anuncios >= 10]

    col, _ = METRICAS[metrica]
    fig = px.choropleth_map(
        por_barrio, geojson=geo, locations='barrio',
        featureidkey='properties.neighbourhood', color=col,
        color_continuous_scale=SEQ, opacity=0.78,
        center={'lat': 40.425, 'lon': -3.69}, zoom=10.4,
        map_style='carto-positron',
        hover_name='barrio',
        hover_data={'barrio': False, 'distrito': True, 'n_anuncios': ':,',
                    'precio_mediano': ':.0f', 'pct_licencia': ':.0f',
                    'rating_medio': ':.2f'},
        labels={'precio_mediano': '€ mediana', 'n_anuncios': 'anuncios',
                'pct_licencia': '% licencia', 'rating_medio': 'rating',
                'distrito': 'distrito'},
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=560, title=dict(text=''),
                      paper_bgcolor='rgba(0,0,0,0)', font=dict(family=SANS, color=INK2),
                      coloraxis_colorbar=dict(
                          title='', thickness=12, outlinewidth=0,
                          tickfont=dict(color=MUTED, size=11), len=0.85))
    st.plotly_chart(fig, width='stretch')

    tabla = por_barrio[['barrio', col]].assign(**{col: por_barrio[col].round(1)})
    c1, c2 = st.columns(2)
    c1.markdown(f'**Los 5 barrios más altos** · {metrica.lower()}')
    c1.dataframe(tabla.nlargest(5, col).rename(columns={col: metrica}),
                 hide_index=True, width='stretch')
    c2.markdown(f'**Los 5 más bajos** · {metrica.lower()}')
    c2.dataframe(tabla.nsmallest(5, col).rename(columns={col: metrica}),
                 hide_index=True, width='stretch')

# ================================================================= PRECIO
with tab_precio:
    c1, c2 = st.columns([1.15, 1])

    # --- correlaciones con log-precio (barras de polaridad) ---
    VARS = {'capacidad': 'Capacidad (huéspedes)', 'dormitorios': 'Dormitorios',
            'rating_ubicacion': 'Rating: ubicación', 'rating': 'Rating global',
            'n_resenas': 'Nº de reseñas', 'disponibilidad_365': 'Disponibilidad anual',
            'anuncios_del_host': 'Anuncios del host',
            'dist_km': 'Distancia al centro (km)', 'noches_min': 'Noches mínimas'}
    if len(fp) >= 100:
        aux = fp.assign(log_precio=np.log10(fp.precio))
        corr = (aux[list(VARS) + ['log_precio']].corr(numeric_only=True)['log_precio']
                .drop('log_precio').rename(VARS).sort_values())
        fig = go.Figure(go.Bar(
            x=corr.values, y=corr.index, orientation='h',
            marker_color=[BLUE if v > 0 else RED for v in corr.values],
            text=[f'{v:+.2f}' for v in corr.values], textposition='outside',
            textfont=dict(color=INK2, size=12.5),
            hovertemplate='%{y}: %{x:+.2f}<extra></extra>'))
        base_layout(fig, 430)
        barras_h(fig, cero=True)
        fig.update_xaxes(range=[-0.5, 0.82])
        titulo_grafico(c1, 'El precio lo marca el tamaño, no la calidad',
                       'correlación de cada variable con log₁₀(precio)')
        c1.plotly_chart(fig, width='stretch')
        nota('La capacidad pesa <b>seis veces más</b> que el rating. Las barras rojas '
             'tienen lógica propia: más noches mínimas es alquiler de temporada '
             '(más barato por noche), y más distancia al centro, menos premium.', c1)
    else:
        c1.info('Muy pocos anuncios con precio para calcular correlaciones con estos filtros.')

    # --- precio por tipo ---
    por_tipo = (fp.groupby('tipo', observed=True).precio.median()
                .sort_values(ascending=False).dropna())
    fig = go.Figure(go.Bar(
        x=por_tipo.index, y=por_tipo.values, marker_color=BLUE, width=0.62,
        text=[f'{v:.0f} €' for v in por_tipo.values], textposition='outside',
        textfont=dict(color=INK2, size=12.5),
        hovertemplate='%{x}: %{y:.0f} €<extra></extra>'))
    base_layout(fig, 300)
    barras_v(fig, por_tipo.values.max())
    titulo_grafico(c2, 'Precio mediano por tipo de alojamiento', '€/noche')
    c2.plotly_chart(fig, width='stretch')

    # --- premium por distancia ---
    anillos = pd.cut(fp.dist_km, [0, 1, 2, 3, 5, 8, 15],
                     labels=['0–1', '1–2', '2–3', '3–5', '5–8', '8+'])
    por_anillo = fp.groupby(anillos, observed=True).precio.median().dropna()
    fig = go.Figure(go.Bar(
        x=por_anillo.index.astype(str), y=por_anillo.values, marker_color=BLUE, width=0.62,
        text=[f'{v:.0f} €' for v in por_anillo.values], textposition='outside',
        textfont=dict(color=INK2, size=12.5),
        hovertemplate='%{x} km: %{y:.0f} €<extra></extra>'))
    base_layout(fig, 300)
    barras_v(fig, por_anillo.values.max())
    titulo_grafico(c2, 'El premium del centro se agota a ~3 km',
                   '€/noche mediana · km hasta la Puerta del Sol')
    c2.plotly_chart(fig, width='stretch')

    st.markdown('<hr class="rule-thin">', unsafe_allow_html=True)

    # --- precio↔rating: la intuición puesta a prueba ---
    c3, c4 = st.columns([1, 1.15])
    c3.markdown(
        '<div class="callout"><div class="k">La intuición, a prueba</div>'
        '<p><b>Lo que se presume:</b> que pagar más compra una estancia mejor. Si fuera '
        'cierto, el precio debería predecir la valoración de los huéspedes.</p>'
        '<p><b>Lo que dicen los datos:</b> casi nada. El precio explica <b>menos del 1%</b> '
        'de la variación en las notas. El efecto existe —y se mantiene al comparar pisos '
        'del mismo barrio y tipo— pero es <b>diminuto</b>.</p>'
        '<p><b>Lo que sí la predice:</b> no cuánto cuesta el alojamiento, sino <b>quién lo '
        'gestiona</b>. En el gráfico contiguo, los dos factores que más pesan son del '
        'anfitrión. La sección <i>Hosts profesionales</i> desarrolla por qué.</p></div>',
        unsafe_allow_html=True)
    if len(fp) >= 200:
        aux = fp.assign(
            log_precio=np.log(fp.precio),
            log_host=np.log(fp.anuncios_del_host.clip(lower=1)),
            es_super=fp.superhost.astype(float),
        ).dropna(subset=['rating'])
        FACTORES = [('Ser Superhost', 'es_super'), ('Anuncios del host', 'log_host'),
                    ('Nº de reseñas', 'n_resenas'), ('Precio', 'log_precio'),
                    ('Distancia al centro', 'dist_km'), ('Capacidad', 'capacidad')]
        filas = []
        for etiqueta, col in FACTORES:
            m = aux[col].notna()
            if m.sum() < 50:
                continue
            r = np.corrcoef(aux[col][m], aux.rating[m])[0, 1]
            filas.append((etiqueta, r, r ** 2 * 100))
        filas.sort(key=lambda t: t[2])
        etiquetas = [t[0] for t in filas]
        r2 = [t[2] for t in filas]
        colores = [RED if e == 'Precio' else BLUE for e in etiquetas]
        direccion = ['sube la nota' if r > 0 else 'baja la nota' for _, r, _ in filas]
        fig = go.Figure(go.Bar(
            x=r2, y=etiquetas, orientation='h', marker_color=colores,
            text=[f'{v:.1f}%' for v in r2], textposition='outside',
            textfont=dict(color=INK2, size=12.5), customdata=direccion,
            hovertemplate='%{y}: explica %{x:.1f}% de la nota · %{customdata}<extra></extra>'))
        base_layout(fig, 340)
        barras_h(fig)
        fig.update_xaxes(range=[0, max(r2) * 1.28])
        titulo_grafico(c4, 'Qué explica la nota —y qué no',
                       '% de la varianza del rating que explica cada factor (R²)')
        c4.plotly_chart(fig, width='stretch')
        nota('El precio apenas mueve la aguja (~1%). Ser <b>Superhost</b> pesa varias veces '
             'más y —contra la intuición— gestionar muchos anuncios <b>baja</b> la nota. '
             'La calidad la marca el host, no la tarifa.', c4)
    else:
        c4.info('Muy pocos anuncios para el análisis con estos filtros.')

# ================================================================= DEMANDA
with tab_demanda:
    st.markdown('### El turismo urbano de Madrid no se recuperó: se disparó')
    # --- serie anual ---
    por_año = rf.groupby(rf.mes.dt.year).n.sum()
    por_año = por_año[(por_año.index >= 2011) & (por_año.index <= 2025)]
    fig = go.Figure(go.Scatter(
        x=por_año.index, y=por_año.values, mode='lines+markers',
        line=dict(color=BLUE, width=2.5), marker=dict(size=6),
        fill='tozeroy', fillcolor='rgba(42,120,214,0.06)',
        hovertemplate='%{x}: %{y:,} reseñas<extra></extra>'))
    if 2020 in por_año.index and 2019 in por_año.index and por_año[2019]:
        caida = por_año[2020] / por_año[2019] - 1
        fig.add_annotation(x=2020, y=por_año[2020], text=f'COVID {caida * 100:+.0f}%',
                           showarrow=True, arrowcolor=MUTED, arrowwidth=1, ax=0, ay=-40,
                           font=dict(family=SANS, color=INK, size=12.5))
    fig.update_yaxes(title='reseñas/año (proxy de estancias)', rangemode='tozero')
    base_layout(fig, 380)
    lineas(fig)
    titulo_grafico(st, 'La demanda se ha cuadruplicado desde la pandemia',
                   'reseñas al año como proxy de estancias · 2011–2025')
    st.plotly_chart(fig, width='stretch')

    c1, c2 = st.columns(2)

    # --- perfil estacional (des-tendenciado) ---
    rm = rf[(rf.mes >= '2015-01-01') & (rf.mes < '2026-01-01')].copy()
    rm['año'] = rm.mes.dt.year
    rm['num_mes'] = rm.mes.dt.month
    por_am = rm.groupby(['año', 'num_mes']).n.sum().reset_index()
    por_am['pct'] = por_am.n / por_am.groupby('año').n.transform('sum') * 100
    perfil = por_am.groupby('num_mes').pct.mean()
    if len(perfil) == 12:
        colores = [BLUE if m == perfil.idxmax() else BLUE_L for m in perfil.index]
        fig = go.Figure(go.Bar(
            x=MESES, y=perfil.values, marker_color=colores, width=0.62,
            hovertemplate='%{x}: %{y:.1f}% del año<extra></extra>'))
        fig.add_hline(y=100 / 12, line_dash='dot', line_color=MUTED, line_width=1,
                      annotation_text='reparto uniforme (8,3%)',
                      annotation_font=dict(family=SANS, color=MUTED, size=11))
        fig.update_yaxes(title='% de las reseñas del año', ticksuffix='%')
        base_layout(fig, 360)
        lineas(fig)
        fig.update_xaxes(tickfont=dict(color=INK2, size=11.5))
        titulo_grafico(c1, 'Octubre manda; agosto se hunde',
                       'media 2015–2025, corregida de la tendencia de crecimiento')
        c1.plotly_chart(fig, width='stretch')
        nota('Perfil <b>des-tendenciado</b> (el % del año que cae en cada mes, promediado '
             'entre años): Madrid es destino urbano —pico en otoño, valle en pleno verano—, '
             'no de playa.', c1)

    # --- ocupación futura ---
    oc = of.groupby('date')[['no_disponibles', 'n']].sum()
    oc = oc[oc.n >= 50]
    curva = (oc.no_disponibles / oc.n * 100).rolling(7, center=True).mean().dropna()
    if len(curva):
        fig = go.Figure(go.Scatter(
            x=curva.index, y=curva.values, mode='lines',
            line=dict(color=BLUE, width=2.5), fill='tozeroy',
            fillcolor='rgba(42,120,214,0.08)',
            hovertemplate='%{x|%d %b %Y}: %{y:.0f}%<extra></extra>'))
        fig.update_yaxes(title='% no disponible', range=[0, 85], ticksuffix='%')
        base_layout(fig, 360)
        lineas(fig)
        titulo_grafico(c2, 'El calendario futuro confirma el patrón',
                       'media móvil 7 días · jun 2026 → may 2027')
        c2.plotly_chart(fig, width='stretch')
        nota('Las fechas cercanas siempre parecen más llenas (efecto <i>lead time</i>). '
             'Lo revelador va <b>contra</b> esa pendiente: agosto cae bajo septiembre y la '
             'primavera de 2027 supera al invierno previo —la misma estación que la histórica.',
             c2)

# ================================================================= HOSTS
with tab_hosts:
    st.markdown('### Un tercio de la oferta ya no es de particulares')
    nota('Cuanto más profesional es el host, más disponibilidad (negocio a tiempo '
         'completo) y <b>peor</b> valoración: el trato personal se nota en las reseñas.')
    orden_hosts = ['1 anuncio', '2-5', '6-20', '21+']
    ph = (f[f.tipo_host.isin(orden_hosts)]
          .groupby('tipo_host').agg(n=('id', 'size'),
                                    disp=('disponibilidad_365', 'mean'),
                                    rating=('rating', 'mean'))
          .reindex(orden_hosts).dropna())
    c1, c2, c3 = st.columns(3)
    fig = go.Figure(go.Bar(x=ph.index, y=ph.n, marker_color=BLUE, width=0.62,
                           text=[fmt(v) for v in ph.n], textposition='outside',
                           textfont=dict(color=INK2, size=12.5), hoverinfo='skip'))
    base_layout(fig, 300)
    barras_v(fig, ph.n.max())
    titulo_grafico(c1, 'Nº de anuncios')
    c1.plotly_chart(fig, width='stretch')

    fig = go.Figure(go.Bar(x=ph.index, y=ph.disp, marker_color=BLUE, width=0.62,
                           text=[f'{v:.0f}' for v in ph.disp], textposition='outside',
                           textfont=dict(color=INK2, size=12.5), hoverinfo='skip'))
    base_layout(fig, 300)
    barras_v(fig, ph.disp.max())
    titulo_grafico(c2, 'Disponibilidad (días/año)')
    c2.plotly_chart(fig, width='stretch')

    fig = go.Figure(go.Scatter(x=ph.index, y=ph.rating, mode='lines+markers+text',
                               line=dict(color=BLUE, width=2.5), marker=dict(size=8),
                               text=[f'{v:.2f}' for v in ph.rating],
                               textposition='top center',
                               textfont=dict(color=INK2, size=12.5), hoverinfo='skip'))
    base_layout(fig, 300)
    fig.update_yaxes(visible=False, range=[4.35, 4.95])
    fig.update_xaxes(showline=True, linecolor=BASE, linewidth=1.2,
                     tickfont=dict(color=INK2, size=12.5))
    titulo_grafico(c3, 'Rating medio')
    c3.plotly_chart(fig, width='stretch')

    st.markdown('<hr class="rule-thin">', unsafe_allow_html=True)
    c4, c5 = st.columns(2)

    # --- superhost ---
    if not solo_super and f.superhost.nunique() == 2:
        ps = f.groupby(f.superhost.map({False: 'Resto', True: 'Superhost'})).agg(
            rpm=('resenas_mes', 'median'), precio=('precio', 'median'))
        fig = go.Figure()
        fig.add_bar(x=ps.index, y=ps.rpm, marker_color=[BLUE_L, BLUE], width=0.5,
                    text=[f'{v:.2f}' for v in ps.rpm], textposition='outside',
                    textfont=dict(color=INK2, size=12.5), hoverinfo='skip')
        base_layout(fig, 320)
        barras_v(fig, ps.rpm.max())
        titulo_grafico(c4, 'El efecto Superhost', 'reseñas/mes (mediana)')
        c4.plotly_chart(fig, width='stretch')
        mult = ps.rpm.get('Superhost', 0) / ps.rpm.get('Resto', 1)
        nota(f'Apenas cobran más ({fmt(ps.precio.get("Superhost", 0))} € vs '
             f'{fmt(ps.precio.get("Resto", 0))} €) pero reciben <b>{mult:.1f}× más reseñas '
             'al mes</b>: el distintivo se monetiza vía ocupación, no vía precio.', c4)
    else:
        c4.info('Desactiva el filtro "Sólo Superhosts" para ver la comparativa.')

    # --- licencias por distrito ---
    pl = (f.groupby('distrito').con_licencia.agg(['mean', 'size'])
          .query('size >= 20').sort_values('mean'))
    media = f.con_licencia.mean() * 100
    fig = go.Figure(go.Bar(
        x=pl['mean'] * 100, y=pl.index, orientation='h', marker_color=BLUE,
        text=[f'{v * 100:.0f}%' for v in pl['mean']], textposition='outside',
        textfont=dict(color=INK2, size=12),
        hovertemplate='%{y}: %{x:.0f}%<extra></extra>'))
    fig.add_vline(x=media, line_dash='dot', line_color=MUTED, line_width=1,
                  annotation_text=f'media {media:.0f}%',
                  annotation_font=dict(family=SANS, color=MUTED, size=11),
                  annotation_position='top')
    base_layout(fig, max(340, 27 * len(pl)))
    barras_h(fig)
    fig.update_xaxes(range=[0, 108])
    titulo_grafico(c5, 'El centro declara más que la periferia',
                   '% de anuncios que declara nº de registro')
    c5.plotly_chart(fig, width='stretch')
    nota('Gradiente inverso al esperado: donde más presión turística hay (Salamanca, '
         'Centro) más se declara —probablemente porque ahí operan los hosts profesionales, '
         'que sí tramitan el registro.', c5)

# ================================================================= HOSTS PROFESIONALES
with tab_pro:
    st.markdown('### Escalar cuesta calidad: el peaje del host profesional')
    nota('El hallazgo central del análisis. Cuantos más anuncios gestiona un host, '
         '<b>peor</b> es su nota —y el desplome no es casual: se concentra en el trato '
         'humano (comunicación, check-in), no en lo estructural. Sobrevive al comparar '
         'pisos del <b>mismo barrio y tipo de alojamiento</b> (correlación parcial '
         'r&nbsp;=&nbsp;−0,19), así que no es un mero reflejo de que los profesionales '
         'operen en peores zonas.')

    orden = ['1 anuncio', '2-5', '6-20', '21+']
    fh = anuncios
    if distritos_sel:
        fh = fh[fh.distrito.isin(distritos_sel)]
    if tipos_sel:
        fh = fh[fh.tipo.isin(tipos_sel)]
    fh = fh[fh.tipo_host.isin(orden)].copy()
    fh['precio_pp'] = fh.precio / fh.capacidad.clip(lower=1)

    # subscore: clave -> (columna, etiqueta, color, ancho de línea)
    SUB = {'comunicacion': ('rating_comunicacion', 'Comunicación', BLUE_D, 3),
           'checkin': ('rating_checkin', 'Check-in', BLUE, 2),
           'limpieza': ('rating_limpieza', 'Limpieza', MUTED, 2),
           'ubicacion': ('rating_ubicacion', 'Ubicación', AQUA, 3)}
    agg = {k: (c, 'mean') for k, (c, _, _, _) in SUB.items()}
    agg.update(n=('id', 'size'), rating=('rating', 'mean'),
               valor=('rating_valor', 'mean'), precio_pp=('precio_pp', 'median'))
    g = fh.groupby('tipo_host').agg(**agg).reindex(orden)
    gg = g.dropna(subset=['rating'])
    cats = [c for c in orden if c in gg.index]

    def coma(v, dec=2):
        return f'{v:.{dec}f}'.replace('.', ',')

    if len(cats) >= 2:
        a0, a1 = cats[0], cats[-1]
        d_rating = gg.rating[a1] - gg.rating[a0]
        d_valor = gg.valor[a1] - gg.valor[a0]
        d_ppp = gg.precio_pp[a1] - gg.precio_pp[a0]
        share_pro = (fh.tipo_host == '21+').mean() * 100

        st.markdown(
            '<div class="statstrip">'
            f'<div class="stat"><div class="stat-label">Oferta de grandes gestores (21+)</div>'
            f'<div class="stat-num">{share_pro:.0f}<small> %</small></div></div>'
            f'<div class="stat"><div class="stat-label">Nota · particular → 21+</div>'
            f'<div class="stat-num">{coma(d_rating)}<small> pts</small></div></div>'
            f'<div class="stat"><div class="stat-label">Calidad-precio · mismo tramo</div>'
            f'<div class="stat-num">{coma(d_valor)}<small> pts</small></div></div>'
            f'<div class="stat"><div class="stat-label">Precio por persona</div>'
            f'<div class="stat-num">{d_ppp:+.0f}<small> €</small></div></div>'
            '</div><hr class="rule-thin">',
            unsafe_allow_html=True)

        c1, c2 = st.columns([1.35, 1])

        # --- slope chart: dónde se rompe la calidad al escalar ---
        fig = go.Figure()
        for k, (col, lab, color, ancho) in SUB.items():
            y = gg[k]
            fig.add_scatter(
                x=cats, y=y.values, mode='lines+markers',
                line=dict(color=color, width=ancho), marker=dict(size=7),
                hovertemplate=f'{lab} · %{{x}}: %{{y:.2f}}<extra></extra>')
            fig.add_annotation(x=cats[-1], y=y.iloc[-1], text=lab, xanchor='left',
                               xshift=12, showarrow=False,
                               font=dict(family=SANS, color=color, size=12))
        fig.update_yaxes(title='puntuación media (1–5)', range=[4.4, 4.95])
        base_layout(fig, 360)
        lineas(fig)
        fig.update_layout(showlegend=False, margin_r=118)
        fig.update_xaxes(tickfont=dict(color=INK2, size=12.5))
        titulo_grafico(c1, 'Al escalar se rompe lo humano, no la ubicación',
                       'puntuación media de cada aspecto · por tamaño del host')
        c1.plotly_chart(fig, width='stretch')
        d_com = gg['comunicacion'][a0] - gg['comunicacion'][a1]
        d_chk = gg['checkin'][a0] - gg['checkin'][a1]
        d_ubi = gg['ubicacion'][a0] - gg['ubicacion'][a1]
        nota(f'Del particular al gran gestor, la <b>comunicación</b> cae {coma(d_com)} '
             f'puntos y el <b>check-in</b> {coma(d_chk)}; la <b>ubicación</b> —que el host '
             f'no puede cambiar— apenas se mueve ({coma(d_ubi)}). El peaje se paga en el '
             'trato, no en los metros.', c1)

        # --- precio por persona: y encima, más barato ---
        ppp = gg.precio_pp.reindex(cats)
        fig = go.Figure(go.Bar(
            x=cats, y=ppp.values, marker_color=BLUE, width=0.62,
            text=[f'{v:.0f} €' for v in ppp.values], textposition='outside',
            textfont=dict(color=INK2, size=12.5),
            hovertemplate='%{x}: %{y:.0f} € por persona<extra></extra>'))
        base_layout(fig, 300)
        barras_v(fig, ppp.values.max())
        titulo_grafico(c2, 'Y encima, cobran menos por persona',
                       '€/noche por huésped (mediana)')
        c2.plotly_chart(fig, width='stretch')
        nota('No es un premio por escala: el profesional compite <b>bajando</b> el precio '
             'por plaza. Peor producto y más barato —el volumen, no la calidad, es su '
             'negocio.', c2)

        st.markdown('<hr class="rule-thin">', unsafe_allow_html=True)
        st.markdown(
            '<div class="callout"><div class="k">Cómo leerlo · rigor</div>'
            '<p>La caída de nota con el tamaño del host es de las señales más fuertes del '
            'dataset (r&nbsp;≈&nbsp;−0,19) y <b>aguanta al controlar barrio y tipo de '
            'alojamiento</b> por correlación parcial —no es un efecto de composición. Aun '
            'así es <b>correlación, no causa</b>: no probamos que profesionalizar estropee '
            'un piso; puede que perfiles distintos de host acaben en distintas escalas. Lo '
            'sólido es el patrón: lo que se erosiona al escalar es el trato humano, no lo '
            'físico.</p></div>',
            unsafe_allow_html=True)
    else:
        st.info('Muy pocos anuncios para comparar tamaños de host con estos filtros.')

st.markdown(
    '<div class="pie">Trabajo universitario · datos de '
    '<a href="http://insideairbnb.com/">Inside Airbnb</a> (Madrid, junio 2026) · '
    'limpieza y análisis exploratorio en <code>notebooks/</code> · '
    'las reseñas se usan como proxy de demanda.</div>',
    unsafe_allow_html=True)
