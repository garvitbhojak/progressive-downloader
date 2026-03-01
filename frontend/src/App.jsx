import { useState } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [metadata, setMetadata] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError('');
    setMetadata(null);
    setIsStreaming(false);

    try {
      const response = await fetch('http://localhost:8000/analyze-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze URL or invalid URL format');
      }

      const data = await response.json();
      setMetadata(data);
    } catch (err) {
      setError(err.message || 'An error occurred during analysis by the server.');
    } finally {
      setLoading(false);
    }
  };

  const handlePlay = () => {
    setIsStreaming(true);
  };

  const formatSize = (bytes) => {
    if (!bytes) return 'Unknown size';
    const mbs = (bytes / (1024 * 1024)).toFixed(2);
    return `${mbs} MB`;
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Progressive Downloader</h1>
      </header>

      <main className="app-main">
        <form className="url-form" onSubmit={handleAnalyze}>
          <input
            type="url"
            className="url-input"
            placeholder="Paste your video URL here..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
            disabled={loading}
          />
          <button type="submit" className="btn analyze-button" disabled={loading || !url.trim()}>
            {loading ? 'Analyzing...' : 'Analyze Link'}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        {metadata && !isStreaming && (
          <div className="metadata-section">
            <div className="metadata-card">
              <h2>Video Information</h2>
              <div className="metadata-details">
                <div className="metadata-row">
                  <span className="metadata-label">Format</span>
                  <span className="metadata-value">{metadata['Content-Type'] || 'Unknown'}</span>
                </div>
                <div className="metadata-row">
                  <span className="metadata-label">Size</span>
                  <span className="metadata-value">{formatSize(metadata['Content-Length'])}</span>
                </div>
                <div className="metadata-row">
                  <span className="metadata-label">Range Support</span>
                  <span className="metadata-value">{metadata.supports_range ? 'Yes (Seekable)' : 'No'}</span>
                </div>
              </div>
            </div>
            <button className="btn play-button" onClick={handlePlay}>
              Watch & Download
            </button>
          </div>
        )}

        {isStreaming && (
          <div className="video-section">
            <video
              className="video-player"
              controls
              autoPlay
              src={`http://localhost:8000/stream?url=${encodeURIComponent(url)}`}
            >
              Your browser does not support the video tag.
            </video>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
