import { Link } from 'react-router-dom'

export default function Landing() {
  return (
    <div className="landing">
      <section className="hero">
        <div className="container">
          <h1>Finance Simulator</h1>
          <p className="hero-subtitle">
            Интерактивный тренажёр по аудиту и финансовому анализу.
            Разбор реальных кейсов, работа с отчётностью, аудиторские процедуры.
          </p>
          <div className="hero-actions">
            <Link to="/cases" className="btn-primary">Начать обучение</Link>
            <a href="https://t.me/finsimulator01bot" target="_blank" rel="noopener" className="btn-secondary">
              Открыть в Telegram
            </a>
          </div>
        </div>
      </section>

      <section className="features">
        <div className="container">
          <h2>Что вы изучите</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Анализ отчётности</h3>
              <p>Ликвидность, рентабельность, оборачиваемость — коэффициенты и их интерпретация</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3>Аудиторские процедуры</h3>
              <p>Планирование, оценка рисков, сбор доказательств, формирование мнения</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🛡️</div>
              <h3>Мошенничество и СВК</h3>
              <p>Red flags, тестирование контроля, процедуры по МСА 240</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎮</div>
              <h3>Игровые кейсы</h3>
              <p>Управление оборотным капиталом, инвестиции, валютные риски</p>
            </div>
          </div>
        </div>
      </section>

      <section className="how-it-works">
        <div className="container">
          <h2>Как это работает</h2>
          <div className="steps">
            <div className="step">
              <span className="step-num">1</span>
              <p>Выберите кейс из каталога</p>
            </div>
            <div className="step">
              <span className="step-num">2</span>
              <p>Изучите теорию и данные</p>
            </div>
            <div className="step">
              <span className="step-num">3</span>
              <p>Ответьте на вопросы</p>
            </div>
            <div className="step">
              <span className="step-num">4</span>
              <p>Получите объяснение и баллы</p>
            </div>
          </div>
        </div>
      </section>

      <section className="cta">
        <div className="container">
          <h2>Готовы начать?</h2>
          <p>Попробуйте демо-кейс в браузере или откройте полную версию в Telegram</p>
          <Link to="/cases" className="btn-primary">Перейти к кейсам</Link>
        </div>
      </section>
    </div>
  )
}
