
import { useState } from 'react';
import Layout from '@/components/Layout';
import { apiGet } from '@/components/useApi';

export default function Audit(){
  const [email, setEmail] = useState('');
  const [items, setItems] = useState([]);

  async function load(){
    const r = await apiGet(`audit?email=${encodeURIComponent(email)}&limit=200`);
    setItems(r.items || []);
  }

  return (
    <Layout>
      <section className="container" style={{padding:'36px 0'}}>
        <div className="card">
          <div className="row">
            <input className="input" placeholder="you@domain.com" value={email} onChange={e=>setEmail(e.target.value)} style={{minWidth:280}}/>
            <button className="btn" onClick={load}>Refresh</button>
          </div>
        </div>

        <div className="card" style={{marginTop:16}}>
          <table>
            <thead><tr><th>Time</th><th>Event</th><th>Message</th><th>Score</th></tr></thead>
            <tbody>
              {items.map((a,i)=>(
                <tr key={i}>
                  <td>{new Date((a.ts||0)*1000).toLocaleString()}</td>
                  <td>{a.event}</td>
                  <td>{a.id || '—'}</td>
                  <td>{a.score || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </Layout>
  )
}
