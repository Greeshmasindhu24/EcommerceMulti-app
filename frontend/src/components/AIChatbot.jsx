import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { sendChatMessage } from '../api';

const CHAT_SESSION_KEY = 'style_chat_session_id';

function getOrCreateSessionId() {
  let sessionId = sessionStorage.getItem(CHAT_SESSION_KEY);
  if (!sessionId) {
    sessionId = `chat-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    sessionStorage.setItem(CHAT_SESSION_KEY, sessionId);
  }
  return sessionId;
}

const AIChatbot = ({ onAddToCart, onAddToWishlist }) => {
  const navigate = useNavigate();
  const [sessionId] = useState(getOrCreateSessionId);
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      text: "Hi! I'm the Style Multi-Agent assistant. I only recommend products from our live catalog. Try: 'show mobiles', 'iPhone price', or 'add all to cart' after a search.",
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

  const executeChatActions = useCallback((actions) => {
    if (!actions?.length) return;

    actions.forEach((action) => {
      const products = action.products || [];
      if (!products.length) return;

      if (action.type === 'ADD_TO_CART' || action.type === 'ADD_ALL_TO_CART') {
        products.forEach((product) => onAddToCart?.(product));
      }

      if (action.type === 'ADD_TO_WISHLIST') {
        products.forEach((product) => onAddToWishlist?.(product));
      }

      if (action.type === 'BUY_NOW') {
        products.forEach((product) => onAddToCart?.(product));
        navigate('/cart');
      }
    });
  }, [navigate, onAddToCart, onAddToWishlist]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input;
    setMessages((prev) => [...prev, { text: userMsg, isUser: true }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(userMsg, sessionId);
      const replyText = response?.reply || "Sorry, I couldn't understand that. Please try again.";
      const agentName = response?.agent || 'Style Assistant';
      const routeLabel = response?.route ? ` [${response.route}]` : '';
      const intentLabel = response?.intent ? ` · ${response.intent}` : '';

      executeChatActions(response?.actions);

      setMessages((prev) => [
        ...prev,
        {
          text: replyText,
          isUser: false,
          agent: `${agentName}${routeLabel}${intentLabel}`,
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
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</div>
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
            placeholder="Search products, add to cart..."
          />
          <button type="submit" disabled={isLoading}>➔</button>
        </form>
      </div>
    </div>
  );
};

export default AIChatbot;
