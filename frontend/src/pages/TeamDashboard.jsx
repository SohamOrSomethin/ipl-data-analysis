import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  LineChart, Line, CartesianGrid, Legend 
} from 'recharts';
import StatCard from '../components/StatCard';
import LoadingSpinner from '../components/LoadingSpinner';

const TeamDashboard = () => {
    const { teamName } = useParams();
    const [teamData, setTeamData] = useState(null);
    const [seasons, setSeasons] = useState([]);
    const [selectedSeason, setSelectedSeason] = useState("all");
    const [loading, setLoading] = useState(true);

    // 1. Fetch available seasons for the dropdown
    useEffect(() => {
        fetch('http://localhost:5000/api/seasons')
            .then(res => res.json())
            .then(data => setSeasons(data));
    }, []);

    // 2. Fetch team summary whenever the team or selected season changes
    useEffect(() => {
        setLoading(true);
        fetch(`http://localhost:5000/api/teams/${teamName}/summary?season=${selectedSeason}`)
            .then(res => res.json())
            .then(data => {
                setTeamData(data);
                setLoading(false);
            });
    }, [teamName, selectedSeason]);

    if (loading || !teamData) return <LoadingSpinner />;

    // Prepare data for Home vs Away Bar Chart
    const homeAwayData = [
        { name: 'Home', matches: teamData.home_away.home },
        { name: 'Away', matches: teamData.home_away.away },
    ];

    return (
        <div className="dashboard-content">
            <div className="dashboard-header">
                <div className="header-left">
                    <button className="back-btn" onClick={() => window.history.back()}>← Back</button>
                    <h1>{teamName} Dashboard</h1>
                </div>
                <div className="select-container">
                    <select 
                        className="premium-select"
                        value={selectedSeason} 
                        onChange={(e) => setSelectedSeason(e.target.value)}
                    >
                        <option value="all">All Seasons</option>
                        {seasons.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>
            </div>

            {/* Top Stats Row */}
            <div className="stats-grid">
                <StatCard title="Win Percentage" value={`${teamData.win_pct}%`} subtitle={`Wins: ${teamData.wins}`} accentColor="#06b6d4" />
                <StatCard title="Total Matches" value={teamData.matches} subtitle="Played" accentColor="#8b5cf6" />
                <StatCard title="Net Run Rate" value={teamData.nrr} subtitle="NRR" accentColor={teamData.nrr >= 0 ? "#10b981" : "#ef4444"} />
            </div>

            <div className="grid-layout">
                {/* Chart 1: Home vs Away (Bar) */}
                <div className="glass-card chart-card">
                    <h2 className="card-title">Home vs Away Split</h2>
                    <div style={{ width: '100%', height: 300 }}>
                        <ResponsiveContainer>
                            <BarChart data={homeAwayData}>
                                <XAxis dataKey="name" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }} />
                                <Bar dataKey="matches" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Chart 2: Season Win Timeline (Line) - Only show for "All Seasons" */}
                {selectedSeason === "all" && (
                    <div className="glass-card chart-card">
                        <h2 className="card-title">Season Win Timeline</h2>
                        <div style={{ width: '100%', height: 300 }}>
                            <ResponsiveContainer>
                                <LineChart data={teamData.history}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                    <XAxis dataKey="season" stroke="#94a3b8" />
                                    <YAxis stroke="#94a3b8" />
                                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }} />
                                    <Line type="monotone" dataKey="wins" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 8 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}
            </div>

            {/* Players Section */}
            <div className="grid-layout">
                <div className="glass-card">
                    <h3 className="card-title">Top 3 Batters</h3>
                    <table>
                        <thead>
                            <tr><th>Batter</th><th>Runs</th><th>SR</th></tr>
                        </thead>
                        <tbody>
                            {teamData.top_batters.map((b, i) => (
                                <tr key={i}><td>{b.batter}</td><td>{b.runs}</td><td>{b.strike_rate}</td></tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div className="glass-card">
                    <h3 className="card-title">Top 3 Bowlers</h3>
                    <table>
                        <thead>
                            <tr><th>Bowler</th><th>Wickets</th></tr>
                        </thead>
                        <tbody>
                            {teamData.top_bowlers.map((b, i) => (
                                <tr key={i}><td>{b.bowler}</td><td>{b.wickets}</td></tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default TeamDashboard;
