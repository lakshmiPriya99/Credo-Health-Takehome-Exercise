import { Link, Route, Routes } from 'react-router-dom'

import PatientDetailView from './views/PatientDetailView.jsx'
import PatientListView from './views/PatientListView.jsx'

export default function App() {
  return (
    <div>
      <h1>
        <Link to="/">Credo Patient Records</Link>
      </h1>
      <Routes>
        <Route path="/" element={<PatientListView />} />
        <Route path="/patients/:id" element={<PatientDetailView />} />
      </Routes>
    </div>
  )
}
