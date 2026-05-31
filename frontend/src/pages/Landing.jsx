const MODULES = [
  'Ликвидность и платёжеспособность',
  'Рентабельность и эффективность',
  'Финансовая устойчивость',
  'Оборачиваемость активов',
  'Аудит денежных потоков',
  'МСА и стандарты аудита',
  'СВК и профессиональная этика',
  'Мошенничество и существенность',
  'Игровые финансовые кейсы',
]

export default function Landing({ botUrl }) {
  return (
    <div className="landing">
      <section className="hero">
        <div className="container hero-grid">
          <div className="hero-text">
            <p className="hero-badge">Telegram-бот</p>
            <h1>Finance Simulator</h1>
            <p className="hero-subtitle">
              Интерактивный тренажёр по аудиту и финансовому анализу прямо в Telegram.
              Разбор кейсов, таблицы отчётности, теория и проверка знаний — без установки приложений.
            </p>
            <div className="hero-actions">
              <a href={botUrl} target="_blank" rel="noopener noreferrer" className="btn-primary">
                Запустить бота
              </a>
              <a href="#how" className="btn-secondary">
                Как пользоваться
              </a>
            </div>
            <p className="hero-note">Бесплатно · Работает на телефоне и ПК</p>
          </div>

          <div className="bot-preview" aria-hidden="true">
            <div className="bot-preview-header">
              <span className="bot-preview-dot" />
              <span className="bot-preview-dot" />
              <span className="bot-preview-dot" />
              <span className="bot-preview-title">Finance Simulator Bot</span>
            </div>
            <div className="bot-preview-body">
              <div className="chat-bubble bot">
                👋 Добро пожаловать! Это симулятор кейсов по реальному сектору экономики.
              </div>
              <div className="chat-bubble bot">
                Выберите действие в меню:
              </div>
              <div className="chat-buttons">
                <span>📂 Доступные кейсы</span>
                <span>📚 Обучение аудиту</span>
                <span>👤 Мой профиль</span>
                <span>🏆 Рейтинг</span>
              </div>
              <div className="chat-bubble user">Обучение аудиту</div>
              <div className="chat-bubble bot">
                📊 Ликвидность: оценка платёжеспособности
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="features">
        <div className="container">
          <h2>Что умеет бот</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Финансовый анализ</h3>
              <p>Коэффициенты ликвидности, рентабельности, оборачиваемости — с разбором и пояснениями</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3>Аудиторские процедуры</h3>
              <p>Планирование, риски, доказательства, формирование мнения по МСА</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📚</div>
              <h3>Теория + практика</h3>
              <p>Сначала материал по теме, затем вопросы и игровые сценарии с обратной связью</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🏆</div>
              <h3>Рейтинг и прогресс</h3>
              <p>Баллы за правильные ответы, профиль и таблица лидеров среди участников</p>
            </div>
          </div>
        </div>
      </section>

      <section id="modules" className="modules">
        <div className="container">
          <h2>Темы в боте</h2>
          <p className="section-lead">
            Более 15 модулей по аудиту и финансам — от базовых коэффициентов до СВК и мошенничества.
          </p>
          <ul className="modules-list">
            {MODULES.map((title) => (
              <li key={title}>{title}</li>
            ))}
          </ul>
        </div>
      </section>

      <section id="how" className="how-it-works">
        <div className="container">
          <h2>Как начать за 1 минуту</h2>
          <div className="steps">
            <div className="step">
              <span className="step-num">1</span>
              <h3>Откройте бота</h3>
              <p>Нажмите «Запустить бота» — Telegram откроет чат с @finsimulator01bot</p>
            </div>
            <div className="step">
              <span className="step-num">2</span>
              <h3>Нажмите Start</h3>
              <p>Команда /start создаст профиль и покажет главное меню</p>
            </div>
            <div className="step">
              <span className="step-num">3</span>
              <h3>Выберите модуль</h3>
              <p>«Обучение аудиту» для теории или «Доступные кейсы» для симуляции</p>
            </div>
            <div className="step">
              <span className="step-num">4</span>
              <h3>Учитесь и проходите</h3>
              <p>Отвечайте на вопросы, смотрите таблицы и набирайте рейтинг</p>
            </div>
          </div>
        </div>
      </section>

      <section className="cta">
        <div className="container">
          <h2>Весь тренажёр — в Telegram</h2>
          <p>Не нужно регистрироваться на сайте. Просто откройте бота и начните первый кейс.</p>
          <a href={botUrl} target="_blank" rel="noopener noreferrer" className="btn-primary btn-large">
            Перейти в @finsimulator01bot
          </a>
        </div>
      </section>
    </div>
  )
}
