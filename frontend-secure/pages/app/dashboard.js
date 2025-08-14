
import { useState } from 'react';
import Layout from '@/components/Layout';
import { apiGet, apiPost } from '@/components/useApi';

export default function Dashboard(){
  const [email, setEmail] = useState('');
  const [shadow, setShadow] = useState(true);
  const [batchResult, setBatchResult] = useState(null);
  const [rules, setRules] = useState({allow:[], block:[]});
  const [allowEntry, setAllowEntry] = useState('');
  const [blockEntry, setBlockEntry] = useState('');
  const [digest, setDigest] = useState([]);
  const [audit, setAudit] = useState([]);
  const [loading, setLoading] = useState(false);
  const [label, setLabel] = useState('INBOX');
  const [threshold, setThreshold] = useState(0.7);
  const [maxResults, setMaxResults] = useState(25);

  async function loadMode(){
    const m = await apiGet(`mode?email=${encodeURIComponent(email)}`);
    setShadow(!!m.shadow);
  }
  async function saveMode(v){
    const r = await apiPost('mode', { email, shadow: v });
    setShadow(r.shadow);
  }
  async function loadRules(){
    const r = await apiGet(`rules?email=${encodeURIComponent(email)}`);
    setRules(r);
  }
  async function addAllow(){
    if(!allowEntry) return;
    const r = await apiPost('rules/allow', { email, entries: [allowEntry] });
    setRules(r); setAllowEntry('');
  }
  async function addBlock(){
    if(!blockEntry) return;
    const r = await apiPost('rules/block', { email, entries: [blockEntry] });
    setRules(r); setBlockEntry('');
  }
  async function runBatch(dry=true){
    setLoading(true);
    try{
      const r = await apiPost('gmail/batch-classify', {
        email, label, max_results: Number(maxResults), quarantine_threshold: Number(threshold), dry_run: dry
      });
      setBatchResult(r);
    }catch(e){ alert(e.message); }
    setLoading(false);
  }
  async function loadDigest(){
    const r = await apiGet(`digest?email=${encodeURIComponent(email)}`);
    setDigest(r.items || []);
  }
  async function loadAudit(){
    const r = await apiGet(`audit?email=${encodeURIComponent(email)}&limit=100`);
    setAudit(r.items || []);
  }

  return (
    <Layout>
      <section className="container" style={{padding:'36px 0'}}>
        <div className="card">
          <div className="row">
            <input className="input" placeholder="you@domain.com" value={email} onChange={e=>setEmail(e.target.value)} style={{minWidth:280}}/>
            <button className="btn" onClick={loadMode}>Load Mode</button>
            <span className="badge">Shadow: {String(shadow)}</span>
            <button className="btn" onClick={()=>saveMode(!shadow)}>{shadow ? 'Turn OFF (act)' : 'Turn ON (safe)'}</button>
          </div>
        </div>

        <div className="grid" style={{marginTop:20}}>
          <div className="card">
            <h3>Allow / Block</h3>
            <div className="row">
              <input className="input" placeholder="@trusted.com or ceo@acme.com" value={allowEntry} onChange={e=>setAllowEntry(e.target.value)} />
              <button className="btn" onClick={addAllow}>Add Allow</button>
            </div>
            <div className="row" style={{marginTop:8}}>
              <input className="input" placeholder="@shady.tld or spam@foo.xyz" value={blockEntry} onChange={e=>setBlockEntry(e.target.value)} />
              <button className="btn" onClick={addBlock}>Add Block</button>
              <button className="btn" onClick={loadRules} style={{background:'transparent',border:'1px solid var(--bd)',color:'var(--ink)'}}>Refresh</button>
            </div>
            <div style={{marginTop:10}}>
              <small className="muted">Allow: {rules.allow?.join(', ') || '—'}</small><br/>
              <small className="muted">Block: {rules.block?.join(', ') || '—'}</small>
            </div>
          </div>

          <div className="card">
            <h3>Batch Classify</h3>
            <div className="row">
              <label>Label:</label>
              <input className="input" value={label} onChange={e=>setLabel(e.target.value)} style={{width:140}}/>
              <label>Max:</label>
              <input className="input" type="number" value={maxResults} onChange={e=>setMaxResults(e.target.value)} style={{width:90}}/>
              <label>Threshold:</label>
              <input className="input" type="number" step="0.05" value={threshold} onChange={e=>setThreshold(e.target.value)} style={{width:110}}/>
            </div>
            <div className="row" style={{marginTop:10}}>
              <button className="btn" disabled={loading} onClick={()=>runBatch(true)}>{loading?'Running…':'Dry Run'}</button>
              <button className="btn" disabled={loading} onClick={()=>runBatch(false)}>{loading?'Running…':'Apply (if Shadow OFF)'}</button>
            </div>
            {batchResult && (
              <div style={{marginTop:12}}>
                <div className="row"><span className="badge">Count: {batchResult.count}</span><span className="badge">Dry: {String(batchResult.dry_run)}</span></div>
                <table style={{marginTop:8}}>
                  <thead><tr><th>ID</th><th>Score</th><th>Reasons</th><th>Action</th></tr></thead>
                  <tbody>
                    {batchResult.items.map((it)=>(
                      <tr key={it.id}><td>{it.id}</td><td>{it.score}</td><td>{(it.reasons||[]).join(', ')}</td><td>{it.action}</td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        <div className="grid" style={{marginTop:20}}>
          <div className="card">
            <h3>Digest (Quarantine)</h3>
            <button className="btn" onClick={loadDigest}>Refresh Digest</button>
            <table style={{marginTop:10}}>
              <thead><tr><th>From</th><th>Subject</th><th>Date</th><th>Snippet</th></tr></thead>
              <tbody>
                {digest.map((d)=> <tr key={d.id}><td>{d.from}</td><td>{d.subject}</td><td>{d.date}</td><td>{d.snippet}</td></tr>)}
              </tbody>
            </table>
          </div>
          <div className="card">
            <h3>Audit Log</h3>
            <button className="btn" onClick={loadAudit}>Refresh Audit</button>
            <table style={{marginTop:10}}>
              <thead><tr><th>Time</th><th>Event</th><th>Message</th><th>Score</th></tr></thead>
              <tbody>
                {audit.map((a,i)=> <tr key={i}><td>{new Date((a.ts||0)*1000).toLocaleString()}</td><td>{a.event}</td><td>{a.id||'—'}</td><td>{a.score||'—'}</td></tr>)}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </Layout>
  )
}
