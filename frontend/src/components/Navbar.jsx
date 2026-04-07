import { NavLink } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="glass-nav">
      <div className="nav-container">
        <NavLink to="/" className="nav-logo">
          <span className="logo-icon">🏏</span>
          IPL Analytics
        </NavLink>
        <div className="nav-links">
          <NavLink 
            to="/" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            end
          >
            Dashboard
          </NavLink>
          <NavLink 
            to="/orange-cap" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            Orange Cap
          </NavLink>
          <NavLink 
            to="/purple-cap" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            Purple Cap
          </NavLink>
          <NavLink 
            to="/players" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            Players
          </NavLink>
          <NavLink 
            to="/teams" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            Teams
          </NavLink>
          <NavLink 
            to="/head-to-head" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            H2H
          </NavLink>
          <NavLink 
            to="/record-card" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            Record Card
          </NavLink>
          <NavLink 
            to="/daily-quiz" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            style={{ color: 'var(--accent-gold)' }}
          >
            Daily Quiz 🧠
          </NavLink>
        </div>
      </div>
    </nav>
  );
}
