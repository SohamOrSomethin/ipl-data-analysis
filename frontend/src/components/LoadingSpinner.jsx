export default function LoadingSpinner() {
  return (
    <div className="spinner-container">
      <div className="spinner">
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-core">🏏</div>
      </div>
      <p className="loading-text">Fetching match data...</p>
    </div>
  );
}
