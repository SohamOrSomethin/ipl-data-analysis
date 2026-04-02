import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const TEAM_LOGOS = {
  "Mumbai Indians": "https://upload.wikimedia.org/wikipedia/en/c/cd/Mumbai_Indians_Logo.svg",
  "Chennai Super Kings": "https://upload.wikimedia.org/wikipedia/en/2/2b/Chennai_Super_Kings_Logo.svg",
  "Kolkata Knight Riders": "https://upload.wikimedia.org/wikipedia/en/4/4c/Kolkata_Knight_Riders_Logo.svg",
  "Royal Challengers Bangalore": "https://upload.wikimedia.org/wikipedia/en/2/2b/Royal_Challengers_Bangalore_2020_logo.svg",
  "Rajasthan Royals": "https://upload.wikimedia.org/wikipedia/en/6/60/Rajasthan_Royals_Logo.svg",
  "Delhi Capitals": "https://upload.wikimedia.org/wikipedia/en/f/f5/Delhi_Capitals_Logo.svg",
  "Sunrisers Hyderabad": "https://upload.wikimedia.org/wikipedia/en/8/81/Sunrisers_Hyderabad.svg",
  "Punjab Kings": "https://upload.wikimedia.org/wikipedia/en/d/d4/Punjab_Kings_Logo.svg",
  "Gujarat Titans": "https://upload.wikimedia.org/wikipedia/en/0/09/Gujarat_Titans_Logo.svg",
  "Lucknow Super Giants": "https://upload.wikimedia.org/wikipedia/en/a/a9/Lucknow_Super_Giants_Logo.svg",
};

const TeamSelector = () => {
  const [teams, setTeams] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:5000/api/teams')
      .then(res => res.json())
      .then(data => setTeams(data));
  }, []);

  return (
    <div className="team-selector-page">
      <h1 className="section-title">Select Franchise</h1>
      <div className="team-grid">
        {teams.map(team => (
          <div key={team} className="glass-card team-card" onClick={() => navigate(`/teams/${team}`)}>
            <img src={TEAM_LOGOS[team] || "https://upload.wikimedia.org/wikipedia/en/c/cd/IPL2024Logo.png"} alt={team} className="team-logo" />
            <h3>{team}</h3>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TeamSelector;
