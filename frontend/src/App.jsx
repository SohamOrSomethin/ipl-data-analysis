import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import OrangeCap from './pages/OrangeCap'
import PurpleCap from './pages/PurpleCap'
import Players from './pages/Players'
import Navbar from './components/Navbar'
import ErrorBoundary from './components/ErrorBoundary'
import TeamSelector from './pages/TeamSelector'
import TeamDashboard from './pages/TeamDashboard'

function App() {
  return (
    <Router>
      <div className="app-shell">
        <Navbar />
        <main className="dashboard-container">
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/orange-cap" element={<OrangeCap />} />
              <Route path="/purple-cap" element={<PurpleCap />} />
              <Route path="/players" element={<Players />} />
              <Route path="/teams" element={<TeamSelector />} />
              <Route path="/teams/:teamName" element={<TeamDashboard />} />
            </Routes>
          </ErrorBoundary>
        </main>
      </div>
    </Router>
  )
}

export default App