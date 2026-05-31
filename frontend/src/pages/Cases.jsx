import { useState, useEffect } from 'react'
import CaseCard from '../components/CaseCard'
import { fetchCases } from '../api/client'

export default function Cases() {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchCases()
      .then(data => { setCases(data); setLoading(false) })
      .catch(err => { setError(err.message); setLoading(false) })
  }, [])

  if (loading) return <div className="container"><p className="loading">Загрузка кейсов...</p></div>
  if (error) return <div className="container"><p className="error">Ошибка: {error}</p></div>

  return (
    <div className="cases-page container">
      <h1>Учебные кейсы</h1>
      <p className="cases-subtitle">Выберите кейс для изучения. Доступны аудиторские и игровые сценарии.</p>
      {cases.length === 0 ? (
        <p className="empty">Пока нет доступных кейсов. Запустите серверную часть.</p>
      ) : (
        <div className="cases-grid">
          {cases.map(c => (
            <CaseCard
              key={c.id}
              id={c.id}
              title={c.title}
              description={c.description}
              industry={c.industry}
              difficulty={c.difficulty}
            />
          ))}
        </div>
      )}
    </div>
  )
}
