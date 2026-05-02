import api from '../api'
import React, { useState, useEffect } from 'react';
import StatCard from '../components/StatCard';

const getTitle = (key) => {
   const titles = {
     highest_individual_score: "Highest Individual Score",
     worst_collapse: "Worst Collapse",
     most_expensive_over: "Most Expensive Over",
     fastest_fifty: "Fastest Fifty",
     most_sixes_innings: "Most Sixes (Innings)",
     best_bowling_figures: "Best Bowling Figures"
   };
   return titles[key] || "Record";
};

const getAccentColor = (index) => {
   const colors = ["#10b981", "#ef4444", "#ef4444", "#3b82f6", "#f59e0b", "#06b6d4"];
   return colors[index % colors.length];
};

export default function RecordCard() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/static/data/records_wall.json')
      .then(res => res.data)
      .then(data => {
        setRecords(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch records:", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="dashboard-content">
      <h1 className="section-title">🏆 <span className="text-gradient">All-Time IPL Records</span></h1>

      {loading ? (
        <div style={{ textAlign: 'center', color: '#94a3b8', padding: '3rem', fontSize: '1.2rem' }}>
          Loading records...
        </div>
      ) : records.length > 0 ? (
        <div className="grid-layout">
          {records.map((r, idx) => (
            <StatCard 
              key={r.key || idx}
              title={getTitle(r.key)} 
              value={r.value} 
              subtitle={`${r.player} (${r.season})`}
              accentColor={getAccentColor(idx)}
            />
          ))}
        </div>
      ) : (
        <div style={{ textAlign: 'center', color: '#ef4444', padding: '3rem' }}>
          Failed to load records.
        </div>
      )}
    </div>
  );
}




