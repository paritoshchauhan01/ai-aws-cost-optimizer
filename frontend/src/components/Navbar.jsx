import { Link, useLocation } from 'react-router-dom'

export default function Navbar({ onDisconnect }) {
  const { pathname } = useLocation()
  return (
    <nav className="navbar">
      <div className="nav-brand">
        ☁️ AWS Cost Optimizer
        <span className="gemini-badge">GEMINI AI</span>
      </div>
      <div className="nav-links">
        <Link className={pathname === '/dashboard' ? 'nav-link active' : 'nav-link'} to="/dashboard">
          Dashboard
        </Link>
        <Link className={pathname === '/chat' ? 'nav-link active' : 'nav-link'} to="/chat">
          AI Chat
        </Link>
      </div>
      <button className="btn-ghost" onClick={onDisconnect}>Disconnect</button>
    </nav>
  )
}
