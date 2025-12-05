import { useState } from 'react';
import { classifyMessage } from '../lib/api';

const initialState = {
  subject: '',
  body: '',
  sender: '',
  recipient: '',
  urls: '',
  attachments: '',
};

export default function ClassificationForm() {
  const [form, setForm] = useState(initialState);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setError('');
    setResult(null);
    try {
      const payload = {
        subject: form.subject,
        body: form.body,
        sender: form.sender,
        recipient: form.recipient,
        urls: form.urls ? form.urls.split(',').map((item) => item.trim()).filter(Boolean) : [],
        attachments: form.attachments ? form.attachments.split(',').map((item) => item.trim()).filter(Boolean) : [],
      };
      const response = await classifyMessage(payload);
      setResult(response);
    } catch (err) {
      setError(err.message || 'Unable to classify message');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 style={{ marginTop: 0 }}>Test a message</h2>
      <p className="muted">Send a sample email payload to the backend classifier. Nothing is stored.</p>
      <form onSubmit={handleSubmit} className="form-grid">
        <div>
          <label htmlFor="subject">Subject</label>
          <input id="subject" name="subject" value={form.subject} onChange={handleChange} placeholder="Wire transfer reminder" required />
        </div>
        <div>
          <label htmlFor="sender">Sender</label>
          <input id="sender" name="sender" type="email" value={form.sender} onChange={handleChange} placeholder="alerts@example.com" required />
        </div>
        <div>
          <label htmlFor="recipient">Recipient</label>
          <input id="recipient" name="recipient" type="email" value={form.recipient} onChange={handleChange} placeholder="you@example.com" required />
        </div>
        <div style={{ gridColumn: '1 / -1' }}>
          <label htmlFor="body">Body</label>
          <textarea id="body" name="body" value={form.body} onChange={handleChange} placeholder="Write the email content here" required />
        </div>
        <div>
          <label htmlFor="urls">Links (comma-separated)</label>
          <input id="urls" name="urls" value={form.urls} onChange={handleChange} placeholder="https://dodgy-payments.io/pay" />
        </div>
        <div>
          <label htmlFor="attachments">Attachments (comma-separated filenames)</label>
          <input id="attachments" name="attachments" value={form.attachments} onChange={handleChange} placeholder="invoice.pdf, details.docx" />
        </div>
        <div style={{ gridColumn: '1 / -1', display: 'flex', gap: 12, alignItems: 'center' }}>
          <button className="btn" type="submit" disabled={isLoading}>{isLoading ? 'Classifying…' : 'Classify message'}</button>
          <button className="btn secondary inline" type="button" onClick={() => setForm(initialState)}>Reset</button>
        </div>
      </form>
      {error && <div className="alert warning">{error}</div>}
      {result && (
        <div className="alert" style={{ marginTop: 16 }}>
          <strong style={{ textTransform: 'uppercase' }}>{result.verdict}</strong>
          <div>Risk score: {result.risk_score}</div>
          <div className="muted" style={{ marginTop: 8 }}>Reasons:</div>
          <ul>
            {result.reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
