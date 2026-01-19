import { Navigate, Route, Routes } from 'react-router-dom'
import './App.css'
import { ChatPage } from './pages/ChatPage'
import { RoadmapPage } from './pages/RoadmapPage'

function App() {
  return (
    <div className="app-root">
      <Routes>
        <Route path="/" element={<Navigate to="/chat" replace />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/roadmap/:id" element={<RoadmapPage />} />
      </Routes>
    </div>
  )
}

export default App
