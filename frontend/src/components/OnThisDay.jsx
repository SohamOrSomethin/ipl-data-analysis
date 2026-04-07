import React, { useState, useEffect } from 'react';

const API = 'http://localhost:5000';

function getNearestDateKey(dataMap, currentMonth, currentDay) {
  const current = new Date(2000, currentMonth - 1, currentDay);
  let nearest = null;
  let minDiff = Infinity;
  const YEAR_MS = 365.25 * 24 * 60 * 60 * 1000;

  for (const key of Object.keys(dataMap)) {
    const [m, d] = key.split('-').map(Number);
    const date1 = new Date(2000, m - 1, d);
    let diff = Math.abs(current - date1);
    diff = Math.min(diff, Math.abs(YEAR_MS - diff));
    if (diff < minDiff) {
      minDiff = diff;
      nearest = key;
    }
  }
  return nearest;
}

export default function OnThisDay() {
  const [eventData, setEventData] = useState(null);
  const [isNearest, setIsNearest] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/static/data/on_this_day.json`)
      .then(res => res.json())
      .then(data => {
        const today = new Date();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        const todayKey = `${mm}-${dd}`;

        if (data[todayKey]) {
          setEventData({ date: todayKey, ...data[todayKey] });
          setIsNearest(false);
        } else {
          const nearestKey = getNearestDateKey(data, today.getMonth() + 1, today.getDate());
          if (nearestKey) {
            setEventData({ date: nearestKey, ...data[nearestKey] });
            setIsNearest(true);
          }
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load on-this-day events", err);
        setLoading(false);
      });
  }, []);

  if (loading || !eventData) return null;

  return (
    <div className="glass-card" style={{ marginBottom: '2rem', position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', background: 'linear-gradient(to bottom, var(--accent-cyan), var(--accent-purple))' }}></div>
      <div style={{ padding: '0.5rem 0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
          <span style={{ fontSize: '1.5rem' }}>🗓️</span>
          <h2 className="card-title" style={{ margin: 0, fontSize: '1.4rem' }}>On This Day in IPL History</h2>
        </div>
        
        {isNearest && (
          <div style={{ fontSize: '0.85rem', color: '#f59e0b', marginBottom: '1rem', fontStyle: 'italic', background: 'rgba(245, 158, 11, 0.1)', padding: '0.5rem 1rem', borderRadius: '4px' }}>
            No event matches today's exact date. Showing the nearest historical event ({eventData.date}):
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <div style={{ color: 'var(--accent-cyan)', fontWeight: 700, fontSize: '1.4rem' }}>
            {eventData.year}
          </div>
          <div style={{ fontSize: '1.1rem', lineHeight: 1.6, color: 'var(--text-main)', marginTop: '0.25rem' }}>
            {eventData.event}
          </div>
        </div>
      </div>
    </div>
  );
}
