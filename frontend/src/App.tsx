import { Navigate, Route, Routes } from 'react-router-dom'
import './App.css'
import { ChatPage } from './pages/ChatPage'

function App() {
  return (
    <div className="app-root">
      <Routes>
        <Route path="/" element={<Navigate to="/chat" replace />} />
        <Route path="/chat" element={<ChatPage />} />
        {/* Future pages can be added here, e.g. /settings, /history, etc. */}
      </Routes>
    </div>
  )
}

export default App
