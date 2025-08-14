
import { useState } from 'react';
import Layout from '@/components/Layout';
import { apiGet, apiPost } from '@/components/useApi';

export default function Dashboard(){
  const [email, setEmail] = useState('');
  const [shadow, setShadow] = useState(true);
  const [batchResult, setBatchResult] = useState(null);

  async function loadMode(){ const m = await apiGet(`mode?email=${encodeURIComponent(email)}`); setShadow(!!m.shadow); }
  async function saveMode(v){ const r = await apiPost('mode', { email, shadow: v }); setShadow(r.shadow); }
  async function runBatch(dry=true){
    const r = await apiPost('gmail/batch-classify', { email, label: 'INBOX', max_results: 25, quarantine_threshold: 0.7, dry_run: dry });
    setBatchResult(r);
  }

  return (
    <Layout>
      <section className="container" style={{padding:'36px 0'}}>
        <div className="card">
          <div className="row">
            <input className="input" placeholder="you@domain.com" value={email} onChange={e=>setEmail(e.target.value)} style={{minWidth:280}}/>
            <button className="btn" onClick={loadMode}>Load Mode</button>
            <span className="btn" onClick={()=>saveMode(!shadow)} style={{background:'transparent',border:'1px solid var(--bd)',color:'var(--ink)'}}>
              Shadow: {String(shadow)} (toggle)
            </span>
            <button className="btn" onClick={()=>runBatch(true)}>Dry Run</button>
            <button className="btn" onClick={()=>runBatch(false)}>Apply</button>
          </div>
        </div>
        {batchResult && (
          <div className="card" style={{marginTop:16}}>
            <h3>Batch Result</h3>
            <table><thead><tr><th>ID</th><th>Score</th><th>Action</th></tr></thead>
              <tbody>{batchResult.items.map(it=>(<tr key={it.id}><td>{it.id}</td><td>{it.score}</td><td>{it.action}</td></tr>))}</tbody>
            </table>
          </div>
        )}
      </section>
    </Layout>
  )
}
