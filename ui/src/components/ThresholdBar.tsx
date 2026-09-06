import './ThresholdBar.css'

interface ThresholdBarProps {
  probability: number
}

function ThresholdBar({ probability }: ThresholdBarProps) {
  const markerPosition = `${Math.min(100, Math.max(0, probability * 100))}%`

  return (
    <div className="threshold-bar">
      <div className="threshold-bar-track">
        <div className="threshold-segment threshold-low" style={{ width: '30%' }} />
        <div className="threshold-segment threshold-medium" style={{ width: '30%' }} />
        <div className="threshold-segment threshold-high" style={{ width: '40%' }} />
        <div className="threshold-marker" style={{ left: markerPosition }} />
      </div>
      <div className="threshold-legend">
        <span>Bajo (&lt;30%)</span>
        <span>Medio (30-60%)</span>
        <span>Alto (&gt;60%)</span>
      </div>
    </div>
  )
}

export default ThresholdBar
