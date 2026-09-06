import { useState } from 'react'
import type { FormEvent } from 'react'
import airlines from '../data/prediction/airlines.json'
import airports from '../data/prediction/airports.json'
import daysOfWeek from '../data/prediction/days-of-week.json'
import type { PredictionInput } from '../types/prediction'
import Tooltip from './Tooltip'
import './PredictionForm.css'

interface PredictionFormProps {
  onSubmit: (input: PredictionInput) => void
  submitting: boolean
}

function PredictionForm({ onSubmit, submitting }: PredictionFormProps) {
  const [airline, setAirline] = useState(airlines[0])
  const [airportFrom, setAirportFrom] = useState(airports[0])
  const [airportTo, setAirportTo] = useState(airports[1])
  const [dayOfWeek, setDayOfWeek] = useState(daysOfWeek[0].value)
  const [time, setTime] = useState(480)
  const [length, setLength] = useState(120)

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
          {airlines.map((code) => (
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
          {airports.map((code) => (
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
        <select id="airportTo" value={airportTo} onChange={(e) => setAirportTo(e.target.value)}>
          {airports.map((code) => (
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
          {daysOfWeek.map((day) => (
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
