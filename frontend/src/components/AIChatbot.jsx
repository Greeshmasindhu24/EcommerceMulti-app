import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../api';

const AIChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      text: "Hi! I'm the Style Multi-Agent assistant. I answer using our live product catalog and your orders (when logged in). Try: 'show all products', 'iPhone price', or 'return policy'.",
      isUser: false,
      agent: 'System',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input;
    setMessages((prev) => [...prev, { text: userMsg, isUser: true }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(userMsg);
      const replyText = response?.reply || "Sorry, I couldn't understand that. Please try again.";
      const agentName = response?.agent || 'Style Assistant';
      const routeLabel = response?.route ? ` [${response.route}]` : '';
      setMessages((prev) => [
        ...prev,
        {
          text: replyText,
          isUser: false,
          agent: `${agentName}${routeLabel}`,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          text: "Sorry, I couldn't connect to the server. Please try again.",
          isUser: false,
          agent: 'Error',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-widget">
      <button type="button" className="chat-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? '✕' : '💬'}
      </button>

      <div className={`chat-window ${!isOpen ? 'hidden' : ''}`}>
        <div className="chat-header">
          <div className="chat-header-dot" />
          <div>
            <div style={{ fontWeight: 600 }}>Style Assistant</div>
            <div style={{ fontSize: '0.8rem', opacity: 0.85 }}>Multi-Agent · Router → Specialist</div>
          </div>
        </div>

        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.isUser ? 'user' : 'bot'}`}>
              {!msg.isUser && <div className="agent-name">{msg.agent}</div>}
              <div>{msg.text}</div>
            </div>
          ))}
          {isLoading && (
            <div className="message bot">
              <div className="agent-name">Routing...</div>
              <div style={{ fontStyle: 'italic', color: 'var(--aura-muted)' }}>Thinking...</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-area" onSubmit={handleSend}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about products, orders..."
          />
          <button type="submit" disabled={isLoading}>➔</button>
        </form>
      </div>
    </div>
  );
};

export default AIChatbot;
