import Layout from '../components/Layout';
import ClassificationForm from '../components/ClassificationForm';
import BatchForm from '../components/BatchForm';

export default function Home() {
  return (
    <Layout>
      <section className="hero">
        <div className="container grid">
          <div>
            <h1>Kill spam. Keep the good.</h1>
            <p className="lead">SiftMail is an AI email defense that cleans your inbox with transparent scoring, reversible quarantine, and batch triage tools.</p>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <a className="btn" href="#tester">Try the live classifier</a>
              <a className="btn secondary" href="#learn">Learn more</a>
            </div>
            <div className="kpis">
              <div className="card"><div style={{ fontSize: 28, fontWeight: 800 }}>95%+</div><small>Spam reduction</small></div>
              <div className="card"><div style={{ fontSize: 28, fontWeight: 800 }}>0</div><small>Permanent deletes by default</small></div>
              <div className="card"><div style={{ fontSize: 28, fontWeight: 800 }}>1‑click</div><small>Undo &amp; retrain</small></div>
            </div>
          </div>
          <div className="card">
            <h3 style={{ marginTop: 0 }}>Pipeline snapshot</h3>
            <ul>
              <li>Inbound email hits SiftMail ingress</li>
              <li>Content + URLs scored for risk and phishing signals</li>
              <li>Safe messages delivered; flagged items quarantined</li>
              <li>Explainable verdicts surfaced to the console</li>
            </ul>
            <div className="badges">
              <span className="badge">FastAPI</span>
              <span className="badge">Next.js</span>
              <span className="badge">Batch APIs</span>
              <span className="badge">Transparent scoring</span>
            </div>
          </div>
        </div>
      </section>

      <section className="section" id="tester">
        <div className="container grid" style={{ alignItems: 'start' }}>
          <ClassificationForm />
          <BatchForm />
        </div>
      </section>

      <section className="section" id="learn">
        <div className="container">
          <div className="features">
            <div className="card">
              <h3>Audit‑friendly</h3>
              <p>Each verdict carries an explicit risk score and reasons so security teams can trace decisions.</p>
            </div>
            <div className="card">
              <h3>Batch triage</h3>
              <p>Send multiple messages to the batch endpoint to triage newsletters, auto-replies, and suspicious waves quickly.</p>
            </div>
            <div className="card">
              <h3>Safe defaults</h3>
              <p>No hard deletes. Quarantine + undo makes tuning and rollout safe for production mailboxes.</p>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
}
