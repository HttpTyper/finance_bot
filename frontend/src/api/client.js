const BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')

export async function fetchCases() {
  const res = await fetch(`${BASE}/cases`)
  if (!res.ok) throw new Error('Failed to fetch cases')
  return res.json()
}

export async function fetchCase(id) {
  const res = await fetch(`${BASE}/cases/${id}`)
  if (!res.ok) throw new Error('Case not found')
  return res.json()
}

export async function fetchCaseStep(caseId, stepOrder) {
  const res = await fetch(`${BASE}/cases/${caseId}/steps/${stepOrder}`)
  if (!res.ok) throw new Error('Step not found')
  return res.json()
}

export async function submitAnswer(caseId, stepOrder, optionIndex) {
  const res = await fetch(`${BASE}/cases/${caseId}/steps/${stepOrder}/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ option_index: optionIndex }),
  })
  if (!res.ok) throw new Error('Failed to submit')
  return res.json()
}
