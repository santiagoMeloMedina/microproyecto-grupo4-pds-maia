import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import airlinesFallback from '../data/prediction/airlines.json'
import airportsFallback from '../data/prediction/airports.json'
import daysFallback from '../data/prediction/days-of-week.json'
import { fetchCatalog } from '../services/predictionService'
import type { Catalog, PredictionInput } from '../types/prediction'
import Tooltip from './Tooltip'
import './PredictionForm.css'

interface PredictionFormProps {
  onSubmit: (input: PredictionInput) => void
  submitting: boolean
}

/**
 * Catalogo de respaldo.
 *
 * Si la API no responde, el formulario sigue siendo utilizable con los codigos
 * que venian en el prototipo. Se reemplaza por el catalogo real en cuanto la
 * API contesta, que es el que refleja el historico efectivamente cargado.
 */
const CATALOGO_RESPALDO: Catalog = {
  airlines: airlinesFallback,
  airports: airportsFallback,
  routes: [],
  days: daysFallback,
}

function comoHora(minutos: number): string {
  const h = Math.floor(minutos / 60) % 24
  const m = minutos % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

function PredictionForm({ onSubmit, submitting }: PredictionFormProps) {
  const [catalog, setCatalog] = useState<Catalog>(CATALOGO_RESPALDO)
  const [airline, setAirline] = useState(CATALOGO_RESPALDO.airlines[0])
  const [airportFrom, setAirportFrom] = useState(CATALOGO_RESPALDO.airports[0])
  const [airportTo, setAirportTo] = useState(CATALOGO_RESPALDO.airports[1])
  const [dayOfWeek, setDayOfWeek] = useState(CATALOGO_RESPALDO.days[0].value)
  const [time, setTime] = useState(480)
  const [length, setLength] = useState(120)

  useEffect(() => {
    let vigente = true

    fetchCatalog()
      .then((real) => {
        if (!vigente || real.airlines.length === 0) return
        setCatalog(real)
        setAirline((actual) => (real.airlines.includes(actual) ? actual : real.airlines[0]))
        setAirportFrom((actual) =>
          real.airports.includes(actual) ? actual : real.airports[0],
        )
        setAirportTo((actual) => (real.airports.includes(actual) ? actual : real.airports[1]))
      })
      .catch(() => {
        // Se conserva el catalogo de respaldo; el error de conexion se reporta
        // al enviar el formulario, que es cuando afecta al usuario.
      })

    return () => {
      vigente = false
    }
  }, [])

  const sameAirport = airportFrom === airportTo

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (sameAirport) return
    onSubmit({ airline, airportFrom, airportTo, dayOfWeek, time, length })
  }

  return (
    <form className="prediction-form" onSubmit={handleSubmit}>
      <div className="prediction-field">
        <span className="prediction-field-label">
          <label htmlFor="airline">Aerolínea</label>
          <Tooltip label="Acerca de Aerolínea" text="Código IATA de la aerolínea que opera el vuelo." />
        </span>
        <select id="airline" value={airline} onChange={(e) => setAirline(e.target.value)}>
          {catalog.airlines.map((code) => (
            <option key={code} value={code}>
              {code}
            </option>
          ))}
        </select>
      </div>

      <div className="prediction-field">
        <span className="prediction-field-label">
          <label htmlFor="airportFrom">Origen</label>
          <Tooltip label="Acerca de Origen" text="Código IATA del aeropuerto de salida." />
        </span>
        <select
          id="airportFrom"
          value={airportFrom}
          onChange={(e) => setAirportFrom(e.target.value)}
        >
          {catalog.airports.map((code) => (
            <option key={code} value={code}>
              {code}
            </option>
          ))}
        </select>
      </div>

      <div className="prediction-field">
        <span className="prediction-field-label">
          <label htmlFor="airportTo">Destino</label>
          <Tooltip label="Acerca de Destino" text="Código IATA del aeropuerto de llegada." />
        </span>
        <select
          id="airportTo"
          value={airportTo}
          onChange={(e) => setAirportTo(e.target.value)}
        >
          {catalog.airports.map((code) => (
            <option key={code} value={code}>
              {code}
            </option>
          ))}
        </select>
        {sameAirport && (
          <p className="prediction-field-error">
            El origen y el destino no pueden ser el mismo aeropuerto.
          </p>
        )}
      </div>

      <div className="prediction-field">
        <span className="prediction-field-label">
          <label htmlFor="dayOfWeek">Día</label>
          <Tooltip label="Acerca de Día" text="Día de la semana programado para el vuelo." />
        </span>
        <select
          id="dayOfWeek"
          value={dayOfWeek}
          onChange={(e) => setDayOfWeek(Number(e.target.value))}
        >
          {catalog.days.map((day) => (
            <option key={day.value} value={day.value}>
              {day.label}
            </option>
          ))}
        </select>
      </div>

      <div className="prediction-field">
        <span className="prediction-field-label">
          <label htmlFor="time">Hora</label>
          <Tooltip
            label="Acerca de Hora"
            text="Hora de salida programada, en minutos desde medianoche (0-1439)."
          />
        </span>
        <input
          id="time"
          type="number"
          min={0}
          max={1439}
          value={time}
          onChange={(e) => setTime(Number(e.target.value))}
        />
        <p className="prediction-field-hint">Equivale a las {comoHora(time)}.</p>
      </div>

      <div className="prediction-field">
        <span className="prediction-field-label">
          <label htmlFor="length">Duración</label>
          <Tooltip label="Acerca de Duración" text="Duración estimada del vuelo, en minutos." />
        </span>
        <input
          id="length"
          type="number"
          min={1}
          value={length}
          onChange={(e) => setLength(Number(e.target.value))}
        />
      </div>

      <button type="submit" className="prediction-submit" disabled={sameAirport || submitting}>
        {submitting ? 'Calculando...' : 'Calcular riesgo de retraso'}
      </button>
    </form>
  )
}

export default PredictionForm
