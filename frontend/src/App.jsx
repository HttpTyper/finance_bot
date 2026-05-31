import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import Cases from './pages/Cases'
import CaseDetail from './pages/CaseDetail'
import './App.css'

export default function App() {
  return (
    <div className="app">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/cases" element={<Cases />} />
          <Route path="/cases/:id" element={<CaseDetail />} />
        </Routes>
      </main>
      <footer className="footer">
        <div className="container">
          <p>Finance Simulator &copy; 2026 &mdash; интерактивный тренажёр по аудиту</p>
        </div>
      </footer>
    </div>
  )
}
