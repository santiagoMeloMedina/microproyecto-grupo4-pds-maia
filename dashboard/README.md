# Dashboard

El tablero principal está implementado en `dashboard/app.py`. La vista descriptiva estratégica se
mantiene separada para evitar modificar el flujo actual mientras se integra el trabajo del equipo.

## Vista estratégica descriptiva

El generador está en `dashboard/descriptive/strategic_overview.py` y el resultado listo para abrir
en un navegador está en `dashboard/descriptive/output/strategic_overview.html`.

Desde la raíz del repositorio:

```bash
dvc pull
python -m pip install -r dashboard/requirements.txt
python dashboard/descriptive/strategic_overview.py
```

La gráfica del HTML usa Plotly desde CDN y requiere conexión a internet para dibujarse.

## Estilos compartidos

`dashboard/descriptive/strategic_overview.css` contiene la paleta y los estilos reutilizables de la
vista estratégica. Todos los selectores están encapsulados bajo la clase `strategic-dashboard`, por
lo que no alteran el tablero principal al importarlos.

Para reutilizarlos en una vista de Dash:

1. Cargar la hoja explícitamente o copiarla a `dashboard/assets/` cuando el equipo decida aplicarla
   globalmente.
2. Asignar `className="strategic-dashboard"` al contenedor raíz de la vista.
3. Reutilizar clases como `hero`, `metrics`, `metric`, `analysis-grid`, `panel`, `insights` y
   `benchmark` en los componentes correspondientes.

El generador estratégico lee la misma hoja y la incrusta en el HTML exportado. De este modo, el
archivo HTML continúa siendo autónomo y la fuente de estilos se mantiene en un solo lugar.
