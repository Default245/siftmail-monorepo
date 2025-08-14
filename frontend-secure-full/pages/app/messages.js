
import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import { apiGet, apiPost } from '@/components/useApi';

export default function Messages(){
  const [email, setEmail] = useState('');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  async function load(){
    setLoading(true);
    try{
      const r = await apiGet(`messages/recent?email=${encodeURIComponent(email)}&label=INBOX&max_results=50`);
      setItems(r.items || []);
    }catch(e){ alert(e.message); }
    setLoading(false);
  }

  async function act(id, action){
    try{
      const r = await apiPost('messages/action', { email, message_id: id, action });
      alert(`Action: ${r.action || r.ok}`);
      load();
    }catch(e){ alert(e.message); }
  }

  return (
    <Layout>
      <section className="container" style={{padding:'36px 0'}}>
        <div className="card">
          <div className="row">
            <input className="input" placeholder="you@domain.com" value={email} onChange={e=>setEmail(e.target.value)} style={{minWidth:280}}/>
            <button className="btn" onClick={load} disabled={loading}>{loading?'Loading…':'Load Messages'}</button>
          </div>
        </div>

        <div className="card" style={{marginTop:16}}>
          <table>
            <thead><tr><th>From</th><th>Subject</th><th>Date</th><th>Score</th><th>Actions</th></tr></thead>
            <tbody>
              {items.map(m => (
                <tr key={m.id}>
                  <td>{m.from}</td>
                  <td>{m.subject}</td>
                  <td>{m.date}</td>
                  <td>{m.score}</td>
                  <td className="row">
                    <button className="btn" onClick={()=>act(m.id,'quarantine')}>Quarantine</button>
                    <button className="btn" onClick={()=>act(m.id,'undo')}>Undo</button>
                    <button className="btn" onClick={()=>act(m.id,'allow')}>Allow</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </Layout>
  )
}
