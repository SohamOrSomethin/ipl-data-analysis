import { useState, useEffect } from 'react'
import api from '../api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorBoundary from '../components/ErrorBoundary'

export default function TopBatters() {
  const [batters, setBatters] = useState([])
  const [seasons, setSeasons] = useState([])
  const [selected, setSelected] = useState('all')
  const [loading, setLoading] = useState(true)
  const [hoveredIndex, setHoveredIndex] = useState(null)

  useEffect(() => {
    api.get('/static/data/seasons.json')
      .then(res => setSeasons(res.data))
      .catch(err => console.error("Error fetching seasons:", err))
  }, [])

  useEffect(() => {
    setLoading(true)
    api.get(`/api/top-batters?season=${selected}`)
      .then(res => {
        setBatters(res.data)
        setLoading(false)
      })
      .catch(err => {
        console.error("Error fetching batters:", err)
        setLoading(false)
      })
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
      <ErrorBoundary>
        {loading ? <LoadingSpinner /> : (
          <ResponsiveContainer width="100%" height={300}>
          <BarChart data={batters} layout="vertical" margin={{ top: 10, right: 30, left: 30, bottom: 0 }}>
            <XAxis type="number" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis type="category" dataKey="batter" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} width={80} />
            <Tooltip 
              cursor={{ fill: 'rgba(255, 255, 255, 0.04)' }}
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }}
              itemStyle={{ color: '#f59e0b', fontWeight: 600 }}
            />
            <Bar 
              dataKey="runs" 
              radius={[0, 4, 4, 0]} 
              barSize={16}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              {batters.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`}
                  cursor="pointer"
                  fill={index === hoveredIndex ? '#fbbf24' : '#f59e0b'}
                  onMouseEnter={() => setHoveredIndex(index)}
                  style={{ transition: 'fill 0.3s ease' }}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
      </ErrorBoundary>
    </div>
  )
}

