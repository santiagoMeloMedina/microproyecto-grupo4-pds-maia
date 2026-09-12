import { NavLink, Route, Routes } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import PredictionPage from './pages/PredictionPage'
import RankingPage from './pages/RankingPage'
import './App.css'

const claseEnlace = ({ isActive }: { isActive: boolean }) =>
  isActive ? 'app-nav-link active' : 'app-nav-link'

function App() {
  return (
    <div className="app-shell">
      <nav className="app-nav">
        <span className="app-brand">
          Microproyecto - Desarrollo de Soluciones
          <span className="app-brand-dataset">Airlines Dataset</span>
        </span>
        <NavLink to="/" end className={claseEnlace}>
          Visualización de datos
        </NavLink>
        <NavLink to="/franjas" className={claseEnlace}>
          Franjas a reforzar
        </NavLink>
        <NavLink to="/prediccion" className={claseEnlace}>
          ¿Qué riesgo tiene tu itinerario?
        </NavLink>
      </nav>

      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/franjas" element={<RankingPage />} />
        <Route path="/prediccion" element={<PredictionPage />} />
      </Routes>
    </div>
  )
}

export default App
