import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import ConnectPage from './pages/ConnectPage'
import DashboardPage from './pages/DashboardPage'
import ChatPage from './pages/ChatPage'
import Navbar from './components/Navbar'
import './App.css'

function App() {
  const [credentials, setCredentials] = useState(null)   // { access_key, secret_key, account_id, region }
  const [scanData, setScanData] = useState(null)

  return (
    <BrowserRouter>
      {credentials && <Navbar onDisconnect={() => { setCredentials(null); setScanData(null) }} />}
      <Routes>
        <Route
          path="/"
          element={
            credentials
              ? <Navigate to="/dashboard" replace />
              : <ConnectPage onConnect={setCredentials} />
          }
        />
        <Route
          path="/dashboard"
          element={
            credentials
              ? <DashboardPage credentials={credentials} scanData={scanData} setScanData={setScanData} />
              : <Navigate to="/" replace />
          }
        />
        <Route
          path="/chat"
          element={
            credentials
              ? <ChatPage credentials={credentials} />
              : <Navigate to="/" replace />
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
