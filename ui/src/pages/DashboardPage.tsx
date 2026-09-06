import widgetData from '../data/widgets.json'
import type { Widget } from '../types/widget'
import WidgetCard from '../components/WidgetCard'
import './DashboardPage.css'

const widgets = widgetData as Widget[]

function DashboardPage() {
  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <h1>Tablero de retrasos de vuelos</h1>
      </header>
      <section className="dashboard-grid">
        {widgets.map((widget) => (
          <WidgetCard key={widget.id} widget={widget} />
        ))}
      </section>
    </main>
  )
}

export default DashboardPage
