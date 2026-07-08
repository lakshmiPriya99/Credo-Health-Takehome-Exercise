async function request(path) {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`)
  }
  return response.json()
}

export function getPatients() {
  return request('/api/patients/')
}

export function getPatient(id) {
  return request(`/api/patients/${id}/`)
}
