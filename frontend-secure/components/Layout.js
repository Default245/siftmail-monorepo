
import Link from 'next/link';
export default function Layout({children}){
  return (
    <div style={{minHeight:'100vh',display:'flex',flexDirection:'column',background:'#0f172a',color:'#e6edf6'}}>
      <header style={{borderBottom:'1px solid #1f2a44',padding:'14px 0'}}>
        <div className="container row">
          <strong>✳︎ Sift Mail</strong>
          <nav className="row" style={{gap:16}}>
            <Link href="/">Home</Link>
            <Link href="/app/dashboard">Dashboard</Link>
            <Link href="/privacy">Privacy</Link>
            <Link href="/terms">Terms</Link>
          </nav>
        </div>
      </header>
      <main style={{flex:1}}>{children}</main>
      <footer style={{borderTop:'1px solid #1f2a44',padding:'16px 0'}}>
        <div className="container row" style={{justifyContent:'space-between'}}>
          <small className="muted">© {new Date().getFullYear()} Sift Mail</small>
          <small className="muted">support@siftmail.app</small>
        </div>
      </footer>
    </div>
  );
}
