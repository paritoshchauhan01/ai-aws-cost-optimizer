import { useState } from 'react'
import axios from 'axios'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  CartesianGrid
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background:'rgba(13,17,23,0.95)', border:'1px solid #1e2640',
      borderRadius:8, padding:'8px 14px', fontSize:13
    }}>
      <div style={{ color:'#5a6a8a', marginBottom:2 }}>{label}</div>
      <div style={{ fontWeight:700 }}>{payload[0].value} resources</div>
    </div>
  )
}

export default function DashboardPage({ credentials, scanData, setScanData }) {
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  const [aiAnalysis, setAiAnalysis] = useState('')

  const handleScan = async () => {
    setLoading(true); setError('')
    try {
      const { data } = await axios.post('/api/scan', {
        access_key: credentials.access_key,
        secret_key: credentials.secret_key,
        region: credentials.region,
      })
      setScanData(data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Scan failed')
    } finally {
      setLoading(false)
    }
  }

  const handleAiAnalyze = async () => {
    setAiLoading(true); setAiAnalysis('')
    try {
      const { data } = await axios.post('/api/analyze', {
        access_key: credentials.access_key,
        secret_key: credentials.secret_key,
        region: credentials.region,
      })
      setAiAnalysis(data.analysis)
    } catch (e) {
      setAiAnalysis('AI analysis failed: ' + (e.response?.data?.detail || e.message))
    } finally {
      setAiLoading(false)
    }
  }

  const resourceCounts = scanData ? [
    { name: 'EC2', count: scanData.resources.ec2.length, color: '#5b5ef4' },
    { name: 'EBS', count: scanData.resources.ebs.length, color: '#22d3ee' },
    { name: 'RDS', count: scanData.resources.rds.length, color: '#10b981' },
    { name: 'S3',  count: scanData.resources.s3.length,  color: '#f59e0b' },
  ] : []

  const totalResources = scanData
    ? Object.values(scanData.resources).reduce((s, arr) => s + arr.length, 0)
    : 0

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h2>Dashboard</h2>
          <p className="account-label">
            Account: {credentials.account_id} · {credentials.region}
          </p>
        </div>
        <div className="header-actions">
          <button className="btn-primary" onClick={handleScan} disabled={loading}>
            {loading
              ? <><span className="spin-icon" />Scanning…</>
              : '🔍 Scan Account'}
          </button>
          {scanData && (
            <button className="btn-secondary" onClick={handleAiAnalyze} disabled={aiLoading}>
              {aiLoading
                ? <><span className="spin-icon" style={{borderTopColor:'var(--accent)'}} />Analyzing…</>
                : '✨ Gemini Analysis'}
            </button>
          )}
        </div>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {!scanData && !loading && (
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h3>No scan data yet</h3>
          <p>Click "Scan Account" to analyse your AWS resources and get cost-saving recommendations</p>
        </div>
      )}

      {scanData && (
        <>
          {/* Summary cards */}
          <div className="cards-row">
            <div className="card card-cost">
              <div className="card-label">Monthly Cost</div>
              <div className="card-value">${scanData.monthly_cost.toLocaleString()}</div>
              <div className="card-sub">this month so far</div>
            </div>
            <div className="card card-saving">
              <div className="card-label">Potential Saving</div>
              <div className="card-value">${scanData.potential_saving.toLocaleString()}</div>
              <div className="card-sub">{scanData.recommendations.length} recommendations</div>
            </div>
            <div className="card card-resources">
              <div className="card-label">Total Resources</div>
              <div className="card-value">{totalResources}</div>
              <div className="card-sub">EC2 · EBS · RDS · S3</div>
            </div>
          </div>

          {/* Bar chart */}
          <div className="chart-card">
            <h3>Resources by Service</h3>
            <ResponsiveContainer width="100%" height={210}>
              <BarChart data={resourceCounts} margin={{ top: 8, right: 16, bottom: 0, left: -10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#5a6a8a' }} axisLine={false} tickLine={false} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#5a6a8a' }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(91,94,244,0.06)' }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]} maxBarSize={52}>
                  {resourceCounts.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Recommendations */}
          {scanData.recommendations.length > 0 && (
            <div className="recs-card">
              <h3>Cost Recommendations</h3>
              <div className="recs-list">
                {scanData.recommendations.map((r, i) => (
                  <div key={i} className="rec-item" style={{ animationDelay: `${i * 0.07}s` }}>
                    <div className="rec-badge">{r.resource_type}</div>
                    <div className="rec-body">
                      <div className="rec-issue">{r.issue}</div>
                      <div className="rec-action">→ {r.action}</div>
                      <div className="rec-id">{r.resource_id}</div>
                    </div>
                    <div className="rec-saving">${r.saving}/mo</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Gemini AI Analysis */}
          {aiAnalysis && (
            <div className="ai-card">
              <div className="ai-card-header">
                <span className="gemini-spinner" />
                <h3>Gemini AI Analysis</h3>
              </div>
              <pre className="ai-text">{aiAnalysis}</pre>
            </div>
          )}
        </>
      )}
    </div>
  )
}
