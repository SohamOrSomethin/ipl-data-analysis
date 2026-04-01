import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import OrangeCap from './pages/OrangeCap'
import PurpleCap from './pages/PurpleCap'
import Navbar from './components/Navbar'
import ErrorBoundary from './components/ErrorBoundary'

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
              <Route path="/players" element={<div className="glass-card"><h2>Player Analytics</h2><p>Coming Soon...</p></div>} />
            </Routes>
          </ErrorBoundary>
        </main>
      </div>
    </Router>
  )
}

export default App