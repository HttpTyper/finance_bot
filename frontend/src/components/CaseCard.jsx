import { Link } from 'react-router-dom'

const DIFFICULTY_COLORS = {
  easy: '#4caf50',
  medium: '#ff9800',
  hard: '#f44336',
}

export default function CaseCard({ id, title, description, industry, difficulty }) {
  return (
    <Link to={`/cases/${id}`} className="case-card">
      <div className="case-card-header">
        <span className="case-industry">{industry}</span>
        {difficulty && (
          <span
            className="case-difficulty"
            style={{ background: DIFFICULTY_COLORS[difficulty] || '#999' }}
          >
            {difficulty === 'easy' ? 'лёгкий' : difficulty === 'medium' ? 'средний' : 'сложный'}
          </span>
        )}
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
    </Link>
  )
}
