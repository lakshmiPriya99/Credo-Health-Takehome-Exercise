import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { getPatients } from '../api'

export default function PatientListView() {
  const [patients, setPatients] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getPatients()
      .then(setPatients)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p>Loading...</p>
  if (error) return <p>Failed to load patients: {error}</p>

  return (
    <div>
      <h2>Patients</h2>
      <ul>
        {patients.map((patient) => (
          <li key={patient.id}>
            <Link to={`/patients/${patient.id}`}>{patient.name}</Link> (
            {patient.gender}, born {patient.birth_date || 'unknown'}) —{' '}
            {patient.observation_count} observation(s)
          </li>
        ))}
      </ul>
    </div>
  )
}
