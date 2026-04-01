import { useState, useEffect } from 'react';

export default function PlayerSearchBar({ onSearch }) {
  const [query, setQuery] = useState('');

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      onSearch(query);
    }, 500); // 500ms debounce

    return () => clearTimeout(delayDebounceFn);
  }, [query, onSearch]);

  return (
    <div className="search-wrapper">
      <div className="search-input-group">
        <span className="search-icon">🔍</span>
        <input
          type="text"
          className="premium-input"
          placeholder="Search players (e.g. Virat Kohli, MS Dhoni)..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        {query && (
          <button className="clear-btn" onClick={() => setQuery('')}>
            ✕
          </button>
        )}
      </div>
      <p className="search-hint">Enter at least 2 characters to start searching</p>
    </div>
  );
}
