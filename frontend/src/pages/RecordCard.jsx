import React, { useState, useEffect } from 'react';
import StatCard from '../components/StatCard';

export default function RecordCard() {
  const [records, setRecords] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      setRecords({
        highestTotal: { team: "Sunrisers Hyderabad", score: "287/3", opponent: "RCB", year: 2024 },
        lowestTotal: { team: "Royal Challengers Bangalore", score: "49/10", opponent: "KKR", year: 2017 },
        mostRuns: { player: "Virat Kohli", runs: "8004", team: "RCB" },
        mostWickets: { player: "Yuzvendra Chahal", wickets: "205", team: "RR" },
        highestIndividualScore: { player: "Chris Gayle", score: "175*", team: "RCB", year: 2013 },
        bestBowlingFigures: { player: "Alzarri Joseph", figures: "6/12", team: "MI", year: 2019 },
      });
      setLoading(false);
    }, 800);
  }, []);

  return (
    <div className="dashboard-content">
      <h1 className="section-title">🏆 All-Time IPL Records</h1>
      {loading ? (
        <div style={{ textAlign: 'center', color: '#94a3b8', padding: '3rem', fontSize: '1.2rem' }}>
          Loading records...
        </div>
      ) : (
        <div className="grid-layout">
          <StatCard 
            title="Highest Team Total" 
            value={records.highestTotal.score} 
            subtitle={`${records.highestTotal.team} vs ${records.highestTotal.opponent} (${records.highestTotal.year})`}
            accentColor="#f59e0b"
          />
          <StatCard 
            title="Lowest Team Total" 
            value={records.lowestTotal.score} 
            subtitle={`${records.lowestTotal.team} vs ${records.lowestTotal.opponent} (${records.lowestTotal.year})`}
            accentColor="#ef4444"
          />
          <StatCard 
            title="Most Runs (All Time)" 
            value={records.mostRuns.runs} 
            subtitle={`${records.mostRuns.player} (${records.mostRuns.team})`}
            accentColor="#06b6d4"
          />
          <StatCard 
            title="Most Wickets (All Time)" 
            value={records.mostWickets.wickets} 
            subtitle={`${records.mostWickets.player} (${records.mostWickets.team})`}
            accentColor="#8b5cf6"
          />
          <StatCard 
            title="Highest Individual Score" 
            value={records.highestIndividualScore.score} 
            subtitle={`${records.highestIndividualScore.player} (${records.highestIndividualScore.team}) - ${records.highestIndividualScore.year}`}
            accentColor="#10b981"
          />
          <StatCard 
            title="Best Bowling Figures" 
            value={records.bestBowlingFigures.figures} 
            subtitle={`${records.bestBowlingFigures.player} (${records.bestBowlingFigures.team}) - ${records.bestBowlingFigures.year}`}
            accentColor="#eab308"
          />
        </div>
      )}
    </div>
  );
}











