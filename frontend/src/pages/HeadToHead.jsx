import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';

const C1 = 'var(--blue)';
const C2 = 'var(--amber)';
const TIP_STYLE = {
  backgroundColor: 'var(--bg-raised)',
  border: '1px solid var(--border-hi)',
  borderRadius: '8px',
  color: 'var(--text-main)',
  fontSize: '0.875rem',
};

const RowStat = ({ label, v1, v2 }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '.75rem 1rem', borderBottom: '1px solid var(--border)' }}>
    <span style={{ color: C1, fontWeight: 700, fontSize: '1.0625rem', minWidth: 60 }}>{v1}</span>
    <span style={{ color: 'var(--text-sub)', fontSize: '.8125rem', textAlign: 'center', flex: 1 }}>{label}</span>
    <span style={{ color: C2, fontWeight: 700, fontSize: '1.0625rem', minWidth: 60, textAlign: 'right' }}>{v2}</span>
  </div>
);

export default function HeadToHead() {
  const [teams, setTeams] = useState([]);
  const [seasons, setSeasons] = useState([]);
  const [team1, setTeam1] = useState('');
  const [team2, setTeam2] = useState('');
  const [fromSeason, setFromSeason] = useState('');
  const [toSeason, setToSeason] = useState('');
  const [stats, setStats] = useState(null);
  const [venues, setVenues] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/api/teams').then(r => { setTeams(r.data); if (r.data.length >= 2) { setTeam1(r.data[0]); setTeam2(r.data[1]); } });
    api.get('/api/seasons').then(r => setSeasons(r.data));
  }, []);

  const fetchAll = () => {
    if (!team1 || !team2 || team1 === team2) return;
    setLoading(true); setError(''); setStats(null); setVenues(null);
    const params = new URLSearchParams({ team1, team2 });
    if (fromSeason) params.set('from', fromSeason);
    if (toSeason) params.set('to', toSeason);
    Promise.all([api.get(`/api/h2h?${params}`), api.get(`/api/h2h/venues?${params}`)])
      .then(([h, v]) => {
        if (h.data.error) { setError(h.data.error); setLoading(false); return; }
        setStats(h.data); setVenues(v.data.error ? null : v.data); setLoading(false);
      })
      .catch(() => { setError('Failed to load data.'); setLoading(false); });
  };

  useEffect(() => { if (team1 && team2 && team1 !== team2) fetchAll(); }, [team1, team2, fromSeason, toSeason]);

  const pieData = stats ? [{ name: stats.team1, value: stats.team1_wins }, { name: stats.team2, value: stats.team2_wins }] : [];
  const venueBar = venues?.venues?.slice(0, 6).map(v => ({
    name: v.venue.length > 22 ? v.venue.slice(0, 22) + '…' : v.venue,
    [stats?.team1 || 't1']: v.team1_wins,
    [stats?.team2 || 't2']: v.team2_wins,
  })) ?? [];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Head to Head</h1>
        <p className="page-subtitle">Compare two IPL teams across seasons and venues</p>
      </div>

      {/* Filter Card */}
      <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div className="form-group" style={{ flex: 2, minWidth: 160 }}>
            <label className="form-label">Team 1</label>
            <select className="premium-select" value={team1} onChange={e => setTeam1(e.target.value)}>
              {teams.map(t => <option key={t} value={t} disabled={t === team2}>{t}</option>)}
            </select>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', paddingBottom: '.625rem' }}>
            <span style={{ fontSize: '.875rem', fontWeight: 700, color: 'var(--text-sub)', letterSpacing: '.05em' }}>VS</span>
          </div>
          <div className="form-group" style={{ flex: 2, minWidth: 160 }}>
            <label className="form-label">Team 2</label>
            <select className="premium-select" value={team2} onChange={e => setTeam2(e.target.value)}>
              {teams.map(t => <option key={t} value={t} disabled={t === team1}>{t}</option>)}
            </select>
          </div>
          <div className="form-group" style={{ flex: 1, minWidth: 120 }}>
            <label className="form-label">From</label>
            <select className="premium-select" value={fromSeason} onChange={e => setFromSeason(e.target.value)}>
              <option value="">All time</option>
              {seasons.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="form-group" style={{ flex: 1, minWidth: 120 }}>
            <label className="form-label">To</label>
            <select className="premium-select" value={toSeason} onChange={e => setToSeason(e.target.value)}>
              <option value="">All time</option>
              {seasons.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <div className="spinner" style={{ margin: '0 auto' }} />
          <p className="loading-text" style={{ marginTop: '1rem' }}>Loading match data…</p>
        </div>
      )}

      {!loading && error && (
        <div className="glass-card" style={{ textAlign: 'center', padding: '2rem', color: 'var(--red)' }}>{error}</div>
      )}

      {!loading && stats && (
        <>
          {/* Tabs */}
          <div style={{ display: 'flex', gap: '.5rem', marginBottom: '1.5rem' }}>
            {['overview', 'venues', 'matches'].map(id => (
              <button key={id} className={`btn-tab${activeTab === id ? ' active' : ''}`} onClick={() => setActiveTab(id)}>
                {id.charAt(0).toUpperCase() + id.slice(1)}
              </button>
            ))}
          </div>

          {activeTab === 'overview' && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <span style={{ color: C1, fontWeight: 700 }}>{stats.team1}</span>
                <span style={{ color: 'var(--text-sub)', fontSize: '.8125rem' }}>
                  {stats.from_season && stats.to_season ? `${stats.from_season} – ${stats.to_season}` :
                   stats.from_season ? `From ${stats.from_season}` :
                   stats.to_season ? `Up to ${stats.to_season}` : 'All Time'}
                </span>
                <span style={{ color: C2, fontWeight: 700 }}>{stats.team2}</span>
              </div>

              <div className="grid-layout">
                <div className="glass-card chart-card">
                  <h2 className="card-title">Win Distribution</h2>
                  <ResponsiveContainer width="100%" height={260}>
                    <PieChart>
                      <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={4} dataKey="value" stroke="none">
                        <Cell fill={C1} /><Cell fill={C2} />
                      </Pie>
                      <Tooltip contentStyle={TIP_STYLE} />
                      <Legend verticalAlign="bottom" height={36} wrapperStyle={{ color: 'var(--text-sub)', fontSize: '.875rem' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="glass-card">
                  <h2 className="card-title">Match Stats</h2>
                  <RowStat label="Wins" v1={stats.team1_wins} v2={stats.team2_wins} />
                  <RowStat label="Win %" v1={`${stats.team1_win_pct}%`} v2={`${stats.team2_win_pct}%`} />
                  <div style={{ padding: '.75rem 1rem', borderBottom: '1px solid var(--border)', textAlign: 'center' }}>
                    <span style={{ color: 'var(--text-sub)', fontSize: '.8125rem' }}>Total Matches — </span>
                    <span style={{ fontWeight: 700 }}>{stats.matches}</span>
                  </div>
                  {stats.no_result > 0 && (
                    <div style={{ padding: '.75rem 1rem', textAlign: 'center' }}>
                      <span style={{ color: 'var(--text-sub)', fontSize: '.8125rem' }}>No Result — </span>
                      <span style={{ fontWeight: 700 }}>{stats.no_result}</span>
                    </div>
                  )}
                </div>
              </div>

              {stats.highest_scoring_match && (
                <div className="glass-card" style={{ marginTop: '1.25rem' }}>
                  <h2 className="card-title">Highest Scoring Match</h2>
                  <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                    {[['Date', stats.highest_scoring_match.date], ['Season', stats.highest_scoring_match.season], ['Venue', stats.highest_scoring_match.venue], ['Total Runs', stats.highest_scoring_match.total_runs], ['Winner', stats.highest_scoring_match.winner]].map(([k, v]) => (
                      <div key={k}>
                        <div style={{ fontSize: '.6875rem', textTransform: 'uppercase', letterSpacing: '.06em', color: 'var(--text-sub)', fontWeight: 600 }}>{k}</div>
                        <div style={{ fontWeight: 600, color: k === 'Total Runs' ? C1 : k === 'Winner' ? C2 : 'var(--text-main)' }}>{v || '—'}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {activeTab === 'venues' && venues && (
            <>
              <div className="grid-layout" style={{ marginBottom: '1.25rem' }}>
                {[
                  { key: 'most_played_venue', title: 'Most Played', color: C1, val: v => `${v.matches} matches` },
                  { key: 'team1_fortress', title: `${stats.team1} Fortress`, color: C1, val: v => `${v.team1_wins} wins here` },
                  { key: 'team2_fortress', title: `${stats.team2} Fortress`, color: C2, val: v => `${v.team2_wins} wins here` },
                ].map(({ key, title, color, val }) => venues[key] && (
                  <div key={key} className="glass-card" style={{ borderTop: `2px solid ${color}` }}>
                    <h2 className="card-title" style={{ color }}>{title}</h2>
                    <p style={{ fontWeight: 600, marginBottom: '.25rem' }}>{venues[key].venue}</p>
                    <p style={{ fontSize: '.875rem', color: 'var(--text-sub)' }}>{val(venues[key])}</p>
                  </div>
                ))}
              </div>

              <div className="glass-card chart-card">
                <h2 className="card-title">Wins by Venue (Top 6)</h2>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={venueBar} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                    <XAxis type="number" tick={{ fill: 'var(--text-sub)', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis type="category" dataKey="name" tick={{ fill: 'var(--text-sub)', fontSize: 11 }} width={140} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={TIP_STYLE} cursor={{ fill: 'rgba(255,255,255,.04)', radius: [0, 4, 4, 0] }} />
                    <Legend wrapperStyle={{ color: 'var(--text-sub)', fontSize: '.875rem' }} />
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
              <div className="table-container" style={{ border: 'none' }}>
                <table>
                  <thead>
                    <tr>{['Date', 'Season', 'Venue', 'Winner', 'Margin'].map(h => <th key={h}>{h}</th>)}</tr>
                  </thead>
                  <tbody>
                    {stats.recent_matches.map((m, i) => (
                      <tr key={i}>
                        <td style={{ color: 'var(--text-sub)' }}>{m.date}</td>
                        <td>{m.season}</td>
                        <td style={{ color: 'var(--text-sub)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>{m.venue}</td>
                        <td style={{ fontWeight: 600, color: m.winner === stats.team1 ? C1 : C2 }}>{m.winner || 'No Result'}</td>
                        <td style={{ color: 'var(--text-sub)' }}>{m.result_margin ? `${m.result_margin} ${m.result_type}` : '—'}</td>
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
