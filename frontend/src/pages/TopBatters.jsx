import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function TopBatters() {
  const [batters, setBatters] = useState([])
  const [seasons, setSeasons] = useState([])
  const [selected, setSelected] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get('/data/seasons.json')
      .then(res => setSeasons(res.data))
  }, [])

  useEffect(() => {
    setLoading(true)
    if (selected === 'all') {
      axios.get('/data/players.json').then(res => {
        const top10 = res.data
          .sort((a, b) => b.runs - a.runs)
          .slice(0, 10)
          .map(p => ({ batter: p.name, runs: p.runs }))
        setBatters(top10)
        setLoading(false)
      })
    } else {
      axios.get(`http://localhost:5000/api/top-batters?season=${selected}`)
        .then(res => {
          setBatters(res.data)
          setLoading(false)
        })
    }
  }, [selected])

  return (
    <div className="glass-card">
      <h2 className="card-title">Top Run Scorers</h2>

      <div className="select-container">
        <select className="premium-select" value={selected} onChange={e => setSelected(e.target.value)}>
          <option value="all">All Seasons</option>
          {seasons.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {loading ? <p>Loading...</p> : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={batters} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis dataKey="batter" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <Tooltip 
              cursor={{ fill: 'rgba(255, 255, 255, 0.04)' }}
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }}
              itemStyle={{ color: '#06b6d4', fontWeight: 600 }}
            />
            <Bar dataKey="runs" fill="#06b6d4" radius={[4, 4, 0, 0]} barSize={32} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}