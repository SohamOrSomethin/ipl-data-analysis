import { useState, useCallback, useEffect } from 'react';
import api from '../api';
import PlayerSearchBar from '../components/PlayerSearchBar';
import PlayerCard from '../components/PlayerCard';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Players() {
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  const fetchPlayers = useCallback(async (query) => {
    if (query.trim().length < 2) {
      setSearchResults([]);
      setHasSearched(false);
      return;
    }

    setLoading(true);
    setHasSearched(true);
    setError(null);

    try {
      const response = await api.get(`/api/players?name=${query}`);
      setSearchResults(response.data);
    } catch (err) {
      console.error("Error fetching players:", err);
      setError("Failed to fetch player data. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="players-page">
      <header className="page-header">
        <h1 className="app-title">Player Analytics</h1>
        <p className="app-subtitle">Search career stats for your favorite IPL stars</p>
      </header>

      <PlayerSearchBar onSearch={fetchPlayers} />

      <div className="results-container">
        {loading && <LoadingSpinner />}

        {!loading && error && <div className="error-alert">{error}</div>}

        {!loading && hasSearched && searchResults.length === 0 && (
          <div className="empty-state glass-card">
            <span className="empty-icon">📂</span>
            <h3>No results found</h3>
            <p>We couldn't find any players matching your search.</p>
          </div>
        )}

        {!loading && searchResults.length > 0 && (
          <div className="player-grid">
            {searchResults.map((player) => (
              <PlayerCard key={player.name} player={player} />
            ))}
          </div>
        )}

        {!loading && !hasSearched && (
          <div className="welcome-state">
            <span className="hint-icon">☝️</span>
            <p>Start typing above to discover career performance</p>
          </div>
        )}
      </div>
    </div>
  );
}
