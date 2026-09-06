# Suite analítica de dashboards

El tablero principal está implementado en `dashboard/app.py`. Las vistas descriptivas se generan
como HTML independientes y forman una sola suite analítica:

- Dashboard 1: nivel estratégico.
- Dashboard 2: nivel táctico.
- Dashboard 3: nivel de priorización.

El flujo ejecutivo, los objetivos, las preguntas de negocio y los límites de interpretación de
las tres vistas están documentados en
[`docs/business_questions_descriptive.md`](docs/business_questions_descriptive.md).

`mockup_tablero_prediccion_retrasos.html` se conserva únicamente como referencia histórica de la
maqueta inicial. No forma parte de la suite descriptiva publicada ni representa su interfaz actual.

## Generación de vistas

Los generadores están en `dashboard/descriptive/` y los resultados se escriben en
`dashboard/descriptive/output/`.

Desde la raíz del repositorio:

```bash
dvc pull
python -m pip install -r dashboard/requirements.txt
python dashboard/descriptive/generate_all.py
```

La gráfica del HTML usa Plotly desde CDN y requiere conexión a internet para dibujarse.

Para visualizar la suite mediante localhost, el servidor debe iniciarse desde la raíz del
repositorio. No debe iniciarse dentro de `dashboard/descriptive/output`, porque esa raíz no puede
servir la hoja maestra ubicada en el directorio padre.

```bash
python -m http.server 8765
```

Las vistas quedan disponibles en:

- `http://localhost:8765/dashboard/descriptive/output/strategic_overview.html`
- `http://localhost:8765/dashboard/descriptive/output/tactical_diagnosis.html`
- `http://localhost:8765/dashboard/descriptive/output/operational_prioritization.html`

## Visualización en GitHub

La vista normal de archivos de GitHub (`github.com/.../blob/...`) muestra el código fuente de un
HTML y no ejecuta sus estilos ni scripts. La suite se publica como sitio mediante GitHub Pages:

- [Dashboard 1 · Estratégico](https://santiagomelomedina.github.io/microproyecto-grupo4-pds-maia/dashboard/descriptive/output/strategic_overview.html)
- [Dashboard 2 · Táctico](https://santiagomelomedina.github.io/microproyecto-grupo4-pds-maia/dashboard/descriptive/output/tactical_diagnosis.html)
- [Dashboard 3 · Priorización](https://santiagomelomedina.github.io/microproyecto-grupo4-pds-maia/dashboard/descriptive/output/operational_prioritization.html)

El workflow `.github/workflows/dashboard-pages.yml` publica únicamente los tres HTML y la hoja
maestra. Se ejecuta al actualizar estos archivos en `main` o manualmente desde **Actions**. En la
configuración del repositorio, **Settings → Pages → Source** debe estar establecido en
**GitHub Actions**.

## Sistema visual compartido

`dashboard/descriptive/dashboard-design-system.css` es la única fuente de estilos de la suite.
Contiene paleta, tipografía, espaciado, tarjetas, KPIs, paneles de gráficos, hallazgos, síntesis,
conclusiones y reglas responsive. Los tokens equivalentes para Plotly y los componentes HTML
compartidos están centralizados en `dashboard/descriptive/common.py`.

Todo dashboard nuevo debe:

1. Referenciar `dashboard-design-system.css`, sin CSS embebido ni hojas particulares.
2. Usar `dashboard-suite` en el contenedor raíz.
3. Reutilizar los componentes documentados en `dashboard/docs/design_system.md`.
4. Aplicar `common.apply_figure_style` y los tokens de `common.py` a todas las figuras Plotly.

Los HTML generados enlazan la misma hoja mediante `../dashboard-design-system.css`; por ello deben
conservar esa ruta relativa cuando se distribuyan junto con el directorio descriptivo.
