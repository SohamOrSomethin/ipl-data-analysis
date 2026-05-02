import { useEffect, useState } from 'react'
import api from '../api'
import TopBatters from './TopBatters'
import TopBowlers from './TopBowlers'
import StatCard from '../components/StatCard'
import OnThisDay from '../components/OnThisDay'

export default function Dashboard() {
  const [records, setRecords] = useState({
    total_runs: 0,
    total_wickets: 0,
    highest_score: 0,
    best_bowling: "0/0"
  })

  useEffect(() => {
    api.get('/static/data/records.json')
      .then(res => setRecords(res.data))
      .catch(err => console.error("Error loading records:", err))
  }, [])

  return (
    <>
      <OnThisDay />

      <div className="stats-grid">
        <StatCard 
          title="All-Time Runs" 
          value={records.total_runs.toLocaleString()} 
          subtitle="Total runs in IPL history" 
          icon="🏏" 
          accentColor="var(--accent-cyan)" 
        />
        <StatCard 
          title="All-Time Wickets" 
          value={records.total_wickets.toLocaleString()} 
          subtitle="Total wickets taken" 
          icon="🎯" 
          accentColor="var(--accent-purple)" 
        />
        <StatCard 
          title="Highest Score" 
          value={records.highest_score} 
          subtitle="Highest individual innings" 
          icon="🔥" 
          accentColor="#f59e0b" 
        />
        <StatCard 
          title="Best Bowling" 
          value={records.best_bowling} 
          subtitle="Best match figures" 
          icon="💨" 
          accentColor="#10b981" 
        />
      </div>

      <div className="grid-layout">
        <TopBatters/>
        <TopBowlers/>
      </div>
    </>
  )
}
