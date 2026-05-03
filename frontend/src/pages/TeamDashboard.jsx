import api from '../api'
import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid, Legend, PieChart, Pie, Cell
} from 'recharts';
import StatCard from '../components/StatCard';
import LoadingSpinner from '../components/LoadingSpinner';

const TIP_STYLE = {
  backgroundColor: 'var(--bg-raised)',
  border: '1px solid var(--border-hi)',
  borderRadius: '8px',
  color: 'var(--text-main)',
  fontSize: '0.875rem',
};

const TeamDashboard = () => {
  const { teamName } = useParams();
  const navigate = useNavigate();
  const [teamData, setTeamData] = useState(null);
  const [seasons, setSeasons] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => { api.get('/api/seasons').then(r => setSeasons(r.data)); }, []);

  useEffect(() => {
    setLoading(true);
    api.get(`/api/teams/${teamName}/summary?season=${selectedSeason}`)
      .then(r => { setTeamData(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [teamName, selectedSeason]);

  if (loading || !teamData) return <LoadingSpinner />;

  const winLossData = [
    { name: 'Wins', value: teamData.wins },
    { name: 'Losses', value: teamData.matches - teamData.wins },
  ];
  const COLORS = ['var(--green)', 'var(--red)'];

  return (
    <div>
      <div className="dashboard-header">
        <div className="header-left">
          <button className="back-btn" onClick={() => navigate('/teams')}>
            ← Back
          </button>
          <div>
            <h1 className="page-title">{teamName}</h1>
            <p className="page-subtitle">Team analytics dashboard</p>
          </div>
        </div>
        <select
          className="premium-select"
          style={{ width: 'auto' }}
          value={selectedSeason}
          onChange={e => setSelectedSeason(e.target.value)}
        >
          <option value="all">All Seasons</option>
          {seasons.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="stats-grid">
        <StatCard title="Win Percentage" value={`${teamData.win_pct}%`} subtitle={`${teamData.wins} wins`} accentColor="var(--green)" />
        <StatCard title="Total Matches" value={teamData.matches} subtitle="Matches played" accentColor="var(--blue)" />
        <StatCard title="Net Run Rate" value={teamData.nrr} subtitle="NRR" accentColor={teamData.nrr >= 0 ? 'var(--green)' : 'var(--red)'} />
      </div>

      <div className="grid-layout">
        <div className="glass-card chart-card">
          <h2 className="card-title">Match Results</h2>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={winLossData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={4} dataKey="value" stroke="none">
                {winLossData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
              </Pie>
              <Tooltip contentStyle={TIP_STYLE} />
              <Legend verticalAlign="bottom" height={36} wrapperStyle={{ color: 'var(--text-sub)', fontSize: '0.875rem' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {selectedSeason === "all" && (
          <div className="glass-card chart-card">
            <h2 className="card-title">Season Win Timeline</h2>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={teamData.history}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="season" tick={{ fill: 'var(--text-sub)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-sub)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={TIP_STYLE} />
                <Line type="monotone" dataKey="wins" stroke="var(--indigo)" strokeWidth={2.5} dot={{ r: 3, fill: 'var(--indigo)' }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="grid-layout" style={{ marginTop: '1.25rem' }}>
        <div className="glass-card">
          <h3 className="card-title">Top 3 Batters</h3>
          <div className="table-container" style={{ border: 'none' }}>
            <table>
              <thead><tr><th>Batter</th><th>Runs</th><th>Strike Rate</th></tr></thead>
              <tbody>
                {teamData.top_batters.map((b, i) => (
                  <tr key={i}>
                    <td><span className="player-link" onClick={() => navigate(`/players?q=${encodeURIComponent(b.batter)}`)}>{b.batter}</span></td>
                    <td style={{ color: 'var(--amber)', fontWeight: 700 }}>{b.runs}</td>
                    <td>{b.strike_rate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="glass-card">
          <h3 className="card-title">Top 3 Bowlers</h3>
          <div className="table-container" style={{ border: 'none' }}>
            <table>
              <thead><tr><th>Bowler</th><th>Wickets</th></tr></thead>
              <tbody>
                {teamData.top_bowlers.map((b, i) => (
                  <tr key={i}>
                    <td><span className="player-link" onClick={() => navigate(`/players?q=${encodeURIComponent(b.bowler)}`)}>{b.bowler}</span></td>
                    <td style={{ color: 'var(--indigo)', fontWeight: 700 }}>{b.wickets}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeamDashboard;
