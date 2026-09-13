import { useState } from 'react'
import PredictionForm from '../components/PredictionForm'
import RiskGauge from '../components/RiskGauge'
import ThresholdBar from '../components/ThresholdBar'
import ReferenceRates from '../components/ReferenceRates'
import { predictDelay } from '../services/predictionService'
import { ApiError } from '../services/api'
import type { PredictionInput, PredictionResult } from '../types/prediction'
import './PredictionPage.css'

const ACCION: Record<string, string> = {
  bajo: 'Sin refuerzo. El itinerario queda por debajo del umbral de priorización.',
  medio: 'Refuerzo recomendado. Supera el umbral del presupuesto de refuerzo del 20%.',
  alto: 'Refuerzo prioritario. Está en la banda de mayor riesgo estimado.',
}

function PredictionPage() {
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(input: PredictionInput) {
    setSubmitting(true)
    setError(null)
    try {
      setResult(await predictDelay(input))
    } catch (err) {
      setResult(null)
      setError(
        err instanceof ApiError ? err.message : 'Ocurrió un error inesperado al predecir.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="prediction-page">
      <header className="prediction-page-header">
        <h1>Predicción de riesgo de retraso</h1>
        <p>
          Ingresa el itinerario programado para consultar la probabilidad de retraso
          estimada por el modelo y contrastarla con el histórico de su aerolínea, su
          ruta y su franja horaria.
        </p>
      </header>

      <div className="prediction-layout">
        <section className="prediction-panel">
          <h2>Itinerario</h2>
          <PredictionForm onSubmit={handleSubmit} submitting={submitting} />
        </section>

        <section className="prediction-panel prediction-results">
          <h2>Resultado</h2>

          {!result && !submitting && !error && (
            <p className="prediction-empty">
              Completa el itinerario y calcula el riesgo para ver el resultado aquí.
            </p>
          )}

          {submitting && <p className="prediction-empty">Consultando el modelo...</p>}

          {error && !submitting && <p className="prediction-error">{error}</p>}

          {result && !submitting && (
            <>
              <div className="prediction-result-top">
                <RiskGauge probability={result.probability} riskLevel={result.band} />
                <div className="prediction-result-threshold">
                  <h3>Punto de operación</h3>
                  <ThresholdBar
                    probability={result.probability}
                    threshold={result.threshold}
                    highBandThreshold={result.highBandThreshold}
                  />
                  <p className="prediction-action">{ACCION[result.band]}</p>
                </div>
              </div>

              <div className="prediction-result-factors">
                <h3>Comparación con el histórico</h3>
                <ReferenceRates
                  references={result.references}
                  probability={result.probability}
                />
              </div>

              <p className="prediction-disclaimer">
                Estimado con el modelo <code>model_riesgo_retraso</code> v
                {result.modelVersion}, XGBoost entrenado sobre los días 0–24 del
                histórico. La probabilidad es de retraso del vuelo, no una predicción
                de su duración.
              </p>
            </>
          )}
        </section>
      </div>
    </main>
  )
}

export default PredictionPage
