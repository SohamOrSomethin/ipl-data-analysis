import { useState, useEffect } from 'react'
import api from '../api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorBoundary from '../components/ErrorBoundary'
import { useNavigate } from 'react-router-dom'

const StatPill = ({ label, value }) => (
  <div style={{ background: 'var(--bg-main)', padding: '.625rem .875rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)' }}>
    <div style={{ fontSize: '.6875rem', textTransform: 'uppercase', letterSpacing: '.06em', color: 'var(--text-sub)', fontWeight: 600, marginBottom: '.15rem' }}>{label}</div>
    <div style={{ fontSize: '1.0625rem', fontWeight: 700, color: 'var(--text-main)' }}>{value}</div>
  </div>
);

export default function GoatPlayers() {
  const [role, setRole] = useState('batter')
  const [players, setPlayers] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    api.get(`/api/goat?role=${role}&limit=10`)
      .then(r => { setPlayers(r.data.players); setLoading(false) })
      .catch(() => setLoading(false))
  }, [role])

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">G.O.A.T Players</h1>
        <p className="page-subtitle">Greatest of all time — ranked by composite performance score</p>
      </div>

      <div style={{ display: 'flex', gap: '.5rem', marginBottom: '2rem' }}>
        <button className={`btn-tab${role === 'batter' ? ' active' : ''}`} onClick={() => setRole('batter')}>Batters</button>
        <button className={`btn-tab${role === 'bowler' ? ' active' : ''}`} onClick={() => setRole('bowler')}>Bowlers</button>
      </div>

      <ErrorBoundary>
        {loading ? <LoadingSpinner /> : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
            {players.map((p, idx) => (
              <div key={idx} className="glass-card" style={{ padding: '1.5rem', position: 'relative', borderTop: '2px solid var(--amber)' }}>
                <div style={{
                  position: 'absolute', top: '1.25rem', right: '1.25rem',
                  background: 'rgba(245,158,11,.12)', color: 'var(--amber)',
                  borderRadius: 'var(--radius-sm)', padding: '.2rem .55rem',
                  fontSize: '.8125rem', fontWeight: 700
                }}>#{p.rank}</div>

                <h3
                  className="player-link"
                  style={{ fontSize: '1.125rem', marginBottom: '.2rem', paddingRight: '2.5rem', cursor: 'pointer' }}
                  onClick={() => navigate(`/players?q=${encodeURIComponent(p.name)}`)}
                >
                  {p.name}
                </h3>

                <p style={{ fontSize: '.875rem', color: 'var(--amber)', fontWeight: 600, marginBottom: '1rem' }}>
                  GOAT Score: {parseFloat(p.goat_score).toFixed(1)}
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '.5rem' }}>
                  <StatPill label="Matches" value={p.stats.matches} />
                  {role === 'batter' ? (
                    <>
                      <StatPill label="Runs" value={p.stats.runs} />
                      <StatPill label="Strike Rate" value={p.stats.strike_rate} />
                      <StatPill label="Average" value={p.stats.batting_avg} />
                    </>
                  ) : (
                    <>
                      <StatPill label="Wickets" value={p.stats.wickets} />
                      <StatPill label="Economy" value={p.stats.economy} />
                      <StatPill label="Average" value={p.stats.bowling_avg} />
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </ErrorBoundary>
    </div>
  )
}
