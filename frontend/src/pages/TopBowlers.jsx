import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function TopBowlers() {
  const [bowlers, setBowlers] = useState([])
  const [seasons, setSeasons] = useState([])
  const [selected, setSelected] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get('http://localhost:5000/api/seasons')
      .then(res => setSeasons(res.data))
  }, [])

  useEffect(() => {
    setLoading(true)
    axios.get(`http://localhost:5000/api/top-bowlers?season=${selected}`)
      .then(res => {
        setBowlers(res.data)
        setLoading(false)
      })
  }, [selected])

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Top Wicket Takers</h2>

      <select value={selected} onChange={e => setSelected(e.target.value)}>
        <option value="all">All Seasons</option>
        {seasons.map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>

      {loading ? <p>Loading...</p> : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={bowlers}>
            <XAxis dataKey="bowler" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="wickets" fill="#4f98a3" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}