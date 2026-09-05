import { NavLink, Route, Routes } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import PredictionPage from './pages/PredictionPage'
import './App.css'

function App() {
  return (
    <div className="app-shell">
      <nav className="app-nav">
        <NavLink
          to="/"
          end
          className={({ isActive }) => (isActive ? 'app-nav-link active' : 'app-nav-link')}
        >
          Visualización de datos
        </NavLink>
        <NavLink
          to="/prediccion"
          className={({ isActive }) => (isActive ? 'app-nav-link active' : 'app-nav-link')}
        >
          ¿Qué riesgo tiene tu itinerario?
        </NavLink>
      </nav>

      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/prediccion" element={<PredictionPage />} />
      </Routes>
    </div>
  )
}

export default App
