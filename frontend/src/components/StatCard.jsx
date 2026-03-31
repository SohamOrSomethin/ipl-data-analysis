export default function StatCard({ title, value, subtitle, icon, accentColor = "#D85A30" }) {
  const lightBg = accentColor + "22"; // ~13% opacity tint

  return (
    <div style={{
      background: "white",
      border: "0.5px solid #e0e0e0",
      borderRadius: "12px",
      borderLeft: `3px solid ${accentColor}`,
      padding: "1.1rem 1.25rem",
      position: "relative",
      overflow: "hidden",
    }}>
      {icon && (
        <div style={{
          position: "absolute", top: 0, right: 0,
          width: "48px", height: "48px",
          background: lightBg,
          borderRadius: "0 12px 0 50%",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: "18px",
        }}>
          {icon}
        </div>
      )}

      <p style={{ fontSize: "11px", fontWeight: 500, color: "#888", textTransform: "uppercase", letterSpacing: "0.06em", margin: "0 0 6px" }}>
        {title}
      </p>
      <p style={{ fontSize: "26px", fontWeight: 500, color: "#111", margin: "0 0 4px", lineHeight: 1.1 }}>
        {value}
      </p>
      {subtitle && (
        <p style={{ fontSize: "12px", color: "#888", margin: 0 }}>
          {subtitle}
        </p>
      )}
    </div>
  );
}