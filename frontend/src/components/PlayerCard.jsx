import { useState } from 'react';

export default function PlayerCard({ player }) {
  const { name, runs, balls, fours, sixes, wickets } = player;
  const sr = balls > 0 ? ((runs / balls) * 100).toFixed(1) : '0.0';

  return (
    <div className="player-card glass-card">
      <div className="player-header">
        <div>
          <h3 className="player-name">{name}</h3>
          <div style={{ display: 'flex', gap: '.5rem', marginTop: '.4rem', flexWrap: 'wrap' }}>
            {runs > 5000 && <span className="badge elite">Elite Batter</span>}
            {wickets > 150 && <span className="badge elite">Elite Bowler</span>}
          </div>
        </div>
      </div>

      <div className="player-stats-grid">
        <div className="stats-panel batting-theme">
          <p className="panel-title">Batting</p>
          <div className="stats-metric-row">
            <div className="metric">
              <span className="label">Runs</span>
              <span className="value gold">{runs.toLocaleString()}</span>
            </div>
            <div className="metric">
              <span className="label">Strike Rate</span>
              <span className="value">{sr}</span>
            </div>
          </div>
          <div className="mini-metrics">
            <span><strong>4s:</strong> {fours}</span>
            <span><strong>6s:</strong> {sixes}</span>
            <span><strong>Balls:</strong> {balls.toLocaleString()}</span>
          </div>
        </div>

        <div className="stats-panel bowling-theme">
          <p className="panel-title">Bowling</p>
          <div className="stats-metric-row">
            <div className="metric">
              <span className="label">Wickets</span>
              <span className="value purple">{wickets}</span>
            </div>
          </div>
          <p style={{ fontSize: '.875rem', color: 'var(--text-sub)', marginTop: '.25rem' }}>
            {wickets > 0 ? 'Key strike bowler for his franchises' : 'Primarily a specialist batter'}
          </p>
        </div>
      </div>
    </div>
  );
}
