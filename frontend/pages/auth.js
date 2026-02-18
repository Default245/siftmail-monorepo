import Layout from '../components/Layout';

export default function Auth() {
  return (
    <Layout>
      <section className="section">
        <div className="container">
          <h1 style={{ marginTop: 0 }}>Authentication</h1>
          <p className="lead">SiftMail uses backend-issued sessions or API keys. Plug your own identity provider on top.</p>
          <div className="card">
            <ol>
              <li>Generate an API key or session token on the backend (see docs/operations.md).</li>
              <li>Store the token securely on the client (ENV: <code>NEXT_PUBLIC_API_BASE_URL</code> points to your backend).</li>
              <li>Attach <code>Authorization: Bearer &lt;token&gt;</code> headers when calling private routes.</li>
            </ol>
            <p className="muted">For the demo build, the endpoints are open for easier evaluation. Lock them down before production.</p>
          </div>
        </div>
      </section>
    </Layout>
  );
}
