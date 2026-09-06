"""Genera el diagnóstico táctico de patrones de retraso en formato HTML."""
from __future__ import annotations

import html
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from common import (
    AIRPORT as AIRPORT_COLOR,
    BLUE as PRIMARY,
    BORDER,
    GLOBAL_DELAY_RATE as GLOBAL_RATE,
    GOLD as BENCHMARK_COLOR,
    INK as TEXT,
    MUTED as MUTED_TEXT,
    OUTPUT_DIR,
    PLOT as PANEL,
    RED as TIME_COLOR,
    ROUTE as ROUTE_COLOR,
    apply_figure_style,
    load_data,
)

MINIMUM_AIRPORT_FLIGHTS = 500
MINIMUM_ROUTE_FLIGHTS = 500
BENCHMARK_TERMS = re.compile(r"44,54%|media global|referencia global|referencia", re.IGNORECASE)


def narrative_html(text: str) -> str:
    """Destaca las referencias narrativas con el color único del benchmark."""
    escaped = html.escape(text)
    return BENCHMARK_TERMS.sub(
        lambda match: f'<span class="benchmark-reference">{match.group(0)}</span>',
        escaped,
    )


def summarize(data: pd.DataFrame, column: str) -> pd.DataFrame:
    """Calcula volumen, retrasos y tasa para una dimensión categórica."""
    return (
        data.groupby(column, observed=True)["Delay"]
        .agg(vuelos="size", retrasos="sum", tasa="mean")
        .reset_index()
    )


def select_segments(
    summary: pd.DataFrame,
    column: str,
    *,
    top: int = 10,
    impact_top: int = 3,
    labels: dict | None = None,
) -> pd.DataFrame:
    """Selecciona y etiqueta los mismos segmentos para los visuales coordinados."""
    selected = (
        pd.concat(
            [summary.nlargest(top, "tasa"), summary.nlargest(impact_top, "retrasos")]
        )
        .drop_duplicates(subset=[column])
        .sort_values("tasa")
        .copy()
    )
    selected["categoria"] = [
        str(labels.get(value, value)) if labels else str(value)
        for value in selected[column]
    ]
    selected["diferencia_pp"] = (selected["tasa"] - GLOBAL_RATE) * 100
    selected["sin_retraso"] = selected["vuelos"] - selected["retrasos"]
    return selected


def add_global_benchmark(figure: go.Figure) -> None:
    """Agrega una referencia global idéntica a todos los gráficos de tasa."""
    figure.add_vline(
        x=GLOBAL_RATE,
        line_dash="dash",
        line_color=BENCHMARK_COLOR,
        line_width=4,
        annotation_text="Media global · 44,54%",
        annotation_position="top",
        annotation=dict(
            bgcolor=BENCHMARK_COLOR,
            bordercolor=BENCHMARK_COLOR,
            borderpad=6,
            font=dict(color=PANEL, size=12),
        ),
    )


def exposure_chart(
    selected: pd.DataFrame,
    title: str,
    color: str,
) -> go.Figure:
    """Muestra exposición y distancia frente a la media global."""
    bar_colors = [color if rate > GLOBAL_RATE else MUTED_TEXT for rate in selected["tasa"]]
    opacities = [1.0 if rate > GLOBAL_RATE else 0.48 for rate in selected["tasa"]]

    figure = go.Figure()
    figure.add_bar(
        x=selected["tasa"],
        y=selected["categoria"],
        orientation="h",
        marker=dict(color=bar_colors, opacity=opacities),
        text=[
            f"{rate:.1%} · {difference:+.1f} pp"
            for rate, difference in zip(selected["tasa"], selected["diferencia_pp"])
        ],
        textposition="outside",
        cliponaxis=False,
        customdata=selected[["vuelos", "retrasos", "diferencia_pp"]].to_numpy(),
        hovertemplate=(
            "%{y}<br>Tasa: %{x:.2%}<br>Vuelos: %{customdata[0]:,}"
            "<br>Retrasos: %{customdata[1]:,}<br>Diferencia: %{customdata[2]:+.2f} pp"
            "<extra></extra>"
        ),
    )
    add_global_benchmark(figure)
    figure.update_layout(
        title=title,
        xaxis=dict(tickformat=".0%", range=[0, 0.88], title="Tasa de retraso"),
        yaxis=dict(type="category", title=None),
        showlegend=False,
    )
    return apply_figure_style(figure, height=max(350, 54 * len(selected)))


def impact_chart(
    summary: pd.DataFrame,
    column: str,
    title: str,
    color: str,
    *,
    top: int = 10,
    labels: dict | None = None,
) -> go.Figure:
    """Ordena los segmentos que generan más retrasos absolutos."""
    selected = summary.nlargest(top, "retrasos").sort_values("retrasos").copy()
    selected["categoria"] = [
        str(labels.get(value, value)) if labels else str(value)
        for value in selected[column]
    ]
    figure = go.Figure()
    figure.add_bar(
        x=selected["retrasos"],
        y=selected["categoria"],
        orientation="h",
        marker_color=color,
        customdata=selected[["tasa", "vuelos"]].to_numpy(),
        hovertemplate=(
            "%{y}<br>Retrasos: %{x:,}<br>Vuelos: %{customdata[1]:,}"
            "<br>Tasa: %{customdata[0]:.2%}<extra></extra>"
        ),
    )
    figure.update_layout(
        title=title,
        xaxis=dict(title="Retrasos observados", tickformat=","),
        yaxis=dict(type="category", title=None),
        showlegend=False,
    )
    return apply_figure_style(figure, height=max(350, 54 * len(selected)))


def delay_share_chart(
    summary: pd.DataFrame,
    column: str,
    title: str,
    color: str,
    *,
    labels: dict | None = None,
) -> go.Figure:
    """Muestra qué proporción de todos los retrasos aporta cada segmento."""
    selected = summary.copy()
    selected["categoria"] = [
        str(labels.get(value, value)) if labels else str(value)
        for value in selected[column]
    ]
    selected["participacion"] = selected["retrasos"] / selected["retrasos"].sum()
    figure = go.Figure(
        go.Bar(
            x=selected["categoria"],
            y=selected["participacion"],
            marker_color=color,
            customdata=selected[["retrasos", "vuelos", "tasa"]].to_numpy(),
            hovertemplate=(
                "%{x}<br>Participación: %{y:.1%}<br>Retrasos: %{customdata[0]:,}"
                "<br>Vuelos: %{customdata[1]:,}<br>Tasa: %{customdata[2]:.2%}<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        title=title,
        xaxis=dict(title=None),
        yaxis=dict(title="% de retrasos", tickformat=".0%"),
        showlegend=False,
    )
    return apply_figure_style(figure, height=350)


def exposure_impact_matrix(dimensions: list[tuple[str, pd.DataFrame, str]]) -> go.Figure:
    """Permite comparar tasa, volumen y retrasos entre dimensiones en un solo visual."""
    figure = go.Figure()
    buttons = []
    impact_cuts = []
    for index, (name, summary, color) in enumerate(dimensions):
        matrix_data = summary.copy()
        impact_cut = float(matrix_data["retrasos"].median())
        impact_cuts.append(impact_cut)
        figure.add_scatter(
            x=matrix_data["tasa"],
            y=matrix_data["retrasos"],
            mode="markers",
            name=name,
            visible=index == 0,
            marker=dict(
                color=color,
                size=np.clip(8 + matrix_data["vuelos"] / 3500, 9, 32),
                opacity=0.78,
                line=dict(color=TEXT, width=0.8),
            ),
            customdata=np.column_stack(
                [matrix_data["categoria"], matrix_data["vuelos"]]
            ),
            hovertemplate=(
                "%{customdata[0]}<br>Tasa: %{x:.2%}<br>Retrasos: %{y:,}"
                "<br>Vuelos: %{customdata[1]:,}<extra></extra>"
            ),
        )
        visibility = [position == index for position in range(len(dimensions))]
        buttons.append(
            dict(
                label=name,
                method="update",
                args=[
                    {"visible": visibility},
                    {
                        "title": f"Exposición e impacto · {name}",
                        "shapes[1].y0": impact_cut,
                        "shapes[1].y1": impact_cut,
                        "annotations[1].y": impact_cut,
                    },
                ],
            )
        )

    add_global_benchmark(figure)
    figure.add_hline(
        y=impact_cuts[0],
        line_dash="dot",
        line_color=MUTED_TEXT,
        line_width=2,
        annotation_text="Mediana de impacto",
        annotation_position="right",
        annotation_font_color=MUTED_TEXT,
    )
    figure.update_layout(
        title="Exposición e impacto · Aerolínea",
        xaxis=dict(tickformat=".0%", title="Tasa de retraso"),
        yaxis=dict(title="Retrasos observados", tickformat=","),
        showlegend=False,
        updatemenus=[
            dict(
                buttons=buttons,
                direction="right",
                x=0,
                xanchor="left",
                y=1.18,
                yanchor="top",
                bgcolor=PANEL,
                bordercolor=BORDER,
                font=dict(color=TEXT),
            )
        ],
    )
    return apply_figure_style(figure, height=500)


def metric_card(label: str, value: str, note: str) -> str:
    return (
        '<article class="metric">'
        f"<span>{html.escape(label)}</span>"
        f"<strong>{html.escape(value)}</strong>"
        f"<small>{narrative_html(note)}</small>"
        "</article>"
    )


def figure_html(figure: go.Figure, index: int) -> str:
    return pio.to_html(
        figure,
        full_html=False,
        include_plotlyjs="cdn" if index == 1 else False,
        config={"displayModeBar": False, "responsive": True},
        div_id=f"tactical-diagnosis-chart-{index}",
    )


def render_tactical_html(
    *,
    cards: list[str],
    matrix: go.Figure,
    modules: list[tuple[str, str, go.Figure, go.Figure | None, str]],
    findings: list[str],
    executive_message: str,
) -> str:
    matrix_block = figure_html(matrix, 1)
    module_blocks = []
    figure_index = 2
    for module_id, title, exposure, secondary, synthesis in modules:
        exposure_block = figure_html(exposure, figure_index)
        figure_index += 1
        if secondary is None:
            visuals = f'<article class="panel chart-panel">{exposure_block}</article>'
        else:
            secondary_block = figure_html(secondary, figure_index)
            figure_index += 1
            visuals = (
                '<div class="paired-visuals">'
                f'<article class="panel chart-panel primary-visual">{exposure_block}</article>'
                f'<article class="panel chart-panel secondary-visual">{secondary_block}</article>'
                '</div>'
            )
        module_blocks.append(
            f'<section class="dimension-module" aria-labelledby="{module_id}">'
            f'<div class="section-heading"><h3 id="{module_id}">{html.escape(title)}</h3></div>'
            f'{visuals}'
            f'<p class="module-synthesis"><strong>Síntesis:</strong> {narrative_html(synthesis)}</p>'
            '</section>'
        )
    operational_modules = "".join(module_blocks[:2])
    geographic_modules = "".join(module_blocks[2:])
    findings_html = "".join(f"<li>{narrative_html(item)}</li>" for item in findings)

    return f"""<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Patrones tácticos de retraso</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../dashboard-design-system.css">
</head>
<body class="dashboard-suite">
<main>
    <header>
        <h1>Patrones tácticos de retraso</h1>
        <p class="page-intro">Concentración de retrasos de vuelos por operador, horario y ubicación.</p>
    </header>

    <section class="dashboard-section" aria-labelledby="resumen-tactico">
        <div class="section-heading">
            <h2 id="resumen-tactico">Resumen táctico</h2>
            <p>Principales focos de exposición observados en la operación.</p>
        </div>
        <div class="metrics metrics--four">{"".join(cards)}</div>
    </section>

    <section class="dashboard-section" aria-labelledby="mapa-general">
        <div class="section-heading">
            <h2 id="mapa-general">Mapa general de exposición e impacto</h2>
            <p>La tasa mide exposición, los retrasos representan impacto y el tamaño indica volumen de vuelos. La línea <span class="benchmark-reference">44,54%</span> es la referencia global.</p>
        </div>
        <article class="panel chart-panel overview-panel">{matrix_block}</article>
    </section>

    <section class="dashboard-section" aria-labelledby="patrones-operativos">
        <div class="section-heading">
            <h2 id="patrones-operativos">Patrones operativos</h2>
            <p>Exposición e impacto observados por aerolínea y franja horaria.</p>
        </div>
        {operational_modules}
    </section>

    <section class="dashboard-section" aria-labelledby="patrones-geograficos">
        <div class="section-heading">
            <h2 id="patrones-geograficos">Patrones geográficos</h2>
            <p>Concentración observada por aeropuerto de origen y ruta frecuente.</p>
        </div>
        {geographic_modules}
    </section>

    <section class="dashboard-section" aria-labelledby="hallazgos-tacticos">
        <div class="panel findings-panel">
            <div><h2 id="hallazgos-tacticos">Hallazgos tácticos</h2><ul class="insights">{findings_html}</ul></div>
        </div>
    </section>
    <p class="executive-takeaway">{html.escape(executive_message)}</p>
</main>
</body>
</html>
"""


def generate() -> None:
    data = load_data()
    required = {"Airline", "AirportFrom", "Delay", "Ruta", "Franja"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Faltan columnas tácticas requeridas: {sorted(missing)}")

    airline = summarize(data, "Airline")
    time_band = summarize(data, "Franja")
    airport = summarize(data, "AirportFrom")
    route = summarize(data, "Ruta")

    airport = airport[airport["vuelos"] >= MINIMUM_AIRPORT_FLIGHTS]
    route = route[route["vuelos"] >= MINIMUM_ROUTE_FLIGHTS]

    selected_airline = select_segments(airline, "Airline")
    selected_band = select_segments(time_band, "Franja", top=4)
    selected_airport = select_segments(airport, "AirportFrom", top=7, impact_top=3)
    matrix_dimensions = [
        ("Aerolínea", select_segments(airline, "Airline", top=len(airline)), PRIMARY),
        ("Franja", select_segments(time_band, "Franja", top=len(time_band)), TIME_COLOR),
        ("Aeropuerto", select_segments(airport, "AirportFrom", top=len(airport)), AIRPORT_COLOR),
        ("Ruta", select_segments(route, "Ruta", top=len(route)), ROUTE_COLOR),
    ]
    matrix = exposure_impact_matrix(matrix_dimensions)

    module_specs = [
        (
            "aerolineas",
            "Exposición e impacto por aerolínea",
            exposure_chart(selected_airline, "Tasa y diferencia frente a la media", PRIMARY),
            impact_chart(airline, "Airline", "Aerolíneas que generan más retrasos", PRIMARY),
            f"{int((airline['tasa'] > GLOBAL_RATE).sum())} de {len(airline)} aerolíneas superan "
            f"la media global. Las tres con más retrasos concentran "
            f"{airline.nlargest(3, 'retrasos')['retrasos'].sum() / airline['retrasos'].sum():.1%} "
            "del impacto; WN lidera simultáneamente exposición e impacto.",
        ),
        (
            "franjas",
            "Concentración de retrasos por franja horaria",
            exposure_chart(selected_band, "Tasa y diferencia frente a la media", TIME_COLOR),
            delay_share_chart(time_band, "Franja", "Participación de los retrasos por franja", TIME_COLOR),
            f"La franja 12-18 concentra "
            f"{time_band.loc[time_band['Franja'] == '12-18', 'retrasos'].iloc[0] / time_band['retrasos'].sum():.1%} "
            "de todos los retrasos, mientras 18-24 presenta la mayor tasa. El incremento de "
            "exposición se concentra en la segunda mitad del día.",
        ),
        (
            "aeropuertos",
            "Exposición e impacto por aeropuerto de origen",
            exposure_chart(selected_airport, "Tasa y diferencia frente a la media", AIRPORT_COLOR),
            None,
            "MDW presenta la mayor exposición y ATL concentra el mayor impacto absoluto. "
            "Los líderes por tasa e impacto no coinciden, evidenciando patrones geográficos distintos.",
        ),
        (
            "rutas",
            "Impacto absoluto en rutas frecuentes",
            impact_chart(route, "Ruta", "Rutas que concentran más retrasos", ROUTE_COLOR),
            None,
            "DAL-HOU presenta la mayor exposición entre rutas frecuentes y LAX-SFO concentra "
            "el mayor impacto absoluto. Tasa e impacto describen focos diferentes.",
        ),
    ]
    modules = module_specs

    airline_above = airline.loc[airline["tasa"] > GLOBAL_RATE].sort_values("tasa", ascending=False)
    bands_above = time_band.loc[time_band["tasa"] > GLOBAL_RATE]
    main_airline = airline.nlargest(1, "tasa").iloc[0]
    cards = [
        metric_card(
            "Referencia global",
            f"{GLOBAL_RATE:.2%}",
            "Benchmark común de exposición",
        ),
        metric_card(
            "Aerolíneas sobre benchmark",
            f"{len(airline_above)} de {len(airline)}",
            "Operadores con tasa superior al 44,54%",
        ),
        metric_card(
            "Franjas sobre benchmark",
            f"{len(bands_above)} de {len(time_band)}",
            "Ambas se ubican en la segunda mitad del día",
        ),
        metric_card(
            "Segmento con mayor exposición e impacto",
            str(main_airline["Airline"]),
            f"{main_airline['tasa']:.1%} · {int(main_airline['retrasos']):,} retrasos",
        ),
    ]
    airline_names = ", ".join(airline_above["Airline"].astype(str))
    bands_above_half = time_band.loc[time_band["tasa"] > 0.5, "Franja"].astype(str).tolist()
    band_names = " y ".join(bands_above_half)
    findings = [
        f"La exposición se concentra en una minoría de operadores: solo {len(airline_above)} "
        f"de {len(airline)} superan la media global ({airline_names}).",
        f"La segunda mitad del día concentra simultáneamente tasas más elevadas y mayor "
        f"proporción del impacto observado; las franjas {band_names} superan el 50% de retrasos.",
        "Los focos geográficos de exposición e impacto no coinciden: MDW y DAL-HOU lideran "
        "por tasa, mientras ATL y LAX-SFO concentran más retrasos absolutos.",
    ]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / "tactical_diagnosis.html"
    output.write_text(
        render_tactical_html(
            cards=cards,
            matrix=matrix,
            modules=modules,
            findings=findings,
            executive_message=(
                "La exposición y el impacto no siempre se concentran en los mismos segmentos."
            ),
        ),
        encoding="utf-8",
    )
    print(f"Generado: {output}")


if __name__ == "__main__":
    generate()
