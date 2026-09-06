# Estándar de diseño de la suite analítica

## Alcance

Dashboard 1, Dashboard 2, Dashboard 3 y toda vista futura forman una sola suite. El nivel
analítico cambia; el sistema visual, la estructura de lectura y los componentes permanecen.

## Fuentes únicas

- `dashboard/descriptive/dashboard-design-system.css`: única hoja de estilos.
- `dashboard/descriptive/common.py`: paleta de Plotly, benchmark, tipografía y componentes HTML.

No se permite CSS embebido, hojas por dashboard, colores hexadecimales locales ni familias
tipográficas definidas dentro de un generador.

## Estructura

1. Encabezado limpio con título principal y una descripción breve mediante `page-intro`; no incluye
	etiqueta de nivel, mensaje central ni conclusiones anticipadas.
2. Resumen del nivel con la cuadrícula `metrics` y tarjetas `metric`.
3. Desarrollo con `dashboard-section`, `section-heading` y visualizaciones en `panel chart-panel`.
4. Síntesis locales con `module-synthesis` cuando una visualización requiera una lectura breve.
5. Nota metodológica con `methodology` solo cuando sea necesaria y antes del cierre ejecutivo.
6. Hallazgos con `panel findings-panel`.
7. Espacio vertical amplio para separar la evidencia del cierre.
8. Un único mensaje con `executive-takeaway`; siempre es el último bloque narrativo.

La secuencia de lectura obligatoria es datos → evidencia → hallazgos → mensaje ejecutivo. El cierre
es una sola frase sin título, fondo, caja ni borde exterior; la barra vertical amarilla es su único
elemento de énfasis.

El elemento raíz siempre usa la clase `dashboard-suite`. Una cuadrícula de cuatro KPIs agrega
`metrics--four`; no redefine el componente.

## Nomenclatura

| Nivel | Hallazgos |
| --- | --- |
| Estratégico | Hallazgos estratégicos |
| Táctico | Hallazgos tácticos |
| Priorización | Hallazgos de priorización |

No se sustituyen estos nombres por variantes como “Insights clave”, “Hallazgos principales”,
“Conclusiones” o “Cómo interpretar resultados”. El mensaje final no lleva encabezado.

## Visualizaciones

Toda figura Plotly debe usar `common.apply_figure_style`. Los colores, la fuente, los fondos, la
cuadrícula y el benchmark se importan desde `common.py`; un generador solo define codificaciones
visuales propias de su análisis.

## Extensión

Un dashboard futuro debe enlazar `../dashboard-design-system.css` desde `output/`, usar
`dashboard-suite`, componer únicamente las clases existentes y reutilizar los tokens de
`common.py`. Si una nueva vista necesita una estructura no cubierta, primero se evalúa como
componente general de la suite; nunca se crea una variante local por dashboard.
