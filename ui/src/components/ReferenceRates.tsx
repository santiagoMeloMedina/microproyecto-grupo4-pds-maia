import type { ReferenceRate } from '../types/prediction'
import './ReferenceRates.css'

interface ReferenceRatesProps {
  references: ReferenceRate[]
  /** Probabilidad estimada para el itinerario consultado. */
  probability: number
}

/**
 * Contrasta la prediccion contra las tasas historicas de su aerolinea, su ruta,
 * su franja y la media global.
 *
 * Reemplaza al grafico de "influencia de cada variable" del prototipo: aquel
 * repartia porcentajes entre los campos del formulario, pero un modelo de
 * arboles con interacciones no atribuye su salida a variables sueltas de esa
 * forma, asi que la cifra no significaba nada. Estas referencias si salen del
 * historico y permiten juzgar si el riesgo estimado es alto o bajo respecto de
 * lo que suele ocurrir.
 */
function ReferenceRates({ references, probability }: ReferenceRatesProps) {
  const valores = [...references.map((r) => r.rate), probability]
  const maximo = Math.max(...valores, 0.01)

  const filas = [
    { label: 'Este itinerario', rate: probability, destacada: true },
    ...references.map((r) => ({ ...r, destacada: false })),
  ]

  return (
    <ul className="reference-rates">
      {filas.map((fila) => (
        <li
          key={fila.label}
          className={fila.destacada ? 'reference-row reference-row-current' : 'reference-row'}
        >
          <span className="reference-label">{fila.label}</span>
          <span className="reference-track">
            <span className="reference-bar" style={{ width: `${(fila.rate / maximo) * 100}%` }} />
          </span>
          <span className="reference-value">{(fila.rate * 100).toFixed(1)}%</span>
        </li>
      ))}
    </ul>
  )
}

export default ReferenceRates
