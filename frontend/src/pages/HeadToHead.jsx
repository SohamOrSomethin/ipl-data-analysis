import React, { useState, useEffect } from 'react';
import api from '../api';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';

const C1  = '#06b6d4';
const C2  = '#f59e0b';

const RowStat = ({ label, v1, v2 }) => (
  <div style={{
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    padding: '0.85rem 1rem', borderBottom: '1px solid rgba(255,255,255,0.06)'
  }}>
    <span style={{ color: C1, fontWeight: 700, fontSize: '1.15rem', minWidth: 60 }}>{v1}</span>
    <span style={{ color: '#94a3b8', fontSize: '0.85rem', textAlign: 'center', flex: 1 }}>{label}</span>
    <span style={{ color: C2, fontWeight: 700, fontSize: '1.15rem', minWidth: 60, textAlign: 'right' }}>{v2}</span>
  </div>
);

export default function HeadToHead() {
  const [teams,      setTeams]      = useState([]);
  const [seasons,    setSeasons]    = useState([]);
  const [team1,      setTeam1]      = useState('');
  const [team2,      setTeam2]      = useState('');
  const [fromSeason, setFromSeason] = useState('');
  const [toSeason,   setToSeason]   = useState('');
  const [stats,      setStats]      = useState(null);
  const [venues,     setVenues]     = useState(null);
  const [loading,    setLoading]    = useState(false);
  const [error,      setError]      = useState('');
  const [activeTab,  setActiveTab]  = useState('overview');

  useEffect(() => {
    api.get('/api/teams')
      .then(res => {
        setTeams(res.data);
        if (res.data.length >= 2) { setTeam1(res.data[0]); setTeam2(res.data[1]); }
      });
    api.get('/api/seasons')
      .then(res => setSeasons(res.data));
  }, []);

  const fetchAll = () => {
    if (!team1 || !team2 || team1 === team2) return;
    setLoading(true); setError(''); setStats(null); setVenues(null);

    const params = new URLSearchParams({ team1, team2 });
    if (fromSeason) params.set('from', fromSeason);
    if (toSeason)   params.set('to',   toSeason);
    const qs = params.toString();

    Promise.all([
      api.get(`/api/h2h?${qs}`),
      api.get(`/api/h2h/venues?${qs}`),
    ])
      .then(([h2hRes, venRes]) => {
        if (h2hRes.data.error) { setError(h2hRes.data.error); setLoading(false); return; }
        setStats(h2hRes.data);
        setVenues(venRes.data.error ? null : venRes.data);
        setLoading(false);
      })
      .catch(() => { setError('Failed to load data.'); setLoading(false); });
  };

  useEffect(() => {
    if (team1 && team2 && team1 !== team2) fetchAll();
  }, [team1, team2, fromSeason, toSeason]);

  const pieData = stats
    ? [
        { name: stats.team1, value: stats.team1_wins },
        { name: stats.team2, value: stats.team2_wins },
      ]
    : [];

  const venueBar = venues?.venues
    ?.slice(0, 6)
    .map(v => ({
      name: v.venue.length > 22 ? v.venue.slice(0, 22) + '\u2026' : v.venue,
      [stats?.team1 || 't1']: v.team1_wins,
      [stats?.team2 || 't2']: v.team2_wins,
    })) ?? [];

  const Tab = ({ id, label }) => (
    <button
      onClick={() => setActiveTab(id)}
      style={{
        padding: '0.5rem 1.25rem', borderRadius: 8, border: 'none', cursor: 'pointer',
        fontWeight: 600, fontSize: '0.875rem',
        background: activeTab === id ? C1 : 'rgba(255,255,255,0.05)',
        color:      activeTab === id ? '#0f172a' : '#94a3b8',
        transition: 'all 0.2s'
      }}
    >{label}</button>
  );

  return (
    <div className="dashboard-content">
      <h1 className="section-title">⚔️ <span className="text-gradient">Head-to-Head Comparison</span></h1>

      <div className="glass-card chart-card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div style={{ flex: 2, minWidth: 180 }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#94a3b8', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Team 1</label>
            <select className="premium-select" value={team1} onChange={e => setTeam1(e.target.value)}>
              {teams.map(t => <option key={t} value={t} disabled={t === team2}>{t}</option>)}
            </select>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.15rem', paddingBottom: '0.75rem' }}>
            <span style={{ fontSize: '1.4rem', fontWeight: 800, color: '#e2e8f0' }}>VS</span>
          </div>
          <div style={{ flex: 2, minWidth: 180 }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#94a3b8', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Team 2</label>
            <select className="premium-select" value={team2} onChange={e => setTeam2(e.target.value)}>
              {teams.map(t => <option key={t} value={t} disabled={t === team1}>{t}</option>)}
            </select>
          </div>
          <div style={{ flex: 1, minWidth: 130 }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#94a3b8', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>From Season</label>
            <select className="premium-select" value={fromSeason} onChange={e => setFromSeason(e.target.value)}>
              <option value="">All time</option>
              {seasons.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div style={{ flex: 1, minWidth: 130 }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#94a3b8', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>To Season</label>
            <select className="premium-select" value={toSeason} onChange={e => setToSeason(e.target.value)}>
              <option value="">All time</option>
              {seasons.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
          <div className="spinner"><div className="spinner-ring"/><div className="spinner-ring"/><div className="spinner-core">⚔️</div></div>
          <p className="loading-text" style={{ marginTop: '1rem' }}>Loading head-to-head data…</p>
        </div>
      )}

      {!loading && error && (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem', color: '#f87171' }}>
          ⚠️ {error}
        </div>
      )}

      {!loading && stats && (
        <>
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <Tab id="overview" label="📊 Overview" />
            <Tab id="venues"   label="🏟️ Venues"   />
            <Tab id="matches"  label="📋 Matches"  />
          </div>

          {activeTab === 'overview' && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <span style={{ color: C1, fontWeight: 700, fontSize: '1.1rem' }}>{stats.team1}</span>
                <span style={{ color: '#475569', fontSize: '0.85rem' }}>
                  {stats.from_season && stats.to_season ? `${stats.from_season} – ${stats.to_season}` :
                   stats.from_season ? `From ${stats.from_season}` :
                   stats.to_season   ? `Up to ${stats.to_season}` : 'All Time'}
                </span>
                <span style={{ color: C2, fontWeight: 700, fontSize: '1.1rem' }}>{stats.team2}</span>
              </div>

              <div className="grid-layout">
                <div className="glass-card chart-card">
                  <h2 className="card-title">Win Distribution</h2>
                  <ResponsiveContainer width="100%" height={280}>
                    <PieChart>
                      <Pie data={pieData} cx="50%" cy="50%" innerRadius={65} outerRadius={105}
                           paddingAngle={4} dataKey="value" stroke="none">
                        <Cell fill={C1} />
                        <Cell fill={C2} />
                      </Pie>
                      <Tooltip contentStyle={{ background: '#1e293b', border: 'none', borderRadius: 8, color: '#fff' }} />
                      <Legend verticalAlign="bottom" height={36} wrapperStyle={{ color: '#94a3b8' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="glass-card chart-card" style={{ justifyContent: 'center' }}>
                  <h2 className="card-title" style={{ textAlign: 'center' }}>Match Stats</h2>
                  <RowStat label="Wins" v1={stats.team1_wins} v2={stats.team2_wins} />
                  <RowStat label="Win %" v1={`${stats.team1_win_pct}%`} v2={`${stats.team2_win_pct}%`} />
                  <div style={{ padding: '0.85rem 1rem', borderBottom: '1px solid rgba(255,255,255,0.06)', textAlign: 'center' }}>
                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Total Matches</span>
                    <span style={{ color: '#fff', fontWeight: 700, fontSize: '1.2rem', marginLeft: '0.75rem' }}>{stats.matches}</span>
                  </div>
                  {stats.no_result > 0 && (
                    <div style={{ padding: '0.85rem 1rem', textAlign: 'center' }}>
                      <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No Result</span>
                      <span style={{ color: '#fff', fontWeight: 700, marginLeft: '0.75rem' }}>{stats.no_result}</span>
                    </div>
                  )}
                </div>
              </div>

              {stats.highest_scoring_match && (
                <div className="glass-card" style={{ marginTop: '2rem', padding: '1.5rem' }}>
                  <h2 className="card-title">🔥 Highest Scoring Match</h2>
                  <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', alignItems: 'center' }}>
                    <div><div style={{ color: '#94a3b8', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Date</div><div style={{ fontWeight: 600 }}>{stats.highest_scoring_match.date || '—'}</div></div>
                    <div><div style={{ color: '#94a3b8', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Season</div><div style={{ fontWeight: 600 }}>{stats.highest_scoring_match.season || '—'}</div></div>
                    <div><div style={{ color: '#94a3b8', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Venue</div><div style={{ fontWeight: 600 }}>{stats.highest_scoring_match.venue || '—'}</div></div>
                    <div><div style={{ color: '#94a3b8', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Runs</div><div style={{ fontWeight: 700, fontSize: '1.5rem', color: C1 }}>{stats.highest_scoring_match.total_runs ?? '—'}</div></div>
                    <div><div style={{ color: '#94a3b8', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Winner</div><div style={{ fontWeight: 600, color: C2 }}>{stats.highest_scoring_match.winner || 'No Result'}</div></div>
                  </div>
                </div>
              )}
            </>
          )}

          {activeTab === 'venues' && venues && (
            <>
              <div className="grid-layout" style={{ marginBottom: '2rem' }}>
                {venues.most_played_venue && (
                  <div className="glass-card" style={{ borderTop: `3px solid ${C1}` }}>
                    <h2 className="card-title">🏟️ Most Played Venue</h2>
                    <div style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: '0.5rem' }}>{venues.most_played_venue.venue}</div>
                    <div style={{ color: '#94a3b8', fontSize: '0.9rem' }}>{venues.most_played_venue.matches} matches</div>
                  </div>
                )}
                {venues.team1_fortress && (
                  <div className="glass-card" style={{ borderTop: `3px solid ${C1}` }}>
                    <h2 className="card-title" style={{ color: C1 }}>🏰 {stats.team1} Fortress</h2>
                    <div style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: '0.5rem' }}>{venues.team1_fortress.venue}</div>
                    <div style={{ color: '#94a3b8', fontSize: '0.9rem' }}>{venues.team1_fortress.team1_wins} wins here</div>
                  </div>
                )}
                {venues.team2_fortress && (
                  <div className="glass-card" style={{ borderTop: `3px solid ${C2}` }}>
                    <h2 className="card-title" style={{ color: C2 }}>🏰 {stats.team2} Fortress</h2>
                    <div style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: '0.5rem' }}>{venues.team2_fortress.venue}</div>
                    <div style={{ color: '#94a3b8', fontSize: '0.9rem' }}>{venues.team2_fortress.team2_wins} wins here</div>
                  </div>
                )}
              </div>
              <div className="glass-card chart-card">
                <h2 className="card-title">Wins by Venue (Top 6)</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={venueBar} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" horizontal={false} />
                    <XAxis type="number" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <YAxis type="category" dataKey="name" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} width={140} />
                    <Tooltip contentStyle={{ background: '#1e293b', border: 'none', borderRadius: 8, color: '#fff' }} />
                    <Legend wrapperStyle={{ color: '#94a3b8' }} />
                    <Bar dataKey={stats.team1} fill={C1} radius={[0, 4, 4, 0]} barSize={10} />
                    <Bar dataKey={stats.team2} fill={C2} radius={[0, 4, 4, 0]} barSize={10} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}

          {activeTab === 'matches' && stats.recent_matches && (
            <div className="glass-card">
              <h2 className="card-title">Recent Matches</h2>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                      {['Date','Season','Venue','Winner','Margin'].map(h => (
                        <th key={h} style={{ padding: '0.75rem 1rem', textAlign: 'left', color: '#94a3b8', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {stats.recent_matches.map((m, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '0.75rem 1rem', color: '#94a3b8', fontSize: '0.9rem' }}>{m.date}</td>
                        <td style={{ padding: '0.75rem 1rem' }}>{m.season}</td>
                        <td style={{ padding: '0.75rem 1rem', color: '#94a3b8', fontSize: '0.9rem' }}>{m.venue}</td>
                        <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: m.winner === stats.team1 ? C1 : C2 }}>{m.winner || 'No Result'}</td>
                        <td style={{ padding: '0.75rem 1rem', color: '#94a3b8', fontSize: '0.9rem' }}>{m.result_margin ? `${m.result_margin} ${m.result_type}` : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
