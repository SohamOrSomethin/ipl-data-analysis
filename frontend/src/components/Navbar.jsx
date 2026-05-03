import { NavLink } from 'react-router-dom';
import { useState, useEffect } from 'react';

const SunIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="4"/>
    <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
  </svg>
);
const MoonIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
  </svg>
);

const NAV = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/orange-cap', label: 'Orange Cap' },
  { to: '/purple-cap', label: 'Purple Cap' },
  { to: '/players', label: 'Players' },
  { to: '/teams', label: 'Teams' },
  { to: '/head-to-head', label: 'Head to Head' },
  { to: '/record-card', label: 'Records' },
  { to: '/daily-quiz', label: 'Daily Quiz' },
  { to: '/goat-players', label: 'G.O.A.T' },
];

export default function Navbar() {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    if (saved) return saved === 'dark';
    return true; // default dark
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  return (
    <nav className="glass-nav">
      <div className="nav-container">
        <NavLink to="/" className="nav-logo">
          IPL Analytics
        </NavLink>

        <div className="nav-links">
          {NAV.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            >
              {label}
            </NavLink>
          ))}
        </div>

        <button
          className="theme-toggle"
          onClick={() => setIsDark(d => !d)}
          aria-label="Toggle theme"
          title="Toggle light / dark mode"
        >
          {isDark ? <SunIcon /> : <MoonIcon />}
        </button>
      </div>
    </nav>
  );
}
