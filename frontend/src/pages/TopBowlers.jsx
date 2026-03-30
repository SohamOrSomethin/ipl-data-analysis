import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function TopBowlers() {
  const [bowlers, setBowlers] = useState([])
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
          .sort((a, b) => b.wickets - a.wickets)
          .slice(0, 10)
          .map(p => ({ bowler: p.name, wickets: p.wickets }))
        setBowlers(top10)
        setLoading(false)
      })
    } else {
      axios.get(`http://localhost:5000/api/top-bowlers?season=${selected}`)
        .then(res => {
          setBowlers(res.data)
          setLoading(false)
        })
    }
  }, [selected])

  return (
    <div className="glass-card">
      <h2 className="card-title">Top Wicket Takers</h2>

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
          <BarChart data={bowlers} layout="vertical" margin={{ top: 10, right: 30, left: 30, bottom: 0 }}>
            <XAxis type="number" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis type="category" dataKey="bowler" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} width={80} />
            <Tooltip 
              cursor={{ fill: 'rgba(255, 255, 255, 0.04)' }}
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }}
              itemStyle={{ color: '#06b6d4', fontWeight: 600 }}
            />
            <Bar dataKey="wickets" fill="#06b6d4" radius={[0, 4, 4, 0]} barSize={16} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}