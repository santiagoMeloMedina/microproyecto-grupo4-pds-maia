import { useState } from 'react'
import PredictionForm from '../components/PredictionForm'
import RiskGauge from '../components/RiskGauge'
import ThresholdBar from '../components/ThresholdBar'
import FactorImpactChart from '../components/FactorImpactChart'
import { predictDelay } from '../services/predictionService'
import type { PredictionInput, PredictionResult } from '../types/prediction'
import './PredictionPage.css'

function PredictionPage() {
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(input: PredictionInput) {
    setSubmitting(true)
    try {
      const prediction = await predictDelay(input)
      setResult(prediction)
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
          estimada y qué aspectos del itinerario influyen más en ese resultado.
        </p>
      </header>

      <div className="prediction-layout">
        {submitting && (
          <section className="prediction-panel prediction-loading">
            <h2>Resultado</h2>
            <div className="loading-spinner" role="status" aria-label="Calculando predicción" />
            <p className="prediction-empty">Calculando predicción...</p>
          </section>
        )}

        {!submitting && result && (
          <section className="prediction-panel prediction-results">
            <h2>Resultado</h2>

            {result.notes.map((note) => (
              <p className="prediction-disclaimer" key={note}>
                {note}
              </p>
            ))}

            <div className="prediction-result-top">
              <RiskGauge probability={result.probability} riskLevel={result.riskLevel} />
              <div className="prediction-result-threshold">
                <h3>Umbral de riesgo</h3>
                <ThresholdBar probability={result.probability} />
              </div>
            </div>

            <div className="prediction-result-factors">
              <h3>Aspectos con mayor influencia en este resultado</h3>
              <FactorImpactChart factors={result.factors} />
            </div>
          </section>
        )}

        <section className="prediction-panel">
          <h2>Itinerario</h2>
          <PredictionForm onSubmit={handleSubmit} submitting={submitting} />
        </section>
      </div>
    </main>
  )
}

export default PredictionPage
