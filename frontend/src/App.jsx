import TopBatters from './pages/TopBatters'
import TopBowlers from './pages/TopBowlers'
import OrangeCap from './pages/OrangeCap'
import PurpleCap from './pages/PurpleCap'

function App() {
  return (
    <div>
      <h1>IPL Dashboard</h1>
      <TopBatters/>
      <TopBowlers/>
      <OrangeCap />
      <PurpleCap />
    </div>
  )
}

export default App