
import Layout from '@/components/Layout';
export default function Home(){
  const base = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8080';
  return (
    <Layout>
      <section className="container" style={{padding:'56px 0'}}>
        <div className="card">
          <h1>Kill spam. Keep the good.</h1>
          <p>Connect your Gmail and try batch classification in shadow mode first.</p>
          <div className="row" style={{marginTop:12}}>
            <a className="btn" href={`${base}/auth/start`}>Connect Gmail</a>
            <a className="btn" href="/app/dashboard" style={{background:'transparent',border:'1px solid var(--bd)',color:'var(--ink)'}}>Open Dashboard</a>
          </div>
        </div>
      </section>
    </Layout>
  )
}
