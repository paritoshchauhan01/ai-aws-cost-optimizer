import { useState } from 'react'
import axios from 'axios'

export default function ConnectPage({ onConnect }) {
  const [accessKey, setAccessKey] = useState('')
  const [secretKey, setSecretKey] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleConnect = async () => {
    if (!accessKey || !secretKey) { setError('Both fields are required'); return }
    setLoading(true); setError('')
    try {
      const { data } = await axios.post('/api/connect', {
        access_key: accessKey,
        secret_key: secretKey,
      })
      onConnect({
        access_key: accessKey,
        secret_key: secretKey,
        region: data.region,
        account_id: data.account_id,
      })
    } catch (e) {
      setError(e.response?.data?.detail || 'Connection failed. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="connect-wrapper">
      <div className="connect-card">
        <div className="connect-header">
          <span className="logo-icon">☁️</span>
          <h1>AWS Cost Optimizer</h1>
          <p>Connect your AWS account to analyse costs and get AI-powered savings recommendations</p>
        </div>

        <div className="powered-row">
          <span className="powered-dot" />
          Powered by Gemini AI
        </div>

        <div className="form-group">
          <label>AWS Access Key ID</label>
          <input
            type="text"
            placeholder="AKIAIOSFODNN7EXAMPLE"
            value={accessKey}
            onChange={e => setAccessKey(e.target.value)}
            autoComplete="off"
          />
        </div>

        <div className="form-group">
          <label>AWS Secret Access Key</label>
          <input
            type="password"
            placeholder="••••••••••••••••••••"
            value={secretKey}
            onChange={e => setSecretKey(e.target.value)}
          />
        </div>

        {error && <div className="error-msg">{error}</div>}

        <div className="connect-btn-wrap">
          <button
            className="btn-primary"
            onClick={handleConnect}
            disabled={loading || !accessKey || !secretKey}
            style={{ width: '100%', padding: '13px', fontSize: '15px' }}
          >
            {loading
              ? <><span className="spin-icon" />Connecting…</>
              : '🔗 Connect AWS Account'}
          </button>
        </div>

        <p className="security-note">
          🔒 Credentials are used only for this session and never stored on disk.<br/>
          Use a read-only IAM policy for security. Region is auto-detected.
        </p>
      </div>
    </div>
  )
}
