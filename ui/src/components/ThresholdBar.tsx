import './ThresholdBar.css'

interface ThresholdBarProps {
  probability: number
  /** Umbral de refuerzo vigente, tal como lo reporta la API. */
  threshold: number
  /** Corte de la banda alta. */
  highBandThreshold: number
}

function porcentaje(valor: number): string {
  return `${(valor * 100).toFixed(1)}%`
}

/**
 * Ubica la probabilidad frente a los dos cortes del punto de operacion.
 *
 * Los cortes no son redondos a proposito: salen del presupuesto de refuerzo del
 * 20% del itinerario, no de una division arbitraria en tercios. Por eso se leen
 * de la API en vez de quedar escritos aqui: si el modelo se recalibra y el
 * umbral cambia, la interfaz lo refleja sin tocar codigo.
 */
function ThresholdBar({ probability, threshold, highBandThreshold }: ThresholdBarProps) {
  const clamp = (valor: number) => Math.min(100, Math.max(0, valor * 100))

  const anchoBajo = clamp(threshold)
  const anchoMedio = clamp(highBandThreshold) - anchoBajo
  const anchoAlto = 100 - clamp(highBandThreshold)

  return (
    <div className="threshold-bar">
      <div className="threshold-bar-track">
        <div className="threshold-segment threshold-low" style={{ width: `${anchoBajo}%` }} />
        <div className="threshold-segment threshold-medium" style={{ width: `${anchoMedio}%` }} />
        <div className="threshold-segment threshold-high" style={{ width: `${anchoAlto}%` }} />
        <div className="threshold-marker" style={{ left: `${clamp(probability)}%` }} />
      </div>
      <div className="threshold-legend">
        <span>Bajo (&lt;{porcentaje(threshold)})</span>
        <span>
          Medio ({porcentaje(threshold)}–{porcentaje(highBandThreshold)})
        </span>
        <span>Alto (&gt;{porcentaje(highBandThreshold)})</span>
      </div>
    </div>
  )
}

export default ThresholdBar
