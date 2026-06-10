# 🛒 E-Commerce Multi-Agent System - Setup Guide

## 🚀 Quick Start

### 1. Backend Setup (Python/Flask)

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the backend server
python app.py
```

The backend will start on `http://localhost:5000`

### 2. Frontend Setup (React/Vite)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file for local development
echo "REACT_APP_API_URL=http://localhost:5000" > .env

# Run development server
npm run dev
```

The frontend will start on `http://localhost:5173` (or similar)

---

## 🔧 Configuration

### Environment Variables (.env)

Create a `.env` file in the `frontend/` directory:

```
# For local backend
REACT_APP_API_URL=http://localhost:5000

# For deployed backend on Render
# REACT_APP_API_URL=https://ecommercemulti-app1.onrender.com
```

---

## 🤖 Multi-Agent System Overview

Your application has **3 AI agents** working together:

### 1. **Sales Agent** 🛍️
- Recommends products based on user queries
- Provides product specifications and pricing
- Helps users find what they're looking for
- **Example**: "Show me gaming laptops under ₹50,000"

### 2. **Order Agent** 📦
- Tracks user orders and delivery status
- Shows order history and details
- Provides tracking information
- **Example**: "Where's my order?" or "Track order #123"

### 3. **Support Agent** 💬
- Answers policy questions (returns, shipping, payments)
- Provides general support information
- Handles billing inquiries
- **Example**: "What's your return policy?" or "Do you offer free shipping?"

---

## 🔑 Key Improvements Made

### ✅ Fixed Checkout Request Failures
- **Problem**: API URL was hardcoded to deployed backend, causing CORS/JWT errors
- **Solution**: 
  - Backend API now auto-detects localhost vs production
  - Improved error messages showing exactly what went wrong
  - Added JWT token validation with auto-logout on 401
  - Better network error handling

### ✅ Multi-Agent System Explanation
- New `/agent-info` page explains how the system works
- Shows difference between multi-agent and single-agent
- View it at: `http://localhost:5173/agent-info`

---

## 🐛 Troubleshooting

### "Error placing order" or "Request failed"

**Cause**: Backend not running or API URL is wrong

**Fix**:
1. Ensure backend is running: `python app.py`
2. Check that backend is on port 5000
3. Create/verify `.env` file has correct `REACT_APP_API_URL`
4. Check browser console (F12) for exact error message

### "Your session has expired"

**Cause**: JWT token is invalid or expired

**Fix**:
1. Logout and login again
2. This refreshes your authentication token

### "Network Error"

**Cause**: Backend server is down or unreachable

**Fix**:
1. Start backend: `python app.py` in `/backend` directory
2. Verify it shows "Running on http://127.0.0.1:5000"

---

## 📱 Chat with AI Assistant

Click the 💬 chat icon in the bottom-right corner to:
- Ask about products
- Track orders
- Get help with policies
- Get recommendations

The system automatically routes your question to the right specialist agent!

---

## 🎯 Testing the Multi-Agent System

Try these conversations in the chat:

**Sales Questions:**
- "What gaming laptops do you have?"
- "Show me phones under ₹30,000"
- "What's the best laptop for coding?"

**Order Questions:**
- "Where's my order?"
- "Track my delivery"
- "What's the status of my order?"

**Support Questions:**
- "What's your return policy?"
- "Do you have free shipping?"
- "What payment methods do you accept?"

---

## 📊 Architecture

```
┌─────────────────────────────────────┐
│     Frontend (React/Vite)            │
│  - User Interface                    │
│  - Chat Component                    │
│  - Order Management                  │
└──────────────┬──────────────────────┘
               │ HTTP/CORS
┌──────────────▼──────────────────────┐
│     Backend (Python/Flask)           │
│                                      │
│  ┌─────────────────────────────┐   │
│  │  Router Agent               │   │
│  │  - Classifies user message  │   │
│  └────────┬────────┬───────────┘   │
│           │        │                │
│      ┌────▼─┐ ┌───▼────┐ ┌───────┐│
│      │Sales │ │ Order  │ │Support││
│      │Agent │ │ Agent  │ │ Agent ││
│      └──────┘ └────────┘ └───────┘│
│                                    │
│  Database: SQLite/PostgreSQL       │
└────────────────────────────────────┘
```

---

## 🌐 Deployment

### Frontend (Vercel/Netlify)
```bash
npm run build
# Deploy dist/ folder
```

### Backend (Render/Heroku)
```bash
# Push to GitHub
git push heroku main
```

Set environment variables on hosting platform:
- `POSTGRES_URL` (if using PostgreSQL)

---

## ❓ FAQ

**Q: What's the difference between multi-agent and single-agent?**
A: Multi-agent uses specialized AI agents for different tasks (sales, orders, support) - more accurate and faster. Single-agent tries to do everything - less accurate.

**Q: Why does the checkout fail?**
A: Make sure your `.env` file points to the correct backend. For local dev: `http://localhost:5000`

**Q: How do I see what the chat agents are doing?**
A: Check browser console (F12) and backend logs. They'll show which agent handled each message.

**Q: Can I add more agents?**
A: Yes! Edit `backend/app.py` and add new agent functions following the same pattern.

---

## 🤝 Support

For issues or questions:
1. Check the error message in browser console (F12)
2. Check backend logs (terminal where you ran `python app.py`)
3. Verify `.env` configuration
4. Ensure both frontend and backend are running

Good luck! 🚀
