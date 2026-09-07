import type { RiskLevel } from '../types/prediction'
import './RiskGauge.css'

interface RiskGaugeProps {
  probability: number
  riskLevel: RiskLevel
}

const RISK_COLOR: Record<RiskLevel, string> = {
  bajo: '#5bc0be',
  medio: '#f5c518',
  alto: '#ff7a59',
}

const RISK_LABEL: Record<RiskLevel, string> = {
  bajo: 'Riesgo bajo',
  medio: 'Riesgo medio',
  alto: 'Riesgo alto',
}

function RiskGauge({ probability, riskLevel }: RiskGaugeProps) {
  const radius = 60
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - probability)
  const color = RISK_COLOR[riskLevel]

  return (
    <div className="risk-gauge">
      <svg viewBox="0 0 140 140" width="140" height="140">
        <circle
          cx="70"
          cy="70"
          r={radius}
          fill="none"
          stroke="var(--hairline)"
          strokeWidth="12"
        />
        <circle
          cx="70"
          cy="70"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 70 70)"
        />
        <text x="70" y="65" textAnchor="middle" className="risk-gauge-value">
          {Math.round(probability * 100)}%
        </text>
        <text x="70" y="85" textAnchor="middle" className="risk-gauge-caption">
          probabilidad
        </text>
      </svg>
      <p className="risk-gauge-label" style={{ color }}>
        {RISK_LABEL[riskLevel]}
      </p>
    </div>
  )
}

export default RiskGauge
