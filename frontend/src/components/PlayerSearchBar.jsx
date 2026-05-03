import { useState } from 'react';

export default function PlayerSearchBar({ onSearch }) {
  const [query, setQuery] = useState('');

  const handleChange = (val) => {
    setQuery(val);
    clearTimeout(window._psb);
    window._psb = setTimeout(() => onSearch(val), 400);
  };

  return (
    <div className="search-wrapper">
      <div className="search-input-group">
        <span className="search-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
        </span>
        <input
          type="text"
          className="premium-input"
          placeholder="Search players — e.g. Virat Kohli, MS Dhoni..."
          value={query}
          onChange={e => handleChange(e.target.value)}
        />
        {query && (
          <button className="clear-btn" onClick={() => handleChange('')} aria-label="Clear">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        )}
      </div>
      <p className="search-hint">Type at least 2 characters to search</p>
    </div>
  );
}
