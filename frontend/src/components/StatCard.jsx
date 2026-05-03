export default function StatCard({ title, value, subtitle, icon, accentColor = "var(--blue)" }) {
  return (
    <div className="stat-card" style={{ '--accent': accentColor }}>
      {icon && <div className="stat-icon-wrapper">{icon}</div>}
      <p className="stat-title">{title}</p>
      <p className="stat-value">{value}</p>
      {subtitle && <p className="stat-subtitle">{subtitle}</p>}
    </div>
  );
}
