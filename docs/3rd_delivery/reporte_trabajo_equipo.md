# Reporte de trabajo en equipo — Entrega Final

**Micro-proyecto · Proyecto de Desarrollo de Soluciones · MAIA · Grupo 4**

## Distribución de actividades

| Actividad | Responsable | Evidencia en el repositorio |
|---|---|---|
| Empaquetamiento del modelo como wheel instalable | Katherin Rodríguez Sánchez | `model-pkg/`, `api/model-package/*.whl` |
| Entrenamiento reproducible y pruebas del paquete | Katherin Rodríguez Sánchez | `model-pkg/train_pipeline.py`, `model-pkg/tests/`, `model-pkg/tox.ini` |
| API de inferencia con FastAPI | Edisson David Prieto | `api/app/`, `docs/api_endpoints.md` |
| Integración de la API con el modelo empaquetado y automatización con tox | Katherin Rodríguez Sánchez | `api/app/services/artifacts.py`, `api/tox.ini` |
| Evaluación experimental de LightGBM en MLflow (no incorporada al modelo final) | Edisson David Prieto | `models/train_lgbm.py`, `models/scenarios.lgbm.training.yaml` |
| Tablero React: estructura, navegación y componentes | Santiago Melo Medina | `ui/src/components/`, `ui/src/pages/DashboardPage.tsx` |
| Tableros descriptivos y preguntas de negocio asociadas | María del Pilar Munoz | `dashboard/descriptive/`, `dashboard/docs/`, PR #9 |
| Conexión del tablero con la API y vista de franjas a reforzar | Katherin Rodríguez Sánchez | `ui/src/services/`, `ui/src/pages/RankingPage.tsx` |
| Contenerización de la API | Edisson David Prieto · Katherin Rodríguez Sánchez | `api/Dockerfile` |
| Contenerización del tablero y orquestación con Compose | Katherin Rodríguez Sánchez | `ui/Dockerfile`, `ui/nginx.conf`, `docker-compose.yml` |
| Infraestructura como código y despliegue en AWS con ECR, ECS sobre EC2, IP elástica, CloudWatch y estado remoto S3 | Santiago Melo Medina | `infra/`, `infra/scripts/build_and_push.sh`, PR #13 |
| Generación reproducible del histórico del tablero | Katherin Rodríguez Sánchez | `scripts/generar_datos_tablero.py` |
| Redacción inicial de los manuales y del reporte final | Katherin Rodríguez Sánchez | `docs/3rd_delivery/manual_usuario.md`, `docs/3rd_delivery/manual_instalacion.md`, `docs/3rd_delivery/reporte_entrega3.md`, PR #12 |
| Reproducción del despliegue, revisión técnica del PR #13, actualización de manuales y reportes, y preparación de evidencias | María del Pilar Munoz | `docs/3rd_delivery/`, PR #14 |
| Insumos técnicos y revisión del reporte final | Todo el equipo | Historial de commits y revisiones de PR |
| Revisión de *pull requests* | Todo el equipo | Historial de PR del repositorio |

La contribución individual es verificable en `Insights → Contributors` y en el historial de commits.

## Organización del trabajo

El equipo mantiene una rama por integrante e integra a `main` mediante *pull
request* con revisión de al menos un compañero. Durante esta entrega se
integraron los PR #6 (LightGBM), #9 y #10 (tablero React y tableros
descriptivos), #11 (API), #12 (consolidación del prototipo, reportes y manuales)
y #13 (infraestructura como código y despliegue en AWS). El PR #14 reúne la
revisión documental final y las evidencias verificadas por Pilar.

La revisión entre pares tuvo efecto sustantivo y no solo formal. En la revisión del PR de LightGBM se
verificó, ejecutando su código sobre los datos, que la partición temporal coincidiera exactamente con
la del notebook de modelado —mismo bloque de prueba de 107.464 vuelos— lo que permitió comparar su
ROC-AUC con el de las otras familias de forma legítima. El resultado se conservó como evidencia
experimental, pero LightGBM no se seleccionó ni se incorporó al paquete, la API o el despliegue: la
solución final utiliza XGBoost.

La revisión del PR #13 incluyó la comprobación del despliegue público, la salud
de la API, la navegación del tablero, el ranking de franjas y una predicción
individual. A partir de esa reproducción se corrigieron los manuales, se
incorporaron capturas de las vistas descriptivas y operativas, y se documentó
el flujo real de Terraform, ECR y ECS junto con sus limitaciones académicas.

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
