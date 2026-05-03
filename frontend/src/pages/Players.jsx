import { useState, useCallback, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api';
import PlayerSearchBar from '../components/PlayerSearchBar';
import PlayerCard from '../components/PlayerCard';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Players() {
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchParams] = useSearchParams();

  const fetchPlayers = useCallback(async (query) => {
    if (query.trim().length < 2) { setSearchResults([]); setHasSearched(false); return; }
    setLoading(true); setHasSearched(true); setError(null);
    try {
      const r = await api.get(`/api/players?name=${query}`);
      setSearchResults(r.data);
    } catch { setError('Failed to fetch player data.'); }
    finally { setLoading(false); }
  }, []);

  // Support ?q= deep-links from other pages
  useEffect(() => {
    const q = searchParams.get('q');
    if (q) fetchPlayers(q);
  }, [searchParams, fetchPlayers]);

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Player Analytics</h1>
        <p className="page-subtitle">Search career stats for your favourite IPL stars</p>
      </div>

      <PlayerSearchBar onSearch={fetchPlayers} />

      {loading && <LoadingSpinner />}

      {!loading && error && (
        <div className="glass-card" style={{ padding: '1.5rem', color: 'var(--red)', textAlign: 'center' }}>{error}</div>
      )}

      {!loading && hasSearched && searchResults.length === 0 && (
        <div className="empty-state glass-card">
          <h3>No results found</h3>
          <p>Try a different name or spelling</p>
        </div>
      )}

      {!loading && searchResults.length > 0 && (
        <div className="player-grid">
          {searchResults.map(player => <PlayerCard key={player.name} player={player} />)}
        </div>
      )}

      {!loading && !hasSearched && (
        <div className="welcome-state">
          <p>Start typing to discover player career stats</p>
        </div>
      )}
    </div>
  );
}
