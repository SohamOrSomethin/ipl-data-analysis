import { useEffect, useState } from 'react'
import axios from 'axios'

export default function OrangeCap() {
  const [data, setData] = useState([])

  useEffect(() => {
    axios.get('http://localhost:5000/api/orange-cap')
      .then(res => setData(res.data))
  }, [])

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Orange Cap Winners</h2>
      <table border="1" cellPadding="8">
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
  )
}