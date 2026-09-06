"""Datos, tokens y componentes compartidos por la suite de dashboards."""
from __future__ import annotations

import html
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from airlines_ml.data import cargar_crudo, limpiar
from airlines_ml.features import agregar_derivadas

OUTPUT_DIR = Path(__file__).resolve().parent / "output"

INK = "#E5EDF5"
MUTED = "#A7B6C7"
PLOT = "#0D1B2A"
BLUE = "#4DA3FF"
RED = "#FF7A59"
GREEN = "#5BC0BE"
GOLD = "#F5C518"
AIRPORT = "#7CC4FA"
ROUTE = "#8E8CF3"
BORDER = "#183248"
PANEL_EMPHASIS = "#0A1928"
FONT_FAMILY = "Inter, Segoe UI, sans-serif"
GLOBAL_DELAY_RATE = 240_263 / 539_379

DAY_NAMES = {
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes",
    6: "Sábado",
    7: "Domingo",
}


def load_data() -> pd.DataFrame:
    """Carga y prepara los datos con las reglas compartidas del proyecto."""
    data = agregar_derivadas(limpiar(cargar_crudo()))
    required = {"Delay"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {sorted(missing)}")
    return data


def apply_figure_style(figure: go.Figure, height: int) -> go.Figure:
    """Aplica el tema visual compartido a una figura Plotly."""
    figure.update_layout(
        height=height,
        margin=dict(l=44, r=34, t=54, b=42),
        paper_bgcolor=PLOT,
        plot_bgcolor=PLOT,
        font=dict(family=FONT_FAMILY, color=INK, size=13),
        title_font=dict(size=16, color=INK),
        hoverlabel=dict(bgcolor=BORDER, font_color=INK),
    )
    figure.update_xaxes(gridcolor=BORDER, zeroline=False)
    figure.update_yaxes(gridcolor=BORDER, zeroline=False)
    return figure


def metric_card(label: str, value: str, note: str) -> str:
    """Construye una tarjeta KPI del sistema compartido."""
    return (
        '<article class="metric">'
        f"<span>{html.escape(label)}</span>"
        f"<strong>{html.escape(value)}</strong>"
        f"<small>{html.escape(note)}</small>"
        "</article>"
    )


def render_document(
    *,
    title: str,
    description: str,
    priority_criteria: list[str],
    summary_text: str,
    analysis_text: str,
    cards: list[str],
    matrix_figure: go.Figure,
    intervention_figure: go.Figure,
    findings: list[str],
    executive_message: str,
    methodology: str,
    output_name: str,
) -> Path:
    """Genera un dashboard de priorización con los componentes compartidos."""
    findings_html = "".join(f"<li>{html.escape(item)}</li>" for item in findings)
    criteria_html = "".join(
        f"<li>{html.escape(item)}</li>" for item in priority_criteria
    )
    matrix_html = pio.to_html(
        matrix_figure,
        full_html=False,
        include_plotlyjs="cdn",
        config={"displayModeBar": False, "responsive": True},
        div_id="operational-prioritization-chart-1",
    )
    intervention_html = pio.to_html(
        intervention_figure,
        full_html=False,
        include_plotlyjs=False,
        config={"displayModeBar": False, "responsive": True},
        div_id="operational-prioritization-chart-2",
    )

    document = f"""<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../dashboard-design-system.css">
</head>
<body class="dashboard-suite">
<main>
    <header>
        <h1>{html.escape(title)}</h1>
        <p class="page-intro">{html.escape(description)}</p>
    </header>
    <section class="dashboard-section" aria-labelledby="resumen-priorizacion">
        <div class="section-heading">
            <h2 id="resumen-priorizacion">Resumen de priorización</h2>
            <p>{html.escape(summary_text)}</p>
        </div>
        <div class="metrics">{"".join(cards)}</div>
    </section>
    <aside class="decision-criteria" aria-labelledby="criterio-prioridad">
        <div>
            <h2 id="criterio-prioridad">¿Cómo se determina la prioridad?</h2>
            <p>La prioridad histórica se define mediante la combinación de:</p>
        </div>
        <ul>{criteria_html}</ul>
    </aside>
    <section class="dashboard-section" aria-labelledby="fundamento-priorizacion">
        <div class="section-heading">
            <h2 id="fundamento-priorizacion">Fundamento de la priorización</h2>
            <p>{html.escape(analysis_text)}</p>
        </div>
        <article class="panel chart-panel chart priority-visual">{matrix_html}</article>
    </section>
    <section class="dashboard-section" aria-labelledby="plan-atencion">
        <div class="section-heading">
            <h2 id="plan-atencion">Plan progresivo de atención</h2>
            <p>¿Qué segmentos merecen atención primero y cuánto retraso concentran?</p>
        </div>
        <article class="panel chart-panel chart">{intervention_html}</article>
    </section>
    <aside class="methodology"><strong>Nota metodológica:</strong> {html.escape(methodology)}</aside>
    <section class="dashboard-section" aria-labelledby="hallazgos-priorizacion">
        <div class="panel findings-panel">
            <h2 id="hallazgos-priorizacion">Hallazgos de priorización</h2>
            <ul class="insights">{findings_html}</ul>
        </div>
    </section>
    <p class="executive-takeaway">{html.escape(executive_message)}</p>
</main>
</body>
</html>
"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / output_name
    output.write_text(document, encoding="utf-8")
    return output
