"""Tablero de riesgo de retraso por franja de itinerario.

Herramienta de planeacion: responde que combinaciones de aerolinea, ruta, dia y
franja horaria concentran el mayor riesgo, para decidir donde reforzar recursos y
que conexiones necesitan mas margen.

Construido con Dash sobre la maqueta de la Entrega 1. En esta entrega el tablero
carga el modelo y los datos directamente; en la Entrega 3 pasara a consumirlos a
traves de la API (ver dashboard/streamlit_app.py como prueba de ese camino).

    python dashboard/app.py    ->    http://localhost:8050
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

AZUL, CORAL, GRIS, VERDE, AMBAR = "#2A6F97", "#C1121F", "#94A3B8", "#2E7D57", "#B77500"
COLOR_BANDA = {"bajo": VERDE, "medio": AMBAR, "alto": CORAL}
DIAS = {1: "Lunes", 2: "Martes", 3: "Miercoles", 4: "Jueves",
        5: "Viernes", 6: "Sabado", 7: "Domingo"}
FRANJAS = ["00-06", "06-12", "12-18", "18-24"]
MINIMO_VUELOS_RUTA = 500
TODOS = "__todos__"


# --- Artefactos -----------------------------------------------------------


def cargar():
    modelo = joblib.load(RAIZ / "models" / "modelo_ganador.joblib")
    meta = json.loads((RAIZ / "models" / "metadata.json").read_text(encoding="utf-8"))
    vuelos = pd.read_parquet(RAIZ / "dashboard" / "data" / "vuelos.parquet")
    return modelo, meta, vuelos


try:
    MODELO, META, VUELOS = cargar()
except FileNotFoundError as exc:
    raise SystemExit(
        f"Falta un artefacto: {exc}\n"
        "Ejecuta modeling/katherin-modelos-entrega2.ipynb para generarlos."
    ) from exc

UMBRAL = float(META.get("umbral", 0.5))
BANDA_ALTA = float(META.get("banda_alta", UMBRAL + 0.15))

AEROLINEAS = sorted(VUELOS["Airline"].unique().tolist())
AEROPUERTOS = sorted(set(VUELOS["AirportFrom"]) | set(VUELOS["AirportTo"]))
_conteo_rutas = VUELOS.groupby("Ruta", observed=True).size()
RUTAS = sorted(_conteo_rutas[_conteo_rutas >= MINIMO_VUELOS_RUTA].index.tolist())

CLAVE_FRANJA = ["Airline", "AirportFrom", "AirportTo", "DayOfWeek", "Franja"]


def construir_franjas() -> pd.DataFrame:
    """Una fila por franja de itinerario, con su riesgo estimado por el modelo.

    Es la unidad de decision del tablero: lo que el equipo de planeacion refuerza
    no es un vuelo suelto sino una franja que se repite todas las semanas.

    El riesgo se toma del modelo y no de la tasa observada porque cada franja
    tiene apenas cuatro o cinco vuelos en el periodo: sobre esa muestra la tasa
    solo puede valer 0%, 25%, 50%, 75% o 100%, y ordenar por ella produciria un
    ranking dominado por el azar. El modelo, entrenado sobre las 539 mil filas,
    aprovecha lo que comparten franjas parecidas.
    """
    agrupado = (
        VUELOS.groupby(CLAVE_FRANJA, observed=True)
        .agg(Time=("Time", "median"), Length=("Length", "median"),
             vuelos=("Delay", "size"), tasa_observada=("Delay", "mean"))
        .reset_index()
    )
    agrupado["Time"] = agrupado["Time"].astype(int)
    agrupado["Length"] = agrupado["Length"].astype(int)
    agrupado["Ruta"] = (agrupado["AirportFrom"].astype(str) + "-"
                        + agrupado["AirportTo"].astype(str))
    agrupado["riesgo"] = MODELO.predict_proba(agrupado)[:, 1]
    return agrupado


FRANJAS_ITINERARIO = construir_franjas()


# --- Logica ---------------------------------------------------------------


def filtrar(aerolinea, ruta, dia, franja, datos: pd.DataFrame | None = None) -> pd.DataFrame:
    """Aplica los cuatro filtros del tablero. Sirve para vuelos y para franjas."""
    datos = VUELOS if datos is None else datos
    if aerolinea != TODOS:
        datos = datos[datos["Airline"] == aerolinea]
    if ruta != TODOS:
        datos = datos[datos["Ruta"] == ruta]
    if dia != TODOS:
        datos = datos[datos["DayOfWeek"] == int(dia)]
    if franja != TODOS:
        datos = datos[datos["Franja"] == franja]
    return datos


def banda(probabilidad: float) -> str:
    if probabilidad >= BANDA_ALTA:
        return "alto"
    if probabilidad >= UMBRAL:
        return "medio"
    return "bajo"


def franja_de(minutos: int) -> str:
    for tope, etiqueta in [(360, "00-06"), (720, "06-12"), (1080, "12-18")]:
        if minutos < tope:
            return etiqueta
    return "18-24"


def figura_vacia(mensaje: str) -> go.Figure:
    """Marcador de posicion cuando una grafica no aporta nada con esos filtros."""
    figura = go.Figure()
    figura.add_annotation(text=mensaje, showarrow=False, font=dict(size=13, color="#64748B"))
    figura.update_layout(height=320, margin=dict(l=10, r=10, t=45, b=10),
                         plot_bgcolor="white",
                         xaxis=dict(visible=False), yaxis=dict(visible=False))
    return figura


def barras_tasa_volumen(datos, columna, titulo, etiquetas=None, tope=None):
    """Tasa de retraso con el volumen de cada grupo anotado al lado.

    El volumen es lo que separa un hallazgo accionable de una curiosidad: una
    tasa del 70% sobre 300 vuelos no justifica reasignar recursos, y sin el
    numero al lado las dos barras se ven iguales.
    """
    resumen = (datos.groupby(columna, observed=True)["Delay"]
               .agg(tasa="mean", vuelos="size"))
    resumen = resumen[resumen["vuelos"] > 0].sort_values("tasa", ascending=False)
    if tope:
        resumen = resumen.nlargest(tope, "vuelos").sort_values("tasa", ascending=False)

    if len(resumen) < 2:
        # Con el filtro puesto queda una sola categoria: la grafica no compara
        # nada y el dato ya esta en los indicadores de arriba.
        return figura_vacia(f"{titulo}<br><br>Sin comparacion posible: el filtro deja"
                            f" una sola categoria.")

    indice = [etiquetas.get(i, i) if etiquetas else str(i) for i in resumen.index]
    media = datos["Delay"].mean()

    figura = go.Figure()
    figura.add_bar(
        x=resumen["tasa"], y=indice, orientation="h", marker_color=AZUL,
        text=[f"{v:,.0f} vuelos" for v in resumen["vuelos"]],
        textposition="outside", textfont=dict(size=10, color="#475569"),
        hovertemplate="%{y}<br>Tasa: %{x:.1%}<br>%{text}<extra></extra>",
    )
    figura.add_vline(x=media, line_dash="dash", line_color=CORAL)
    figura.update_layout(
        title=titulo, height=320, margin=dict(l=10, r=60, t=45, b=10),
        xaxis=dict(tickformat=".0%", range=[0, 1.05], title="Tasa de retraso"),
        # type='category' es obligatorio: sin el, Plotly interpreta etiquetas como
        # "00-06" o "12-18" como fechas y el eje sale con anos y marcas horarias.
        yaxis=dict(type="category", autorange="reversed"),
        plot_bgcolor="white",
    )
    return figura


def figura_ranking(seleccion: pd.DataFrame, tope: int = 12) -> go.Figure:
    """Las franjas de itinerario mas expuestas: la respuesta operativa del tablero.

    Es lo que el equipo de planeacion se lleva de aqui: una lista priorizada de
    combinaciones concretas sobre las que asignar refuerzo.
    """
    if seleccion.empty:
        return figura_vacia("Ninguna franja cumple esos filtros.")

    top = seleccion.nlargest(tope, "riesgo").iloc[::-1]
    etiquetas = [
        f"{f.Airline} · {f.Ruta} · {DIAS[f.DayOfWeek][:3]} · {f.Franja}"
        for f in top.itertuples()
    ]
    colores = [COLOR_BANDA[banda(r)] for r in top["riesgo"]]

    figura = go.Figure()
    figura.add_bar(
        x=top["riesgo"], y=etiquetas, orientation="h", marker_color=colores,
        text=[f"{r:.0%}" for r in top["riesgo"]],
        textposition="outside", textfont=dict(size=10, color="#475569"),
        customdata=top[["tasa_observada", "vuelos"]].to_numpy(),
        hovertemplate=("%{y}<br>Riesgo estimado: %{x:.1%}"
                       "<br>Tasa observada: %{customdata[0]:.0%}"
                       " en %{customdata[1]:.0f} vuelos<extra></extra>"),
    )
    figura.add_vline(x=UMBRAL, line_dash="dash", line_color=CORAL,
                     annotation_text="Umbral de refuerzo", annotation_position="top")
    figura.update_layout(
        title=f"Franjas de itinerario con mayor riesgo (top {tope})",
        height=430, margin=dict(l=10, r=60, t=45, b=10),
        xaxis=dict(tickformat=".0%", range=[0, 1.08], title="Riesgo estimado por el modelo"),
        yaxis=dict(type="category"), plot_bgcolor="white",
    )
    return figura


def tarjeta(titulo, valor, nota=""):
    return html.Div(
        [
            html.P(titulo, style={"fontSize": "13px", "color": "#64748B", "margin": "0 0 4px"}),
            html.P(valor, style={"fontSize": "26px", "fontWeight": 500, "margin": 0}),
            html.P(nota, style={"fontSize": "11px", "color": "#94A3B8", "margin": "2px 0 0"}),
        ],
        style={"background": "#F8FAFC", "borderRadius": "10px", "padding": "14px 16px",
               "border": "1px solid #E2E8F0", "flex": "1"},
    )


# --- Aplicacion -----------------------------------------------------------

app = Dash(__name__, meta_tags=[{"name": "viewport",
                                 "content": "width=device-width, initial-scale=1"}])
app.title = "Riesgo de retraso por franja de itinerario"
server = app.server

ESTILO_SELECT = {"minWidth": "150px", "flex": "1"}

app.layout = html.Div(
    style={"fontFamily": "system-ui, sans-serif", "maxWidth": "1280px",
           "margin": "0 auto", "padding": "24px"},
    children=[
        html.H2("Riesgo de retraso por franja de itinerario",
                style={"margin": "0 0 4px"}),
        html.P(
            "Herramienta de planeacion de red: identifica que combinaciones de aerolinea, ruta, "
            "dia y franja horaria concentran el mayor riesgo, para priorizar refuerzo de recursos "
            "y margenes de conexion.",
            style={"color": "#64748B", "margin": "0 0 20px", "fontSize": "14px"},
        ),

        html.Div(
            style={"display": "flex", "gap": "12px", "flexWrap": "wrap",
                   "background": "#F1F5F9", "padding": "14px", "borderRadius": "10px"},
            children=[
                dcc.Dropdown(id="f-aerolinea", style=ESTILO_SELECT, clearable=False,
                             value=TODOS, placeholder="Aerolinea",
                             options=[{"label": "Aerolinea: todas", "value": TODOS}]
                             + [{"label": a, "value": a} for a in AEROLINEAS]),
                dcc.Dropdown(id="f-ruta", style=ESTILO_SELECT, clearable=False,
                             value=TODOS, placeholder="Ruta",
                             options=[{"label": "Ruta: todas", "value": TODOS}]
                             + [{"label": r, "value": r} for r in RUTAS]),
                dcc.Dropdown(id="f-dia", style=ESTILO_SELECT, clearable=False,
                             value=TODOS, placeholder="Dia",
                             options=[{"label": "Dia: todos", "value": TODOS}]
                             + [{"label": n, "value": str(d)} for d, n in DIAS.items()]),
                dcc.Dropdown(id="f-franja", style=ESTILO_SELECT, clearable=False,
                             value=TODOS, placeholder="Franja",
                             options=[{"label": "Franja: todas", "value": TODOS}]
                             + [{"label": f, "value": f} for f in FRANJAS]),
            ],
        ),

        html.Div(id="kpis", style={"display": "flex", "gap": "12px", "margin": "18px 0"}),

        dcc.Graph(id="g-ranking"),
        html.P(id="nota-ranking",
               style={"color": "#64748B", "fontSize": "12px", "margin": "-6px 0 18px"}),

        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "14px"},
                 children=[dcc.Graph(id="g-aerolinea"), dcc.Graph(id="g-franja"),
                           dcc.Graph(id="g-dia"), dcc.Graph(id="g-deriva")]),

        html.Hr(style={"margin": "28px 0 20px", "border": "none",
                       "borderTop": "1px solid #E2E8F0"}),

        html.H3("Evaluar una franja de itinerario", style={"margin": "0 0 4px"}),
        html.P(id="ficha-modelo",
               style={"color": "#64748B", "fontSize": "13px", "margin": "0 0 14px"}),

        html.Div(
            style={"display": "flex", "gap": "10px", "flexWrap": "wrap",
                   "alignItems": "flex-end"},
            children=[
                html.Div([html.Label("Aerolinea", style={"fontSize": "12px"}),
                          dcc.Dropdown(id="p-aerolinea", options=AEROLINEAS, value="WN",
                                       clearable=False, style={"width": "120px"})]),
                html.Div([html.Label("Origen", style={"fontSize": "12px"}),
                          dcc.Dropdown(id="p-origen", options=AEROPUERTOS, value="DAL",
                                       clearable=False, style={"width": "120px"})]),
                html.Div([html.Label("Destino", style={"fontSize": "12px"}),
                          dcc.Dropdown(id="p-destino", options=AEROPUERTOS, value="HOU",
                                       clearable=False, style={"width": "120px"})]),
                html.Div([html.Label("Dia", style={"fontSize": "12px"}),
                          dcc.Dropdown(id="p-dia", clearable=False, value=3,
                                       options=[{"label": n, "value": d} for d, n in DIAS.items()],
                                       style={"width": "130px"})]),
                html.Div([html.Label("Hora (min desde 00:00)", style={"fontSize": "12px"}),
                          dcc.Input(id="p-hora", type="number", value=840, min=0, max=1439,
                                    style={"width": "150px", "height": "34px"})]),
                html.Div([html.Label("Duracion (min)", style={"fontSize": "12px"}),
                          dcc.Input(id="p-duracion", type="number", value=60, min=15, max=1000,
                                    style={"width": "120px", "height": "34px"})]),
                html.Button("Evaluar riesgo", id="p-boton", n_clicks=0,
                            style={"height": "38px", "padding": "0 18px", "borderRadius": "8px",
                                   "border": "none", "background": AZUL, "color": "white",
                                   "cursor": "pointer", "fontSize": "14px"}),
            ],
        ),

        html.Div(id="resultado", style={"marginTop": "20px"}),
    ],
)


@app.callback(
    Output("kpis", "children"), Output("g-ranking", "figure"), Output("nota-ranking", "children"),
    Output("g-aerolinea", "figure"), Output("g-franja", "figure"),
    Output("g-dia", "figure"), Output("g-deriva", "figure"), Output("ficha-modelo", "children"),
    Input("f-aerolinea", "value"), Input("f-ruta", "value"),
    Input("f-dia", "value"), Input("f-franja", "value"),
)
def actualizar(aerolinea, ruta, dia, franja):
    datos = filtrar(aerolinea, ruta, dia, franja)
    seleccion = filtrar(aerolinea, ruta, dia, franja, FRANJAS_ITINERARIO)

    if datos.empty:
        vacio = figura_vacia("Ninguna franja cumple esos filtros.")
        aviso = [html.Div("Ninguna franja del itinerario cumple esa combinacion de filtros.",
                          style={"color": CORAL, "padding": "14px"})]
        return aviso, vacio, "", vacio, vacio, vacio, vacio, ""

    # El conteo refleja la seleccion activa, no el dataset completo: un KPI que
    # siempre dice 539.383 no informa sobre lo que el usuario esta mirando.
    n_franjas = datos.groupby(["Airline", "Ruta", "DayOfWeek", "Franja"], observed=True).ngroups
    kpis = [
        tarjeta("Tasa de retraso", f"{datos['Delay'].mean():.1%}", "en la seleccion activa"),
        tarjeta("Vuelos en la seleccion", f"{len(datos):,}",
                f"de {len(VUELOS):,} del historico"),
        tarjeta("Franjas de itinerario", f"{n_franjas:,}",
                "combinaciones aerolinea x ruta x dia x franja"),
        tarjeta("AUC del modelo", f"{META['metricas_prueba']['roc_auc']:.3f}",
                "sobre el bloque de prueba"),
    ]

    fig_aerolinea = barras_tasa_volumen(datos, "Airline", "Tasa de retraso por aerolinea", tope=8)
    fig_franja = barras_tasa_volumen(datos, "Franja", "Tasa de retraso por franja horaria")
    fig_dia = barras_tasa_volumen(datos, "DayOfWeek", "Tasa de retraso por dia de la semana",
                                  etiquetas=DIAS)

    # La deriva no estaba en la maqueta, pero documenta visualmente por que el
    # modelo caduca y hay que reentrenarlo.
    deriva = datos.groupby("DiaCalendario")["Delay"].mean()
    fig_deriva = go.Figure()
    fig_deriva.add_scatter(x=deriva.index, y=deriva.values, mode="lines+markers",
                           line_color=AZUL, name="Tasa diaria")
    fig_deriva.add_hline(y=datos["Delay"].mean(), line_dash="dash", line_color=CORAL)
    fig_deriva.add_vrect(x0=-0.5, x1=24.5, fillcolor=GRIS, opacity=0.15, line_width=0,
                         annotation_text="Ventana de entrenamiento",
                         annotation_position="top left")
    fig_deriva.update_layout(title="Evolucion diaria de la tasa de retraso", height=320,
                             margin=dict(l=10, r=10, t=45, b=10), plot_bgcolor="white",
                             yaxis_tickformat=".0%", xaxis_title="Dia del periodo")

    fig_ranking = figura_ranking(seleccion)
    sobre_umbral = int((seleccion["riesgo"] >= UMBRAL).sum()) if not seleccion.empty else 0
    nota = (f"{sobre_umbral:,} de {len(seleccion):,} franjas de la selección superan el umbral de "
            f"refuerzo ({UMBRAL:.2f}). El riesgo lo estima el modelo, no la tasa observada: cada "
            f"franja tiene cuatro o cinco vuelos en el período y sobre esa muestra la tasa "
            f"observada solo puede valer 0%, 25%, 50%, 75% o 100%.")

    ficha = (f"Modelo: {META.get('familia')} · entrenado con {META.get('ventana_entrenamiento')} · "
             f"umbral de refuerzo {UMBRAL:.2f} ({META.get('criterio_umbral', '')}). "
             "No incorpora variables meteorologicas.")
    return (kpis, fig_ranking, nota, fig_aerolinea, fig_franja, fig_dia, fig_deriva, ficha)


@app.callback(
    Output("resultado", "children"),
    Input("p-boton", "n_clicks"),
    State("p-aerolinea", "value"), State("p-origen", "value"), State("p-destino", "value"),
    State("p-dia", "value"), State("p-hora", "value"), State("p-duracion", "value"),
    prevent_initial_call=True,
)
def evaluar(_, aerolinea, origen, destino, dia, hora, duracion):
    if origen == destino:
        return html.Div("El origen y el destino no pueden ser el mismo aeropuerto.",
                        style={"color": CORAL})
    if hora is None or duracion is None:
        return html.Div("Completa la hora y la duracion.", style={"color": CORAL})

    entrada = pd.DataFrame([{
        "Airline": aerolinea, "AirportFrom": origen, "AirportTo": destino,
        "DayOfWeek": int(dia), "Time": int(hora), "Length": int(duracion),
    }])
    probabilidad = float(MODELO.predict_proba(entrada)[0, 1])
    nivel = banda(probabilidad)

    ruta = f"{origen}-{destino}"
    referencias = {
        "Esta franja (modelo)": probabilidad,
        f"Historico {aerolinea}": VUELOS.loc[VUELOS["Airline"] == aerolinea, "Delay"].mean(),
        f"Historico {ruta}": VUELOS.loc[VUELOS["Ruta"] == ruta, "Delay"].mean(),
        f"Historico franja {franja_de(int(hora))}":
            VUELOS.loc[VUELOS["Franja"] == franja_de(int(hora)), "Delay"].mean(),
        "Media global": VUELOS["Delay"].mean(),
    }
    referencias = {k: v for k, v in referencias.items() if pd.notna(v)}

    comparativa = go.Figure()
    comparativa.add_bar(
        x=list(referencias.values()), y=list(referencias), orientation="h",
        marker_color=[COLOR_BANDA[nivel]] + [GRIS] * (len(referencias) - 1),
        text=[f"{v:.1%}" for v in referencias.values()], textposition="outside",
    )
    comparativa.update_layout(
        title="Como se compara con su historico", height=260,
        margin=dict(l=10, r=50, t=45, b=10), plot_bgcolor="white",
        xaxis=dict(tickformat=".0%", range=[0, 1.05]), yaxis=dict(autorange="reversed"),
    )

    accion = ("Priorizar en el plan de refuerzo" if nivel == "alto"
              else "Considerar si hay capacidad disponible" if nivel == "medio"
              else "No requiere refuerzo especifico")

    return html.Div(
        style={"display": "grid", "gridTemplateColumns": "260px 1fr", "gap": "18px",
               "alignItems": "start"},
        children=[
            html.Div(
                style={"background": COLOR_BANDA[nivel], "color": "white", "padding": "20px",
                       "borderRadius": "10px", "textAlign": "center"},
                children=[
                    html.P(f"Riesgo {nivel}", style={"margin": 0, "fontSize": "13px",
                                                     "opacity": 0.85}),
                    html.P(f"{probabilidad:.0%}", style={"margin": "4px 0",
                                                         "fontSize": "36px", "fontWeight": 600}),
                    html.P(accion, style={"margin": 0, "fontSize": "12px", "opacity": 0.9}),
                    html.P(f"Umbral de refuerzo: {UMBRAL:.2f}",
                           style={"margin": "8px 0 0", "fontSize": "11px", "opacity": 0.75}),
                ],
            ),
            dcc.Graph(figure=comparativa),
        ],
    )


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
