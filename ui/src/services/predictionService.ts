import type {
  PredictionFactor,
  PredictionInput,
  PredictionResult,
  RiskLevel,
} from '../types/prediction'

function hashToUnit(value: string): number {
  let hash = 0
  for (let i = 0; i < value.length; i += 1) {
    hash = (hash * 31 + value.charCodeAt(i)) | 0
  }
  return (Math.abs(hash) % 1000) / 1000
}

function timeOfDayFactor(minutesSinceMidnight: number): number {
  const hour = (minutesSinceMidnight / 60) % 24
  return (1 - Math.cos(((hour - 4) / 24) * 2 * Math.PI)) / 2
}

function riskLevelFor(probability: number): RiskLevel {
  if (probability < 0.3) return 'bajo'
  if (probability < 0.6) return 'medio'
  return 'alto'
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value))
}

export async function predictDelay(input: PredictionInput): Promise<PredictionResult> {
  const timeFactor = timeOfDayFactor(input.time)
  const airlineFactor = hashToUnit(input.airline)
  const routeFactor = (hashToUnit(input.airportFrom) + hashToUnit(input.airportTo)) / 2
  const dayFactor = hashToUnit(String(input.dayOfWeek))
  const lengthFactor = clamp(input.length / 400, 0, 1)

  const weighted: PredictionFactor[] = [
    { key: 'time', label: 'Franja horaria', impact: timeFactor * 0.3 },
    { key: 'airline', label: 'Aerolínea', impact: airlineFactor * 0.2 },
    { key: 'airportFrom', label: 'Ruta (origen-destino)', impact: routeFactor * 0.25 },
    { key: 'dayOfWeek', label: 'Día de la semana', impact: dayFactor * 0.15 },
    { key: 'length', label: 'Duración del vuelo', impact: lengthFactor * 0.1 },
  ]

  const probability = clamp(
    weighted.reduce((total, factor) => total + factor.impact, 0),
    0.02,
    0.98,
  )

  const factors = [...weighted].sort((a, b) => b.impact - a.impact)

  await new Promise((resolve) => setTimeout(resolve, 300))

  return {
    probability,
    riskLevel: riskLevelFor(probability),
    factors,
    notes: ['Resultado simulado, pendiente de integración con la API real del modelo.'],
  }
}
