import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const QUICK_PROMPTS = [
  'Analyze my AWS account for cost savings',
  'Why might my AWS bill be increasing?',
  'What are the cheapest EC2 alternatives?',
  'How can I reduce my S3 storage costs?',
  'Explain Reserved Instances vs Savings Plans',
  'How do Savings Plans compare to Spot Instances?',
]

export default function ChatPage({ credentials }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hi! I'm your AWS cost optimization assistant, powered by Gemini AI.\n\nI can help you understand your AWS spending, find savings opportunities, and explain cost concepts.\n\nWhat would you like to know?`,
    },
  ])
  const [input, setInput]   = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text) => {
    const msg = text || input.trim()
    if (!msg || loading) return

    const newMessages = [...messages, { role: 'user', content: msg }]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    try {
      const { data } = await axios.post('/api/chat', {
        message: msg,
        access_key: credentials.access_key,
        secret_key: credentials.secret_key,
        history: newMessages.slice(-6),
      })
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠️ Sorry, I encountered an error. Please try again.',
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h2>✨ AI Cost Assistant</h2>
        <p>Ask anything about your AWS costs — powered by Gemini</p>
      </div>

      <div className="quick-prompts">
        {QUICK_PROMPTS.map((p, i) => (
          <button key={i} className="quick-btn" onClick={() => sendMessage(p)}>
            {p}
          </button>
        ))}
      </div>

      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            <div className="msg-row">
              {m.role === 'assistant' && (
                <div className="msg-avatar">✦</div>
              )}
              <div className="message-bubble">
                <pre>{m.content}</pre>
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="msg-row">
              <div className="msg-avatar">✦</div>
              <div className="message-bubble typing">
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-row">
        <input
          type="text"
          placeholder="Ask about your AWS costs…"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          disabled={loading}
        />
        <button
          className="btn-primary"
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
        >
          <span className="send-icon">➤</span>
        </button>
      </div>
    </div>
  )
}
