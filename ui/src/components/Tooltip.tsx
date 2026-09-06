import { useId, useState } from 'react'
import './Tooltip.css'

interface TooltipProps {
  label: string
  text: string
}

function Tooltip({ label, text }: TooltipProps) {
  const [visible, setVisible] = useState(false)
  const tooltipId = useId()

  return (
    <span className="tooltip">
      <button
        type="button"
        className="tooltip-trigger"
        aria-describedby={tooltipId}
        aria-label={label}
        onMouseEnter={() => setVisible(true)}
        onMouseLeave={() => setVisible(false)}
        onFocus={() => setVisible(true)}
        onBlur={() => setVisible(false)}
      >
        i
      </button>
      {visible && (
        <span role="tooltip" id={tooltipId} className="tooltip-bubble">
          {text}
        </span>
      )}
    </span>
  )
}

export default Tooltip
