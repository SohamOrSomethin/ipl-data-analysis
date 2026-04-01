import { useEffect, useState } from 'react'
import axios from 'axios'

export default function PurpleCap() {
  const [data, setData] = useState([])

  useEffect(() => {
    axios.get('/data/purple_cap.json')
      .then(res => setData(res.data))
  }, [])

  return (
    <div className="glass-card">
      <h2 className="card-title">🎯 Purple Cap Winners</h2>
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
                <td>{row.wickets}</td>
                <td>{row.team}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}