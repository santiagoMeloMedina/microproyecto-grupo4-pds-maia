import { useEffect } from 'react'
import type { Widget } from '../types/widget'
import './WidgetModal.css'

interface WidgetModalProps {
  widget: Widget
  onClose: () => void
}

function WidgetModal({ widget, onClose }: WidgetModalProps) {
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  return (
    <div className="widget-modal-overlay" onClick={onClose}>
      <div
        className="widget-modal"
        role="dialog"
        aria-modal="true"
        aria-label={widget.title}
        onClick={(event) => event.stopPropagation()}
      >
        <header className="widget-modal-header">
          <h2>{widget.title}</h2>
          <button type="button" className="widget-modal-close" onClick={onClose}>
            Cerrar
          </button>
        </header>
        <p className="widget-modal-description">{widget.description}</p>
        <iframe src={widget.htmlPath} title={widget.title} />
      </div>
    </div>
  )
}

export default WidgetModal
