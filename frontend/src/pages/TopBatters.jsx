import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function TopBatters() {
  const [batters, setBatters] = useState([])
  const [seasons, setSeasons] = useState([])
  const [selected, setSelected] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get('/data/seasons.json')
      .then(res => setSeasons(res.data))
  }, [])

  useEffect(() => {
    setLoading(true)
    if (selected === 'all') {
      axios.get('/data/players.json').then(res => {
        const top10 = res.data
          .sort((a, b) => b.runs - a.runs)
          .slice(0, 10)
          .map(p => ({ batter: p.name, runs: p.runs }))
        setBatters(top10)
        setLoading(false)
      })
    } else {
      axios.get(`http://localhost:5000/api/top-batters?season=${selected}`)
        .then(res => {
          setBatters(res.data)
          setLoading(false)
        })
    }
  }, [selected])

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Top Run Scorers</h2>

      <select value={selected} onChange={e => setSelected(e.target.value)}>
        <option value="all">All Seasons</option>
        {seasons.map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>

      {loading ? <p>Loading...</p> : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={batters}>
            <XAxis dataKey="batter" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="runs" fill="#4f98a3" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}