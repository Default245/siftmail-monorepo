
import Layout from '@/components/Layout';

export default function Home(){
  const startAuth = () => {
    // OAuth endpoints are open; we hit backend directly (no API key needed)
    const base = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8080';
    window.location.href = `${base}/auth/start`;
  };
  return (
    <Layout>
      <section className="container" style={{padding:'56px 0'}}>
        <div className="grid">
          <div>
            <h1>Kill spam. Keep the good.</h1>
            <p className="badge">Secure API proxy + API key</p>
            <p className="muted">Connect Gmail, run batch classify in Shadow Mode, then flip the switch to quarantine for real.</p>
            <div className="row" style={{marginTop:12}}>
              <button className="btn" onClick={startAuth}>Connect Gmail</button>
              <a className="btn" href="/app/dashboard" style={{background:'transparent',border:'1px solid var(--bd)',color:'var(--ink)'}}>Open Dashboard</a>
            </div>
          </div>
          <div className="card">
            <h3>How it works</h3>
            <ol>
              <li>Click <b>Connect Gmail</b> and finish Google consent.</li>
              <li>Open <b>Dashboard</b>, enter your email, keep <b>Shadow Mode</b> ON.</li>
              <li>Run <b>Batch Classify</b> (dry run) to see what would be quarantined.</li>
              <li>Turn <b>Shadow Mode</b> OFF to actually move mail.</li>
            </ol>
          </div>
        </div>
      </section>
    </Layout>
  )
}
