"""Genera la visión estratégica de retrasos en formato HTML."""
from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

from common import (
    FONT_FAMILY,
    GREEN as ON_TIME_COLOR,
    INK as TEXT,
    OUTPUT_DIR,
    PLOT as PANEL,
    RED as DELAY_COLOR,
    apply_figure_style,
    load_data,
)


def build_distribution_figure(delayed: int, on_time: int) -> go.Figure:
        """Resume la composición y destaca la estrecha brecha entre ambos estados."""
        total = delayed + on_time
        delayed_rate = delayed / total
        on_time_rate = on_time / total
        gap = on_time_rate - delayed_rate

        figure = go.Figure(
                go.Pie(
                        labels=["Con retraso", "Sin retraso"],
                        values=[delayed, on_time],
                        hole=0.68,
                        sort=False,
                        direction="clockwise",
                        marker=dict(
                            colors=[DELAY_COLOR, ON_TIME_COLOR],
                            line=dict(color=PANEL, width=4),
                        ),
                        textinfo="percent",
                        textfont=dict(color=TEXT, size=17),
                        hovertemplate="%{label}<br>%{value:,} vuelos<br>%{percent}<extra></extra>",
                )
        )
        figure.add_annotation(
            text=f"<b>{gap * 100:.2f} pp</b><br><span style='font-size:12px'>de diferencia</span>",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(family=FONT_FAMILY, color=TEXT, size=24),
        )
        apply_figure_style(figure, height=320)
        figure.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.02, xanchor="center", x=0.5),
        )
        return figure


def render_strategic_html(
        *, total: int, delayed: int, on_time: int, delay_rate: float
) -> str:
    on_time_rate = on_time / total
    percentage_gap = on_time_rate - delay_rate
    figure_html = pio.to_html(
        build_distribution_figure(delayed, on_time),
        full_html=False,
        include_plotlyjs="cdn",
        config={"displayModeBar": False, "responsive": True},
        div_id="strategic-overview-chart-1",
    )

    return f"""<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Panorama general de los retrasos</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../dashboard-design-system.css">
</head>
<body class="dashboard-suite">
<main>
    <header>
        <h1>Panorama general de los retrasos</h1>
        <p class="page-intro">Dimensión general del problema de retrasos de vuelos en la operación analizada.</p>
    </header>
    <section class="hero">
        <div><div class="section-label">Tasa global de retraso</div>
            <div class="hero-value">{delay_rate:.2%}</div>
            <p class="hero-copy">Casi 45 de cada 100 vuelos presentan retraso.</p></div>
        <div class="hero-context"><strong>Contexto del indicador</strong>
            La tasa global de retraso resume la proporción de vuelos que presentaron retraso dentro de la
            muestra analizada. Este indicador ofrece una visión general del comportamiento observado antes de
            examinar aerolíneas, rutas u horarios específicos.</div>
    </section>
    <section class="dashboard-section" aria-labelledby="resumen-estrategico">
        <div class="section-heading"><h2 id="resumen-estrategico">Resumen estratégico</h2></div>
        <div class="metrics">
            <article class="metric"><span>Vuelos analizados</span><strong>{total:,}</strong></article>
            <article class="metric"><span>Con retraso</span><strong>{delayed:,}</strong>
                <small>{delay_rate:.2%} del total</small></article>
            <article class="metric"><span>Sin retraso</span><strong>{on_time:,}</strong>
                <small>{on_time_rate:.2%} del total</small></article>
        </div>
    </section>
    <section class="dashboard-section" aria-labelledby="analisis-estrategico">
        <div class="section-heading"><h2 id="analisis-estrategico">Análisis estratégico</h2></div>
        <div class="analysis-grid">
            <article class="panel chart-panel"><h2>Proporción de vuelos con y sin retraso</h2>{figure_html}</article>
            <article class="panel findings-panel"><h2>Hallazgos estratégicos</h2>
                <ul class="insights">
                    <li>El {delay_rate:.1%} de los vuelos presenta retraso; equivale a cerca de 45 de cada 100.</li>
                    <li>La diferencia entre vuelos sin retraso y retrasados es de {percentage_gap * 100:.1f} puntos porcentuales, equivalente a {on_time - delayed:,} vuelos.</li>
                    <li>La distribución observada sugiere que los retrasos son un comportamiento recurrente y no un evento aislado dentro de la muestra analizada.</li>
                </ul>
            </article>
        </div>
    </section>
    <p class="executive-takeaway">Casi uno de cada dos vuelos presenta retrasos.</p>
</main>
</body>
</html>
"""


def generate() -> None:
        data = load_data()
        total = len(data)
        delayed = int(data["Delay"].sum())
        on_time = total - delayed
        delay_rate = delayed / total

        if total != 539_379 or delayed != 240_263:
                raise ValueError(
                        f"Los datos no coinciden con la versión validada: {total=} {delayed=}"
                )

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output = OUTPUT_DIR / "strategic_overview.html"
        output.write_text(
                render_strategic_html(
                        total=total, delayed=delayed, on_time=on_time, delay_rate=delay_rate
                ),
                encoding="utf-8",
        )
        print(f"Generado: {output}")


if __name__ == "__main__":
        generate()