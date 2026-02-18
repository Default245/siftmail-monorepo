import Layout from '../components/Layout';

export default function DataPolicy() {
  return (
    <Layout>
      <section className="section">
        <div className="container">
          <div className="card">
            <h1 style={{ marginTop: 0 }}>Data Policy</h1>
            <p className="muted">We collect the minimum required to run the service. You can request export or deletion any time.</p>
            <ul>
              <li>Account info (email + display name)</li>
              <li>OAuth tokens under your consent</li>
              <li>Product settings and usage metadata</li>
            </ul>
          </div>
        </div>
      </section>
    </Layout>
  );
}
