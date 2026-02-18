import Layout from '../components/Layout';

export default function Terms() {
  return (
    <Layout>
      <section className="section">
        <div className="container">
          <div className="card">
            <h1 style={{ marginTop: 0 }}>Terms of Service</h1>
            <p className="muted">Straightforward rules so you can evaluate SiftMail quickly.</p>
            <ul>
              <li>Use the service responsibly and do not probe, abuse, or attack mailboxes you do not control.</li>
              <li>Send accurate contact info when requesting access; we revoke access for fraud or abuse.</li>
              <li>Early users may experience breaking changes, but we announce them in advance.</li>
              <li>We will never sell your data; you may request export or deletion at any time.</li>
            </ul>
          </div>
        </div>
      </section>
    </Layout>
  );
}
