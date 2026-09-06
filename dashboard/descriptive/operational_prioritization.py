"""Genera vistas de concentración e impacto histórico para priorización."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common import (
    BLUE,
    GOLD,
    GREEN,
    GLOBAL_DELAY_RATE,
    INK,
    MUTED,
    RED,
    apply_figure_style,
    load_data,
    metric_card,
    render_document,
)

MINIMUM_SUPPORT = 100


def segment_summary(
    data: pd.DataFrame,
    columns: list[str],
    label: str,
) -> pd.DataFrame:
    """Resume segmentos comparables para priorización por exposición e impacto."""
    summary = (
        data.groupby(columns, observed=True)["Delay"]
        .agg(vuelos="size", retrasos="sum", tasa="mean")
        .reset_index()
    )
    summary["segmento"] = summary.apply(lambda row: label.format(**row), axis=1)
    total_delays = summary["retrasos"].sum()
    summary["participacion"] = summary["retrasos"] / total_delays
    return summary


def pareto_chart(summary: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    eligible = summary[
        (summary["vuelos"] >= MINIMUM_SUPPORT)
        & (summary["tasa"] > GLOBAL_DELAY_RATE)
    ]
    top = eligible.nlargest(10, "retrasos").copy()
    top["acumulado"] = top["participacion"].cumsum()
    checkpoints = {1, 3, 5, 10}
    checkpoint_labels = [
        f"{share:.1%}" if position in checkpoints else ""
        for position, share in enumerate(top["acumulado"], start=1)
    ]

    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_bar(
        x=top["segmento"],
        y=top["retrasos"],
        name="Retrasos",
        marker_color=BLUE,
        customdata=top[["vuelos", "tasa", "participacion"]].to_numpy(),
        hovertemplate=(
            "%{x}<br>Retrasos: %{y:,}<br>Vuelos: %{customdata[0]:,}"
            "<br>Tasa: %{customdata[1]:.1%}<br>Participación: %{customdata[2]:.2%}"
            "<extra></extra>"
        ),
        secondary_y=False,
    )
    figure.add_scatter(
        x=top["segmento"],
        y=top["acumulado"],
        mode="lines+markers+text",
        name="Participación acumulada de retrasos",
        line=dict(color=RED, width=3),
        marker=dict(size=[10 if position in checkpoints else 6 for position in range(1, 11)]),
        text=checkpoint_labels,
        textposition="top center",
        hovertemplate="%{x}<br>Participación acumulada: %{y:.1%}<extra></extra>",
        secondary_y=True,
    )
    figure.update_layout(title="Plan progresivo de atención · Aerolínea y franja")
    figure.update_xaxes(tickangle=-28, title=None)
    figure.update_yaxes(title_text="Retrasos", secondary_y=False)
    figure.update_yaxes(
        tickformat=".0%", title_text="Participación acumulada", secondary_y=True
    )
    return apply_figure_style(figure, height=570), top


def exposure_impact_matrix(summary: pd.DataFrame) -> go.Figure:
    supported = summary[summary["vuelos"] >= MINIMUM_SUPPORT].copy()
    impact_cut = supported["retrasos"].quantile(0.75)
    supported["marker_size"] = np.interp(
        np.sqrt(supported["vuelos"]),
        [np.sqrt(supported["vuelos"].min()), np.sqrt(supported["vuelos"].max())],
        [10, 32],
    )
    supported["perfil"] = np.where(
        (supported["tasa"] >= GLOBAL_DELAY_RATE) & (supported["retrasos"] >= impact_cut),
        "Prioridad histórica",
        "Contexto",
    )
    colors = {
        "Prioridad histórica": GOLD,
        "Contexto": MUTED,
    }

    figure = go.Figure()
    for profile, group in supported.groupby("perfil"):
        figure.add_scatter(
            x=group["tasa"],
            y=group["retrasos"],
            mode="markers",
            name=profile,
            marker=dict(
                color=colors[profile],
                size=group["marker_size"],
                opacity=0.72,
                line=dict(color="white", width=0.6),
            ),
            customdata=group[["segmento", "vuelos"]].to_numpy(),
            hovertemplate=(
                "%{customdata[0]}<br>Exposición: %{x:.1%}<br>Impacto: %{y:,} retrasos"
                "<br>Vuelos: %{customdata[1]:,}<extra></extra>"
            ),
        )
    figure.add_vline(x=GLOBAL_DELAY_RATE, line_dash="dash", line_color=GOLD)
    figure.add_hline(y=impact_cut, line_dash="dot", line_color=GREEN)
    figure.update_layout(
        title="Matriz exposición-impacto",
        xaxis=dict(tickformat=".0%", tickangle=0, title="Exposición"),
        yaxis=dict(title="Impacto · retrasos"),
        legend=dict(orientation="h", x=0, y=1.02, yanchor="bottom"),
    )
    return apply_figure_style(figure, height=620)


def generate() -> None:
    data = load_data()
    operational = segment_summary(
        data,
        ["Airline", "Franja"],
        "{Airline} · {Franja}",
    )
    pareto, top = pareto_chart(operational)
    cumulative_delays = top["retrasos"].cumsum()
    cumulative_share = top["participacion"].cumsum()
    top_three_delays = int(cumulative_delays.iloc[2])
    top_three_share = float(cumulative_share.iloc[2])
    top_ten_delays = int(cumulative_delays.iloc[9])
    top_share = float(top["participacion"].sum())
    leader = top.iloc[0]

    output = render_document(
        title="Priorización de exposición e impacto",
        description=(
            "Identificación de los segmentos que merecen atención por su tasa y volumen histórico "
            "de retrasos. Análisis descriptivo: no estima riesgo futuro ni el efecto de una intervención."
        ),
        priority_criteria=[
            "Exposición superior al benchmark",
            "Impacto absoluto observado",
            "Tamaño muestral suficiente",
            "Volumen histórico de retrasos",
        ],
        summary_text="Concentración acumulada de los segmentos priorizados con datos históricos.",
        analysis_text=(
            "La matriz identifica los segmentos que combinan exposición superior al benchmark e "
            "impacto absoluto relevante."
        ),
        cards=[
            metric_card(
                "Primera prioridad de atención",
                str(leader["segmento"]),
                f"{int(leader['retrasos']):,} retrasos · {leader['participacion']:.2%} del total",
            ),
            metric_card(
                "Retrasos acumulados del Top 3",
                f"{top_three_delays:,}",
                f"retrasos · {top_three_share:.2%} del total",
            ),
            metric_card(
                "Retrasos acumulados del Top 10",
                f"{top_ten_delays:,}",
                f"retrasos · {top_share:.2%} del total",
            ),
        ],
        matrix_figure=exposure_impact_matrix(operational),
        intervention_figure=pareto,
        findings=[
            f"La primera prioridad de atención histórica es {leader['segmento']}, con {int(leader['retrasos']):,} "
            f"retrasos en {int(leader['vuelos']):,} vuelos ({leader['tasa']:.1%}).",
            f"Las tres primeras prioridades acumulan {top_three_delays:,} retrasos, equivalentes al "
            f"{top_three_share:.2%} del total histórico.",
            f"Las diez prioridades de aerolínea y franja concentran {top_share:.2%} de todos los "
            "retrasos observados.",
        ],
        executive_message=(
            "Las diez principales prioridades concentran casi la mitad de los retrasos "
            "observados."
        ),
        methodology=(
            "La concentración se mide mediante el número de vuelos retrasados; no se estiman costos, "
            f"severidad ni beneficios de intervención. La priorización considera segmentos "
            f"con al menos {MINIMUM_SUPPORT} vuelos y exposición superior al benchmark global. "
            "El orden indica atención analítica basada en datos históricos; no constituye una "
            "recomendación operativa ni representa probabilidad futura."
        ),
        output_name="operational_prioritization.html",
    )
    print(f"Generado: {output}")


if __name__ == "__main__":
    generate()
