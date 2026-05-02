export default function PlayerCard({ player }) {
  const { name, runs, balls, fours, sixes, wickets } = player;

  const sr = balls > 0 ? ((runs / balls) * 100).toFixed(2) : "0.00";

  return (
    <div className="player-card glass-card">
      <div className="player-header">
        <h3 className="player-name">{name}</h3>
        <div className="player-badges">
          {runs > 5000 && <span className="badge elite">Elite Batter</span>}
          {wickets > 150 && <span className="badge elite">Elite Bowler</span>}
        </div>
      </div>

      <div className="player-stats-grid">
        {/* Batting Panel */}
        <div className="stats-panel batting-theme">
          <h4 className="panel-title">🏏 Batting Performance</h4>
          <div className="stats-metric-row">
            <div className="metric">
              <span className="label">Total Runs</span>
              <span className="value gold">{runs.toLocaleString()}</span>
            </div>
            <div className="metric">
              <span className="label">Strike Rate</span>
              <span className="value">{sr}</span>
            </div>
          </div>
          <div className="mini-metrics">
            <span className="mini-metric"><b>4s:</b> {fours}</span>
            <span className="mini-metric"><b>6s:</b> {sixes}</span>
            <span className="mini-metric"><b>Balls:</b> {balls}</span>
          </div>
        </div>

        {/* Bowling Panel */}
        <div className="stats-panel bowling-theme">
          <h4 className="panel-title">🎯 Bowling Performance</h4>
          <div className="stats-metric-row">
            <div className="metric">
              <span className="label">Total Wickets</span>
              <span className="value purple">{wickets}</span>
            </div>
          </div>
          <p className="panel-footer">
            {wickets > 0 ? "Key strike bowler for his franchises" : "Primarily a specialist batter"}
          </p>
        </div>
      </div>
    </div>
  );
}



