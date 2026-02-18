import { useEffect, useState } from 'react';
import Layout from '../../components/Layout';
import { fetchHealth } from '../../lib/api';

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch((err) => setError(err.message || 'Unable to reach backend'));
  }, []);

  return (
    <Layout>
      <section className="section">
        <div className="container">
          <h1 style={{ marginTop: 0 }}>Operations console</h1>
          <p className="lead">Monitor the API and verify the connection between the frontend and backend.</p>
          {error && <div className="alert warning">{error}</div>}
          {health && (
            <div className="card" style={{ maxWidth: 420 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span>Status</span>
                <strong style={{ color: '#2dd4bf' }}>{health.status}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span>Environment</span>
                <strong>{health.environment}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>App</span>
                <strong>{health.app}</strong>
              </div>
            </div>
          )}
        </div>
      </section>
    </Layout>
  );
}
