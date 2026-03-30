import { useEffect, useState } from 'react'
import axios from 'axios'

export default function OrangeCap() {
  const [data, setData] = useState([])

  useEffect(() => {
    axios.get('/data/orange_cap.json')
      .then(res => setData(res.data))
  }, [])

  return (
    <div className="glass-card">
      <h2 className="card-title">Orange Cap Winners</h2>
      <div className="table-container">
        <table>
          <thead>
            <tr><th>Season</th><th>Batter</th><th>Runs</th></tr>
          </thead>
          <tbody>
            {data.map(row => (
              <tr key={row.season}>
                <td>{row.season}</td>
                <td>{row.batter}</td>
                <td>{row.runs}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}