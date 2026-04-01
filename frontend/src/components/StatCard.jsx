export default function StatCard({ title, value, subtitle, icon, accentColor = "var(--accent-cyan)" }) {
  return (
    <div className="stat-card" style={{ '--accent': accentColor }}>
      {icon && (
        <div className="stat-icon-wrapper">
          {icon}
        </div>
      )}
      <div className="stat-content">
        <p className="stat-title">{title}</p>
        <p className="stat-value">{value}</p>
        {subtitle && <p className="stat-subtitle">{subtitle}</p>}
      </div>
      <div className="stat-accent-bar"></div>
    </div>
  );
}