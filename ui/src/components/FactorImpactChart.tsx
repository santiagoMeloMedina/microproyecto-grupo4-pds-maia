import type { PredictionFactor } from '../types/prediction'
import './FactorImpactChart.css'

interface FactorImpactChartProps {
  factors: PredictionFactor[]
}

function FactorImpactChart({ factors }: FactorImpactChartProps) {
  const total = factors.reduce((sum, factor) => sum + factor.impact, 0)

  return (
    <ul className="factor-impact-chart">
      {factors.map((factor) => {
        const share = total > 0 ? (factor.impact / total) * 100 : 0
        return (
          <li key={factor.key} className="factor-impact-row">
            <span className="factor-impact-label">{factor.label}</span>
            <span className="factor-impact-track">
              <span
                className="factor-impact-bar"
                style={{ width: `${share}%` }}
              />
            </span>
            <span className="factor-impact-value">{share.toFixed(0)}%</span>
          </li>
        )
      })}
    </ul>
  )
}

export default FactorImpactChart
