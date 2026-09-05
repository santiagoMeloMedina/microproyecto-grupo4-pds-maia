export interface PredictionInput {
  airline: string
  airportFrom: string
  airportTo: string
  dayOfWeek: number
  time: number
  length: number
}

export interface PredictionFactor {
  key: keyof PredictionInput
  label: string
  impact: number
}

export type RiskLevel = 'bajo' | 'medio' | 'alto'

export interface PredictionResult {
  probability: number
  riskLevel: RiskLevel
  factors: PredictionFactor[]
  notes: string[]
}
