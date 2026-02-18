import Link from 'next/link';
import Image from 'next/image';

export default function Layout({ children }) {
  return (
    <>
      <header>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div className="brand">
            <Image src="/assets/logo.svg" alt="SiftMail logo" width={32} height={32} />
            <span>SiftMail</span>
          </div>
          <nav>
            <Link href="/" legacyBehavior><a>Home</a></Link>
            <Link href="/app" legacyBehavior><a>Console</a></Link>
            <Link href="/data-policy" legacyBehavior><a>Data Policy</a></Link>
            <Link href="/privacy" legacyBehavior><a>Privacy</a></Link>
            <Link href="/terms" legacyBehavior><a>Terms</a></Link>
          </nav>
        </div>
      </header>
      <main>{children}</main>
      <footer>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <small>© 2025 SiftMail</small>
          <small>Contact: <a href="mailto:support@siftmail.app" className="muted">support@siftmail.app</a></small>
        </div>
      </footer>
    </>
  );
}
