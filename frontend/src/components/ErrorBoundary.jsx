import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Dashboard Error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="glass-card error-fallback">
          <div className="error-icon">⚠️</div>
          <h2 className="error-title">Data Load Error</h2>
          <p className="error-message">
            We couldn't load this section. This might be due to a missing data file or network issue.
          </p>
          <button 
            className="premium-button"
            onClick={() => window.location.reload()}
          >
            Retry Dashboard
          </button>
        </div>
      );
    }

    return this.props.children; 
  }
}

export default ErrorBoundary;



