import { useEffect, useState } from 'react'
import axios from 'axios'

export default function PurpleCap() {
  const [data, setData] = useState([])

  useEffect(() => {
    axios.get('/data/purple_cap.json')
      .then(res => setData(res.data))
  }, [])

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Purple Cap Winners</h2>
      <table border="1" cellPadding="8">
        <thead>
          <tr><th>Season</th><th>Bowler</th><th>Wickets</th></tr>
        </thead>
        <tbody>
          {data.map(row => (
            <tr key={row.season}>
              <td>{row.season}</td>
              <td>{row.bowler}</td>
              <td>{row.wickets}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}