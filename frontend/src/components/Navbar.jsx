export default function Navbar({ botUrl }) {
  return (
    <nav className="navbar">
      <div className="container">
        <a href="#" className="logo">Finance Simulator</a>
        <div className="nav-links">
          <a href="#features">Возможности</a>
          <a href="#modules">Модули</a>
          <a href="#how">Как начать</a>
          <a href={botUrl} target="_blank" rel="noopener noreferrer" className="btn-telegram">
            Открыть бота
          </a>
        </div>
      </div>
    </nav>
  )
}
