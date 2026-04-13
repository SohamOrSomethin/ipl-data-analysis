import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const TEAM_LOGOS = {
  "Mumbai Indians": "https://upload.wikimedia.org/wikipedia/en/c/cd/Mumbai_Indians_Logo.svg",
  "Chennai Super Kings": "https://upload.wikimedia.org/wikipedia/en/2/2b/Chennai_Super_Kings_Logo.svg",
  "Kolkata Knight Riders": "https://upload.wikimedia.org/wikipedia/en/4/4c/Kolkata_Knight_Riders_Logo.svg",
  "Royal Challengers Bangalore": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d4/Royal_Challengers_Bengaluru_Logo.svg/250px-Royal_Challengers_Bengaluru_Logo.svg.png",
  "Rajasthan Royals": "https://upload.wikimedia.org/wikipedia/hi/thumb/6/60/Rajasthan_Royals_Logo.svg/960px-Rajasthan_Royals_Logo.svg.png",
  "Delhi Capitals": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2f/Delhi_Capitals.svg/1280px-Delhi_Capitals.svg.png",
  "Sunrisers Hyderabad": "https://www.sunrisershyderabad.in/assets/teamLogo/srhLogo.svg",
  "Punjab Kings": "https://upload.wikimedia.org/wikipedia/en/d/d4/Punjab_Kings_Logo.svg",
  "Gujarat Titans": "https://upload.wikimedia.org/wikipedia/en/0/09/Gujarat_Titans_Logo.svg",
  "Lucknow Super Giants": "https://upload.wikimedia.org/wikipedia/en/thumb/3/34/Lucknow_Super_Giants_Logo.svg/1280px-Lucknow_Super_Giants_Logo.svg.png",
  "Rising Pune Supergiants": "https://upload.wikimedia.org/wikipedia/en/9/9a/Rising_Pune_Supergiant.png",
  "Gujarat Lions": "https://upload.wikimedia.org/wikipedia/en/c/c4/Gujarat_Lions.png",
  "Deccan Chargers": "https://upload.wikimedia.org/wikipedia/en/a/a6/HyderabadDeccanChargers.png",
  "Kochi Tuskers Kerala": "https://upload.wikimedia.org/wikipedia/en/thumb/9/96/Kochi_Tuskers_Kerala_Logo.svg/1280px-Kochi_Tuskers_Kerala_Logo.svg.png",
  "Pune Warriors India": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4a/Pune_Warriors_India_IPL_Logo.png/500px-Pune_Warriors_India_IPL_Logo.png",
  "Delhi Daredevils": "https://upload.wikimedia.org/wikipedia/sa/7/74/298px-Delhi_Daredevils_Logo.svg.png",
  "Kings XI Punjab": "https://1000logos.net/wp-content/uploads/2022/09/Punjab-Kings-Logo-2012.png"
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
      <h1 className="section-title"><span className="text-gradient">Select Franchise</span></h1>
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
