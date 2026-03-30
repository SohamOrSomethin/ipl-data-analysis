import TopBatters from './pages/TopBatters'
import TopBowlers from './pages/TopBowlers'
import OrangeCap from './pages/OrangeCap'
import PurpleCap from './pages/PurpleCap'

function App() {
  return (
    <div className="dashboard-container">
      <h1 className="app-title">IPL Data Analytics</h1>
      <div className="grid-layout">
        <TopBatters/>
        <TopBowlers/>
        <OrangeCap />
        <PurpleCap />
      </div>
    </div>
  )
}

export default App