import TopBatters from './pages/TopBatters'
import TopBowlers from './pages/TopBowlers'
import OrangeCap from './pages/OrangeCap'
import PurpleCap from './pages/PurpleCap'
import StatCard from './components/StatCard'

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
    
    <div>
      <StatCard title="Total Runs" value="12345" subtitle="Across all seasons" icon="🏏" accentColor="#D85A30" />
      <StatCard title="Total Wickets" value="6789" subtitle="Across all seasons" icon="🎯" accentColor="#1E90FF" />
      <StatCard title="Highest Score" value="200*" subtitle="By a single player" icon="🔥" accentColor="#FF4500" />
      <StatCard title="Best Bowling" value="6/20" subtitle="Best figures in an innings" icon="💨" accentColor="#32CD32" />
    </div>

    </div>


  )
}

export default App