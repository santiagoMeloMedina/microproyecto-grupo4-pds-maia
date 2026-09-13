import { query, request } from './api'
import type { Catalog, Health, PredictionInput, PredictionResult } from '../types/prediction'
import type { ScheduleSlot, SlotFilters, SlotsSummary } from '../types/slots'

/**
 * Riesgo de retraso de un itinerario, estimado por el modelo empaquetado.
 *
 * La API expone el XGBoost ganador de los 90 experimentos de la Entrega 2,
 * instalado como paquete `model_riesgo_retraso`. La respuesta trae tambien el
 * umbral de operacion vigente, de modo que la interfaz no tenga que suponer
 * donde empieza cada banda de riesgo.
 */
export async function predictDelay(input: PredictionInput): Promise<PredictionResult> {
  return request<PredictionResult>('/predict', {
    method: 'POST',
    body: JSON.stringify({
      airline: input.airline,
      airportFrom: input.airportFrom,
      airportTo: input.airportTo,
      dayOfWeek: input.dayOfWeek,
      time: input.time,
      length: input.length,
    }),
  })
}

/** Aerolineas, aeropuertos, rutas frecuentes y dias validos del historico. */
export async function fetchCatalog(): Promise<Catalog> {
  return request<Catalog>('/catalog')
}

/** Estado de la API y version del modelo que esta sirviendo. */
export async function fetchHealth(): Promise<Health> {
  return request<Health>('/health')
}

/** Franjas de itinerario ordenadas por riesgo estimado, de mayor a menor. */
export async function fetchScheduleSlots(
  filters: SlotFilters = {},
  limit = 20,
): Promise<ScheduleSlot[]> {
  return request<ScheduleSlot[]>(`/schedule-slots${query({ ...filters, limit })}`)
}

/** Indicadores de la seleccion activa. */
export async function fetchSlotsSummary(filters: SlotFilters = {}): Promise<SlotsSummary> {
  return request<SlotsSummary>(`/schedule-slots/summary${query({ ...filters })}`)
}
