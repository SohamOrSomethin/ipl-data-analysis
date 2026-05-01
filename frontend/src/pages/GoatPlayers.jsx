import { useState, useEffect } from 'react'
import axios from 'axios'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorBoundary from '../components/ErrorBoundary'

export default function GoatPlayers() {
  const [role, setRole] = useState('batter')
  const [players, setPlayers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    axios.get(`/api/goat?role=${role}&limit=10`)
      .then(res => {
        setPlayers(res.data.players)
        setLoading(false)
      })
      .catch(err => {
        console.error("Error fetching GOAT players:", err)
        setLoading(false)
      })
  }, [role])

  return (
    <div className="glass-card page-container" style={{ padding: '2rem' }}>
      <h1 className="page-title" style={{ textAlign: 'center', marginBottom: '2rem', fontSize: '2.5rem', background: 'linear-gradient(45deg, #fbbf24, #f59e0b)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
        G.O.A.T Players
      </h1>
      
      <div className="select-container" style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '2rem' }}>
        <button 
          onClick={() => setRole('batter')}
          style={{ 
            padding: '0.75rem 2rem', 
            borderRadius: '8px', 
            border: '1px solid rgba(255,255,255,0.1)', 
            background: role === 'batter' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(255,255,255,0.05)', 
            color: role === 'batter' ? '#fbbf24' : '#94a3b8', 
            cursor: 'pointer', 
            transition: 'all 0.3s ease',
            fontWeight: role === 'batter' ? '600' : '400'
          }}
        >
          🏏 Batters
        </button>
        <button 
          onClick={() => setRole('bowler')}
          style={{ 
            padding: '0.75rem 2rem', 
            borderRadius: '8px', 
            border: '1px solid rgba(255,255,255,0.1)', 
            background: role === 'bowler' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(255,255,255,0.05)', 
            color: role === 'bowler' ? '#fbbf24' : '#94a3b8', 
            cursor: 'pointer', 
            transition: 'all 0.3s ease',
            fontWeight: role === 'bowler' ? '600' : '400'
          }}
        >
          ⚾ Bowlers
        </button>
      </div>

      <ErrorBoundary>
        {loading ? <LoadingSpinner /> : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
            {players.map((p, idx) => (
              <div key={idx} className="glass-card" style={{ position: 'relative', overflow: 'hidden', padding: '1.5rem' }}>
                <div style={{ position: 'absolute', top: 0, right: 0, padding: '0.5rem 1rem', background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', borderBottomLeftRadius: '12px', fontWeight: 'bold', fontSize: '1.1rem' }}>
                  #{p.rank}
                </div>
                
                <h3 style={{ fontSize: '1.4rem', marginBottom: '0.25rem', color: '#f8fafc', paddingRight: '3rem' }}>
                  {p.name}
                </h3>
                
                <div style={{ color: '#fbbf24', fontSize: '1.1rem', marginBottom: '1.25rem', fontWeight: '600' }}>
                  GOAT Score: {parseFloat(p.goat_score).toFixed(1)}
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.9rem', color: '#cbd5e1' }}>
                  <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ color: '#94a3b8', fontSize: '0.8rem', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Matches</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: '500', color: '#f1f5f9' }}>{p.stats.matches}</div>
                  </div>
                  
                  {role === 'batter' ? (
                    <>
                      <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                        <div style={{ color: '#94a3b8', fontSize: '0.8rem', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Runs</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: '500', color: '#f1f5f9' }}>{p.stats.runs}</div>
                      </div>
                      <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                        <div style={{ color: '#94a3b8', fontSize: '0.8rem', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Strike Rate</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: '500', color: '#f1f5f9' }}>{p.stats.strike_rate}</div>
                      </div>
                      <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                        <div style={{ color: '#94a3b8', fontSize: '0.8rem', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Average</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: '500', color: '#f1f5f9' }}>{p.stats.batting_avg}</div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                        <div style={{ color: '#94a3b8', fontSize: '0.8rem', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Wickets</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: '500', color: '#f1f5f9' }}>{p.stats.wickets}</div>
                      </div>
                      <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                        <div style={{ color: '#94a3b8', fontSize: '0.8rem', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Economy</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: '500', color: '#f1f5f9' }}>{p.stats.economy}</div>
                      </div>
                      <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                        <div style={{ color: '#94a3b8', fontSize: '0.8rem', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Average</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: '500', color: '#f1f5f9' }}>{p.stats.bowling_avg}</div>
                      </div>
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
