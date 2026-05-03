import { useState, useEffect } from 'react';
import api from '../api';

export default function OnThisDay() {
  const [event, setEvent] = useState(null);
  const [isNearest, setIsNearest] = useState(false);

  useEffect(() => {
    api.get('/static/data/on_this_day.json').then(res => {
      const data = res.data;
      const today = new Date();
      const mm = String(today.getMonth() + 1).padStart(2, '0');
      const dd = String(today.getDate()).padStart(2, '0');
      const todayKey = `${mm}-${dd}`;

      const map = {};
      const tagMap = { birthday: 'Birthday', history: 'History', record: 'Record', final: 'Final Match', semifinal: 'Semi-final' };

      if (Array.isArray(data)) {
        data.forEach(item => {
          if (item.fact != null) map[item.date] = { tag: tagMap[item.category] || 'Did You Know', event: item.fact };
        });
      } else Object.assign(map, data);

      if (map[todayKey]) { setEvent({ date: todayKey, ...map[todayKey] }); }
      else {
        const YEAR = 365.25 * 86400000;
        const cur = new Date(2000, today.getMonth(), today.getDate());
        let nearest = null, min = Infinity;
        for (const k of Object.keys(map)) {
          const [m, d] = k.split('-').map(Number);
          const diff = Math.min(Math.abs(cur - new Date(2000, m - 1, d)), YEAR - Math.abs(cur - new Date(2000, m - 1, d)));
          if (diff < min) { min = diff; nearest = k; }
        }
        if (nearest) { setEvent({ date: nearest, ...map[nearest] }); setIsNearest(true); }
      }
    }).catch(() => {});
  }, []);

  if (!event) return null;

  return (
    <div className="otd-card">
      <span className="otd-tag">{event.tag || 'On This Day in IPL History'}</span>
      {isNearest && (
        <span className="otd-notice">No event for today — showing nearest ({event.date})</span>
      )}
      <p className="otd-body">{event.event}</p>
    </div>
  );
}
