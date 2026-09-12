export interface PredictionInput {
  airline: string
  airportFrom: string
  airportTo: string
  dayOfWeek: number
  time: number
  length: number
}

export type RiskLevel = 'bajo' | 'medio' | 'alto'

/** Tasa historica de retraso de un grupo, para contrastar la prediccion. */
export interface ReferenceRate {
  label: string
  rate: number
}

export interface PredictionResult {
  probability: number
  /** Banda de accion segun el punto de operacion, no un corte arbitrario. */
  band: RiskLevel
  /** Umbral de refuerzo que devuelve la API: por encima, la franja se marca. */
  threshold: number
  /** Corte de la banda alta. */
  highBandThreshold: number
  references: ReferenceRate[]
  modelVersion: string
}

export interface DayOption {
  value: number
  label: string
}

export interface Catalog {
  airlines: string[]
  airports: string[]
  routes: string[]
  days: DayOption[]
}

export interface Health {
  name: string
  apiVersion: string
  modelVersion: string
  modelFamily: string
  threshold: number
  highBandThreshold: number
}
