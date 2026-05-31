import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { fetchCase } from '../api/client'

export default function CaseDetail() {
  const { id } = useParams()
  const [caseData, setCaseData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchCase(id)
      .then(data => { setCaseData(data); setLoading(false) })
      .catch(err => { setError(err.message); setLoading(false) })
  }, [id])

  if (loading) return <div className="container"><p className="loading">Загрузка...</p></div>
  if (error) return <div className="container"><p className="error">Ошибка: {error}</p></div>
  if (!caseData) return <div className="container"><p className="empty">Кейс не найден</p></div>

  return (
    <div className="case-detail container">
      <h1>{caseData.title}</h1>
      <p className="case-description">{caseData.description}</p>
      {caseData.preamble && (
        <div className="case-preamble">{caseData.preamble}</div>
      )}
      <div className="case-steps">
        {caseData.steps?.map((step, i) => (
          <div key={i} className="step-block">
            <h3>Шаг {step.order}: {step.title}</h3>
            <p>{step.question}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
