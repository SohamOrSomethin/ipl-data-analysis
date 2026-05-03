import api from '../api'
import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts'
import { useNavigate } from 'react-router-dom'

const TIP_STYLE = {
  backgroundColor: 'var(--bg-raised)',
  border: '1px solid var(--border-hi)',
  borderRadius: '8px',
  color: 'var(--text-main)',
  fontSize: '0.875rem',
};

export default function PurpleCap() {
  const [data, setData] = useState([])
  const [hovered, setHovered] = useState(null)
  const navigate = useNavigate()

  useEffect(() => { api.get('/api/purple-cap').then(r => setData(r.data)) }, [])

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Purple Cap Winners</h1>
        <p className="page-subtitle">Leading wicket-takers each IPL season</p>
      </div>

      <div className="glass-card chart-card" style={{ marginBottom: '1.25rem' }}>
        <h2 className="card-title">Wickets by Season</h2>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={data} margin={{ top: 4, right: 8, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
            <XAxis dataKey="season" tick={{ fill: 'var(--text-sub)', fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: 'var(--text-sub)', fontSize: 12 }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={TIP_STYLE}
              cursor={{ fill: 'rgba(99,102,241,0.08)', radius: 4 }}
              formatter={(v, _, props) => [v + ' wickets', `${props.payload.bowler} · ${props.payload.team}`]}
            />
            <Bar dataKey="wickets" radius={[4, 4, 0, 0]} barSize={24}>
              {data.map((_, i) => (
                <Cell
                  key={i}
                  fill={i === hovered ? '#818cf8' : 'var(--indigo)'}
                  onMouseEnter={() => setHovered(i)}
                  onMouseLeave={() => setHovered(null)}
                  style={{ cursor: 'pointer', transition: 'fill .15s' }}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="glass-card">
        <div className="table-container">
          <table>
            <thead>
              <tr><th>Season</th><th>Bowler</th><th>Wickets</th><th>Team</th></tr>
            </thead>
            <tbody>
              {data.map(row => (
                <tr key={row.season}>
                  <td>{row.season}</td>
                  <td>
                    <span className="player-link" onClick={() => navigate(`/players?q=${encodeURIComponent(row.bowler)}`)}>{row.bowler}</span>
                  </td>
                  <td style={{ color: 'var(--indigo)', fontWeight: 700 }}>{row.wickets}</td>
                  <td>{row.team}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
