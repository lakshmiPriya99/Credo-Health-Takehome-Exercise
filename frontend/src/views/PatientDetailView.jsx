import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { getPatient } from '../api'

export default function PatientDetailView() {
  const { id } = useParams()
  const [patient, setPatient] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    setError(null)
    getPatient(id)
      .then(setPatient)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [id])

  return (
    <div>
      <p>
        <Link to="/">&larr; Back to patient list</Link>
      </p>
      {loading && <p>Loading...</p>}
      {error && <p>Failed to load patient: {error}</p>}
      {patient && (
        <div>
          <h2>{patient.name}</h2>
          <p>
            Gender: {patient.gender} | Birth date: {patient.birth_date || 'unknown'}
          </p>
          <h3>Observations</h3>
          {patient.observations.length === 0 ? (
            <p>No observations recorded.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Observation</th>
                  <th>Value</th>
                  <th>Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {patient.observations.map((obs) => (
                  <tr key={obs.id}>
                    <td>{obs.code_text}</td>
                    <td>{obs.value_text || '—'}</td>
                    <td>{obs.effective_date || 'unknown'}</td>
                    <td>{obs.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}
