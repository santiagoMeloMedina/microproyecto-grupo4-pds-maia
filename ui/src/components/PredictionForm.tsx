import { useState } from 'react'
import type { FormEvent } from 'react'
import airlines from '../data/prediction/airlines.json'
import airports from '../data/prediction/airports.json'
import daysOfWeek from '../data/prediction/days-of-week.json'
import type { PredictionInput } from '../types/prediction'
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
        <label htmlFor="airline">Aerolínea</label>
        <select id="airline" value={airline} onChange={(e) => setAirline(e.target.value)}>
          {airlines.map((code) => (
            <option key={code} value={code}>
              {code}
            </option>
          ))}
        </select>
      </div>

      <div className="prediction-field">
        <label htmlFor="airportFrom">Aeropuerto de origen</label>
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
        <label htmlFor="airportTo">Aeropuerto de destino</label>
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
        <label htmlFor="dayOfWeek">Día de la semana</label>
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
        <label htmlFor="time">Hora programada (minutos desde medianoche)</label>
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
        <label htmlFor="length">Duración del vuelo (minutos)</label>
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
