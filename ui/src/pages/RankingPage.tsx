import { useEffect, useMemo, useState } from 'react'
import {
  fetchCatalog,
  fetchScheduleSlots,
  fetchSlotsSummary,
} from '../services/predictionService'
import { ApiError } from '../services/api'
import type { Catalog } from '../types/prediction'
import type { ScheduleSlot, SlotFilters, SlotsSummary } from '../types/slots'
import './RankingPage.css'

const FRANJAS = ['00-06', '06-12', '12-18', '18-24']
const TODOS = ''

function porcentaje(valor: number | null | undefined, decimales = 1): string {
  if (valor === null || valor === undefined) return '—'
  return `${(valor * 100).toFixed(decimales)}%`
}

function comoHora(minutos: number): string {
  const h = Math.floor(minutos / 60) % 24
  const m = minutos % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

/**
 * Ranking de franjas de itinerario por riesgo estimado.
 *
 * Es la respuesta directa a la pregunta de negocio: que franjas conviene
 * reforzar la proxima semana. El orden lo da el modelo y no la tasa observada,
 * porque cada franja tiene pocos vuelos en el periodo y su tasa cruda es ruido.
 */
function RankingPage() {
  const [catalog, setCatalog] = useState<Catalog | null>(null)
  const [filters, setFilters] = useState<SlotFilters>({})
  const [slots, setSlots] = useState<ScheduleSlot[]>([])
  const [summary, setSummary] = useState<SlotsSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchCatalog().then(setCatalog).catch(() => setCatalog(null))
  }, [])

  useEffect(() => {
    let vigente = true
    setLoading(true)
    setError(null)

    Promise.all([fetchScheduleSlots(filters, 25), fetchSlotsSummary(filters)])
      .then(([franjas, resumen]) => {
        if (!vigente) return
        setSlots(franjas)
        setSummary(resumen)
      })
      .catch((err) => {
        if (!vigente) return
        setSlots([])
        setSummary(null)
        setError(
          err instanceof ApiError ? err.message : 'No se pudieron cargar las franjas.',
        )
      })
      .finally(() => {
        if (vigente) setLoading(false)
      })

    return () => {
      vigente = false
    }
  }, [filters])

  const actualizar = (campo: keyof SlotFilters, valor: string) =>
    setFilters((previos) => {
      const siguientes = { ...previos }
      if (valor === TODOS) {
        delete siguientes[campo]
      } else if (campo === 'dayOfWeek') {
        siguientes.dayOfWeek = Number(valor)
      } else {
        siguientes[campo] = valor as never
      }
      return siguientes
    })

  const hayFiltros = useMemo(() => Object.keys(filters).length > 0, [filters])

  return (
    <main className="ranking-page">
      <header className="ranking-header">
        <h1>Franjas de itinerario a reforzar</h1>
        <p>
          Franjas ordenadas por el riesgo de retraso que estima el modelo, de mayor a
          menor. El orden lo da el modelo y no la tasa observada: cada franja tiene
          pocos vuelos en el período y su tasa cruda sería ruido.
        </p>
      </header>

      <section className="ranking-filters" aria-label="Filtros">
        <label>
          <span>Aerolínea</span>
          <select
            value={filters.airline ?? TODOS}
            onChange={(e) => actualizar('airline', e.target.value)}
          >
            <option value={TODOS}>Todas</option>
            {catalog?.airlines.map((code) => (
              <option key={code} value={code}>
                {code}
              </option>
            ))}
          </select>
        </label>

        <label>
          <span>Ruta</span>
          <select
            value={filters.route ?? TODOS}
            onChange={(e) => actualizar('route', e.target.value)}
          >
            <option value={TODOS}>Todas</option>
            {catalog?.routes.map((route) => (
              <option key={route} value={route}>
                {route}
              </option>
            ))}
          </select>
        </label>

        <label>
          <span>Día</span>
          <select
            value={filters.dayOfWeek ?? TODOS}
            onChange={(e) => actualizar('dayOfWeek', e.target.value)}
          >
            <option value={TODOS}>Todos</option>
            {catalog?.days.map((day) => (
              <option key={day.value} value={day.value}>
                {day.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          <span>Franja</span>
          <select
            value={filters.slot ?? TODOS}
            onChange={(e) => actualizar('slot', e.target.value)}
          >
            <option value={TODOS}>Todas</option>
            {FRANJAS.map((franja) => (
              <option key={franja} value={franja}>
                {franja}
              </option>
            ))}
          </select>
        </label>

        {hayFiltros && (
          <button type="button" className="ranking-clear" onClick={() => setFilters({})}>
            Limpiar filtros
          </button>
        )}
      </section>

      {summary && (
        <section className="ranking-kpis" aria-label="Indicadores de la selección">
          <article>
            <span className="kpi-value">{porcentaje(summary.delayRate)}</span>
            <span className="kpi-label">Tasa de retraso en la selección</span>
          </article>
          <article>
            <span className="kpi-value">{summary.flightsInSelection.toLocaleString('es-CO')}</span>
            <span className="kpi-label">
              Vuelos de {summary.totalFlights.toLocaleString('es-CO')}
            </span>
          </article>
          <article>
            <span className="kpi-value">{summary.slotsInSelection.toLocaleString('es-CO')}</span>
            <span className="kpi-label">Franjas en la selección</span>
          </article>
          <article>
            <span className="kpi-value">
              {summary.slotsOverThreshold.toLocaleString('es-CO')}
            </span>
            <span className="kpi-label">
              Sobre el umbral de {porcentaje(summary.threshold)}
            </span>
          </article>
        </section>
      )}

      {error && <p className="ranking-error">{error}</p>}
      {loading && !error && <p className="ranking-empty">Consultando el modelo...</p>}
      {!loading && !error && slots.length === 0 && (
        <p className="ranking-empty">
          Ninguna franja coincide con los filtros seleccionados.
        </p>
      )}

      {!loading && slots.length > 0 && (
        <div className="ranking-table-wrapper">
          <table className="ranking-table">
            <thead>
              <tr>
                <th scope="col">#</th>
                <th scope="col">Aerolínea</th>
                <th scope="col">Ruta</th>
                <th scope="col">Día</th>
                <th scope="col">Franja</th>
                <th scope="col">Salida</th>
                <th scope="col" className="num">Riesgo</th>
                <th scope="col">Banda</th>
                <th scope="col" className="num">Tasa observada</th>
                <th scope="col" className="num">Vuelos</th>
              </tr>
            </thead>
            <tbody>
              {slots.map((slot, indice) => (
                <tr key={`${slot.airline}-${slot.route}-${slot.dayOfWeek}-${slot.slot}`}>
                  <td>{indice + 1}</td>
                  <td>{slot.airline}</td>
                  <td>{slot.route}</td>
                  <td>{slot.dayLabel}</td>
                  <td>{slot.slot}</td>
                  <td>{comoHora(slot.time)}</td>
                  <td className="num strong">{porcentaje(slot.risk)}</td>
                  <td>
                    <span className={`ranking-band ranking-band-${slot.band}`}>
                      {slot.band}
                    </span>
                  </td>
                  <td className="num">{porcentaje(slot.observedRate)}</td>
                  <td className="num">{slot.flights}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  )
}

export default RankingPage
