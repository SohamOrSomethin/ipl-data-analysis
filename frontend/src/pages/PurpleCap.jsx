import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function PurpleCap() {
  const [data, setData] = useState([])

  useEffect(() => {
    fetch('http://localhost:5000/api/purple-cap')
      .then(res => res.json())
      .then(data => setData(data))
  }, [])

  return (
    <div className="dashboard-content">
      <h1 className="section-title" style={{ background: 'none', WebkitTextFillColor: 'initial', color: 'var(--accent-purple)' }}>
        🎯 Purple Cap Winners
      </h1>
      
      <div className="glass-card chart-card mb-4" style={{ marginBottom: '2rem' }}>
        <h2 className="card-title">Wickets by Season</h2>
        <div style={{ width: '100%', height: 350 }}>
          <ResponsiveContainer>
             <BarChart data={data}>
               <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false}/>
               <XAxis dataKey="season" stroke="#94a3b8" />
               <YAxis stroke="#94a3b8" />
               <Tooltip 
                 contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} 
                 labelStyle={{ color: '#8b5cf6' }}
                 formatter={(value, name, props) => [value, `${props.payload.bowler} (${props.payload.team})`]} 
               />
               <Bar dataKey="wickets" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
             </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-card">
        <div className="table-container">
          <table>
            <thead>
              <tr><th>Season</th><th>Bowler Name</th><th>Total Wickets</th><th>Team</th></tr>
            </thead>
            <tbody>
              {data.map(row => (
                <tr key={row.season}>
                  <td>{row.season}</td>
                  <td>{row.bowler}</td>
                  <td style={{ color: '#8b5cf6', fontWeight: 'bold' }}>{row.wickets}</td>
                  <td>{row.team}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}