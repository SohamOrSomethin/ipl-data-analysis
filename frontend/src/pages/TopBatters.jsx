import { useState, useEffect } from 'react'
import api from '../api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorBoundary from '../components/ErrorBoundary'
import { useNavigate } from 'react-router-dom'

const TIP_STYLE = {
  backgroundColor: 'var(--bg-raised)',
  border: '1px solid var(--border-hi)',
  borderRadius: '8px',
  color: 'var(--text-main)',
  fontSize: '0.875rem',
};

export default function TopBatters() {
  const [batters, setBatters] = useState([])
  const [seasons, setSeasons] = useState([])
  const [selected, setSelected] = useState('all')
  const [loading, setLoading] = useState(true)
  const [hovered, setHovered] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/static/data/seasons.json').then(r => setSeasons(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    api.get(`/api/top-batters?season=${selected}`)
      .then(r => { setBatters(r.data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [selected])

  return (
    <div className="glass-card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '.75rem' }}>
        <h2 className="card-title" style={{ margin: 0 }}>Top Run Scorers</h2>
        <select className="premium-select" style={{ width: 'auto' }} value={selected} onChange={e => setSelected(e.target.value)}>
          <option value="all">All Seasons</option>
          {seasons.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
      <ErrorBoundary>
        {loading ? <LoadingSpinner /> : (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={batters} layout="vertical" margin={{ top: 0, right: 16, left: 20, bottom: 0 }}>
              <XAxis type="number" tick={{ fill: 'var(--text-sub)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis
                type="category"
                dataKey="batter"
                tick={{ fill: 'var(--text-sub)', fontSize: 11, cursor: 'pointer' }}
                width={90}
                axisLine={false}
                tickLine={false}
                onClick={(d) => navigate(`/players?q=${encodeURIComponent(d.value)}`)}
              />
              <Tooltip
                contentStyle={TIP_STYLE}
                cursor={{ fill: 'rgba(245,158,11,0.07)', radius: [0, 4, 4, 0] }}
              />
              <Bar dataKey="runs" radius={[0, 4, 4, 0]} barSize={14}>
                {batters.map((_, i) => (
                  <Cell
                    key={i}
                    fill={i === hovered ? '#fbbf24' : 'var(--amber)'}
                    onMouseEnter={() => setHovered(i)}
                    onMouseLeave={() => setHovered(null)}
                    style={{ cursor: 'pointer', transition: 'fill .15s' }}
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
