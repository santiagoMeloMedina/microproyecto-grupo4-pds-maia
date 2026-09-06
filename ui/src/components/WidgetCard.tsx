import { useState } from 'react'
import type { Widget } from '../types/widget'
import Tooltip from './Tooltip'
import WidgetModal from './WidgetModal'
import './WidgetCard.css'

interface WidgetCardProps {
  widget: Widget
}

function WidgetCard({ widget }: WidgetCardProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <article className="widget-card">
      <header className="widget-card-header">
        <h2>{widget.title}</h2>
        <Tooltip label={`Acerca de ${widget.title}`} text={widget.description} />
      </header>

      <div className="widget-card-body">
        <iframe src={widget.thumbHtmlPath} title={widget.title} loading="lazy" />
      </div>

      <button
        type="button"
        className="widget-expand-button"
        onClick={() => setExpanded(true)}
      >
        Expandir
      </button>

      {expanded && (
        <WidgetModal widget={widget} onClose={() => setExpanded(false)} />
      )}
    </article>
  )
}

export default WidgetCard
