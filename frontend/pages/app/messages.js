import Layout from '../../components/Layout';

const sampleMessages = [
  { subject: 'Security review', verdict: 'clean', score: 0.1, reason: 'No risky markers detected' },
  { subject: 'Urgent wire transfer', verdict: 'spam', score: 0.92, reason: 'Spam keywords + suspicious domain' },
  { subject: 'Weekly newsletter', verdict: 'suspicious', score: 0.61, reason: 'Bulk sender detected' },
];

export default function MessagesPage() {
  return (
    <Layout>
      <section className="section">
        <div className="container">
          <h1 style={{ marginTop: 0 }}>Recent verdicts</h1>
          <p className="lead">Use this view to validate that the classifier is making explainable decisions.</p>
          <div className="card">
            <table className="table">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Verdict</th>
                  <th>Risk score</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {sampleMessages.map((message) => (
                  <tr key={message.subject}>
                    <td>{message.subject}</td>
                    <td style={{ textTransform: 'uppercase' }}>{message.verdict}</td>
                    <td>{message.score}</td>
                    <td>{message.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </Layout>
  );
}
