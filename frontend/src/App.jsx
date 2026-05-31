import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import './App.css'

const BOT_URL = 'https://t.me/finsimulator01bot'

export default function App() {
  return (
    <div className="app">
      <Navbar botUrl={BOT_URL} />
      <main>
        <Landing botUrl={BOT_URL} />
      </main>
      <footer className="footer">
        <div className="container">
          <p>
            Finance Simulator &copy; 2026 &mdash; тренажёр по аудиту и финансам в Telegram
          </p>
          <a href={BOT_URL} target="_blank" rel="noopener noreferrer" className="footer-link">
            @finsimulator01bot
          </a>
        </div>
      </footer>
    </div>
  )
}
