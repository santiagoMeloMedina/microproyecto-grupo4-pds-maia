export interface ScheduleSlot {
  airline: string
  route: string
  airportFrom: string
  airportTo: string
  dayOfWeek: number
  dayLabel: string
  slot: string
  time: number
  length: number
  /** Vuelos observados en el periodo para esa franja. */
  flights: number
  observedRate: number
  /** Riesgo estimado por el modelo, que es lo que ordena el ranking. */
  risk: number
  band: string
}

export interface SlotsSummary {
  delayRate: number | null
  flightsInSelection: number
  totalFlights: number
  scheduleSlots: number
  slotsOverThreshold: number
  slotsInSelection: number
  rocAuc: number | null
  threshold: number
}

export interface SlotFilters {
  airline?: string
  route?: string
  dayOfWeek?: number
  slot?: string
}
