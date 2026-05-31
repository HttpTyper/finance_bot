import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
  const { pathname } = useLocation()

  return (
    <nav className="navbar">
      <div className="container">
        <Link to="/" className="logo">Finance Simulator</Link>
        <div className="nav-links">
          <Link to="/" className={pathname === '/' ? 'active' : ''}>Главная</Link>
          <Link to="/cases" className={pathname.startsWith('/cases') ? 'active' : ''}>Кейсы</Link>
          <a href="https://t.me/finsimulator01bot" target="_blank" rel="noopener" className="btn-telegram">
            Telegram бот
          </a>
        </div>
      </div>
    </nav>
  )
}
