# Reporte de trabajo en equipo — Entrega Final

**Micro-proyecto · Proyecto de Desarrollo de Soluciones · MAIA · Grupo 4**

## Distribución de actividades

| Actividad | Responsable | Evidencia en el repositorio |
|---|---|---|
| Empaquetamiento del modelo como wheel instalable | Katherin Rodríguez Sánchez | `model-pkg/`, `api/model-package/*.whl` |
| Entrenamiento reproducible y pruebas del paquete | Katherin Rodríguez Sánchez | `model-pkg/train_pipeline.py`, `model-pkg/tests/`, `model-pkg/tox.ini` |
| API de inferencia con FastAPI | Edisson David Prieto | `api/app/`, `docs/api_endpoints.md` |
| Integración de la API con el modelo empaquetado y automatización con tox | Katherin Rodríguez Sánchez | `api/app/services/artifacts.py`, `api/tox.ini` |
| Modelo LightGBM y su experimentación en MLflow | Edisson David Prieto | `models/train_lgbm.py`, `models/scenarios.lgbm.training.yaml` |
| Tablero React: estructura, navegación y componentes | Santiago Melo Medina | `ui/src/components/`, `ui/src/pages/DashboardPage.tsx` |
| Tableros descriptivos y preguntas de negocio asociadas | María del Pilar Munoz | `dashboard/descriptive/`, `dashboard/docs/` |
| Conexión del tablero con la API y vista de franjas a reforzar | Katherin Rodríguez Sánchez | `ui/src/services/`, `ui/src/pages/RankingPage.tsx` |
| Contenerización de la API | Edisson David Prieto · Katherin Rodríguez Sánchez | `api/Dockerfile` |
| Contenerización del tablero y orquestación con Compose | Katherin Rodríguez Sánchez | `ui/Dockerfile`, `ui/nginx.conf`, `docker-compose.yml` |
| Generación reproducible del histórico del tablero | Katherin Rodríguez Sánchez | `scripts/generar_datos_tablero.py` |
| Manuales de usuario e instalación | Katherin Rodríguez Sánchez | `docs/3rd_delivery/manual_usuario.md`, `manual_instalacion.md` |
| Redacción del reporte final | Todo el equipo | `docs/3rd_delivery/reporte_entrega3.md` |
| Revisión de *pull requests* | Todo el equipo | Historial de PR del repositorio |

La contribución individual es verificable en `Insights → Contributors` y en el historial de commits.

## Organización del trabajo

El equipo mantiene una rama por integrante e integra a `main` mediante *pull request* con revisión de
al menos un compañero. Durante esta entrega se integraron los PR #6 (LightGBM), #9 y #10 (tablero
React y tableros descriptivos) y #11 (API), y la rama `k-entrega3` consolidó todas las piezas en el
prototipo desplegable.

La revisión entre pares tuvo efecto sustantivo y no solo formal. En la revisión del PR de LightGBM se
verificó, ejecutando su código sobre los datos, que la partición temporal coincidiera exactamente con
la del notebook de modelado —mismo bloque de prueba de 107.464 vuelos— lo que permitió comparar su
ROC-AUC con el de las otras familias de forma legítima. Esa verificación es la que sustenta la
conclusión de que cuatro familias independientes convergen al mismo techo.

## Defectos detectados al integrar

Tres problemas solo se hicieron visibles al armar el sistema de extremo a extremo, y quedaron
documentados con pruebas de regresión:

- El tablero devolvía predicciones simuladas —un hash del nombre de la aerolínea— en lugar de
  consultar el modelo.
- Los artefactos del modelo y el histórico no estaban versionados, de modo que un clon limpio no
  podía construir la imagen de la API.
- La configuración de CORS rechazaba el propio origen del tablero, porque pydantic normaliza las URL
  agregando una barra final que el navegador no envía. El síntoma era engañoso: la API respondía bien
  por `curl` y solo fallaba desde el navegador.

## Lecciones

La integración temprana habría revelado antes los tres defectos anteriores: cada pieza funcionaba de
forma aislada y las fallas estaban en los contratos entre ellas. Para una siguiente iteración, el
equipo definiría el contrato de la API antes de construir el tablero, en lugar de después.
