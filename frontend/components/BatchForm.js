import { useState } from 'react';
import { classifyBatch } from '../lib/api';

const template = [
  {
    subject: 'Password reset needed',
    body: 'Use the secure portal to update your password today.',
    sender: 'security@example.com',
    recipient: 'you@example.com',
    urls: ['https://example.com/reset'],
    attachments: [],
  },
];

export default function BatchForm() {
  const [messagesJson, setMessagesJson] = useState(JSON.stringify(template, null, 2));
  const [submitted, setSubmitted] = useState(template);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      const parsed = JSON.parse(messagesJson);
      if (!Array.isArray(parsed)) {
        throw new Error('Payload must be an array of messages');
      }
      const response = await classifyBatch({ messages: parsed });
      setResults(response.results);
      setSubmitted(parsed);
    } catch (err) {
      setError(err.message || 'Unable to run batch classification');
      setResults(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 style={{ marginTop: 0 }}>Batch classify (JSON)</h2>
      <p className="muted">Paste a JSON array of messages to classify multiple items at once.</p>
      <form onSubmit={handleSubmit}>
        <textarea value={messagesJson} onChange={(e) => setMessagesJson(e.target.value)} aria-label="Messages JSON" />
        <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
          <button className="btn" type="submit" disabled={isLoading}>{isLoading ? 'Classifying…' : 'Run batch'}</button>
          <button className="btn secondary inline" type="button" onClick={() => { setMessagesJson(JSON.stringify(template, null, 2)); setSubmitted(template); }}>Reset sample</button>
        </div>
      </form>
      {error && <div className="alert warning">{error}</div>}
      {results && (
        <div style={{ marginTop: 16 }}>
          <table className="table">
            <thead>
              <tr>
                <th>Subject</th>
                <th>Sender</th>
                <th>Verdict</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {results.map((item, index) => (
                <tr key={`${item.verdict}-${index}`}>
                  <td>{submitted[index]?.subject || `Message ${index + 1}`}</td>
                  <td>{submitted[index]?.sender || ''}</td>
                  <td style={{ textTransform: 'uppercase' }}>{item.verdict}</td>
                  <td>{item.risk_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
