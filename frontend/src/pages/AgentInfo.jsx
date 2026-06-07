import React from 'react';
import { Bot, GitBranch, BarChart3 } from 'lucide-react';

const AgentInfo = () => {
  return (
    <div className="max-w-6xl mx-auto py-12 px-4">
      <h1 className="text-4xl font-bold mb-2">Multi-Agent AI System</h1>
      <p className="text-gray-600 mb-6">Understand how our AI assistant works — and how it differs from the single-agent MyStore app.</p>

      <div className="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-6 mb-12">
        <h2 className="text-xl font-bold mb-3">See the difference side by side</h2>
        <p className="text-gray-700 mb-4">
          Multi-agent (this app) shows which specialist answered: <strong>Sales Expert [SALES]</strong>, <strong>Order Assistant [ORDER]</strong>, or <strong>Support Team [SUPPORT]</strong>.
          The single-agent app uses one assistant for everything with no routing label.
        </p>
        <table className="w-full text-sm border-collapse mb-4">
          <thead>
            <tr className="bg-gray-900 text-white">
              <th className="p-3 text-left">App</th>
              <th className="p-3 text-left">Folder</th>
              <th className="p-3 text-left">Backend</th>
              <th className="p-3 text-left">Frontend</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="p-3 font-semibold">Multi-Agent (STYLE)</td>
              <td className="p-3">EcommerceMultiAgent</td>
              <td className="p-3">localhost:5000</td>
              <td className="p-3">localhost:3000</td>
            </tr>
            <tr>
              <td className="p-3 font-semibold">Single-Agent (MyStore)</td>
              <td className="p-3">EcommerceSingleAgent</td>
              <td className="p-3">localhost:5001</td>
              <td className="p-3">localhost:3001</td>
            </tr>
          </tbody>
        </table>
        <p className="text-gray-600 text-sm">
          Run this STYLE multi-agent app and compare with the separate single-agent project when needed — no changes required to the single-agent codebase.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-12 mb-12">
        {/* Multi-Agent vs Single Agent */}
        <div className="bg-white p-8 rounded-xl shadow-lg border-2 border-primary">
          <div className="flex items-center mb-4">
            <GitBranch className="text-primary mr-3" size={32} />
            <h2 className="text-2xl font-bold">Multi-Agent System</h2>
          </div>
          <p className="text-gray-700 mb-4">
            Our system uses <strong>3 specialized AI agents</strong> working together:
          </p>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start">
              <span className="text-primary font-bold mr-3">1.</span>
              <div>
                <strong>Sales Agent</strong> - Helps you find products, get recommendations, and learn about specs
              </div>
            </li>
            <li className="flex items-start">
              <span className="text-primary font-bold mr-3">2.</span>
              <div>
                <strong>Order Agent</strong> - Tracks your orders, shows delivery status, and answers order questions
              </div>
            </li>
            <li className="flex items-start">
              <span className="text-primary font-bold mr-3">3.</span>
              <div>
                <strong>Support Agent</strong> - Handles returns, policies, payments, and general help
              </div>
            </li>
          </ul>
        </div>

        <div className="bg-blue-50 p-8 rounded-xl border-2 border-blue-200">
          <div className="flex items-center mb-4">
            <BarChart3 className="text-blue-600 mr-3" size={32} />
            <h2 className="text-2xl font-bold">Single-Agent System</h2>
          </div>
          <p className="text-gray-700 mb-4">
            A single AI agent that tries to handle <strong>everything</strong>:
          </p>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start">
              <span className="text-blue-600 font-bold mr-3">❌</span>
              <div>Less specialized responses</div>
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 font-bold mr-3">❌</span>
              <div>Can't access user-specific data like orders</div>
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 font-bold mr-3">❌</span>
              <div>Slower at complex tasks</div>
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 font-bold mr-3">❌</span>
              <div>Less accurate recommendations</div>
            </li>
          </ul>
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-8 rounded-xl shadow-lg mb-12 border-2 border-purple-200">
        <h2 className="text-2xl font-bold mb-6 flex items-center">
          <Bot className="mr-3 text-purple-600" size={32} />
          How Our Multi-Agent System Works
        </h2>
        
        <div className="space-y-6">
          <div className="flex items-start bg-white p-4 rounded-lg">
            <div className="bg-purple-600 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold mr-4 flex-shrink-0">1</div>
            <div>
              <h3 className="font-bold text-lg mb-1">You Ask a Question</h3>
              <p className="text-gray-700">Type your question in the chat window (e.g., "Where's my order?" or "Show me gaming laptops")</p>
            </div>
          </div>

          <div className="flex items-start bg-white p-4 rounded-lg">
            <div className="bg-purple-600 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold mr-4 flex-shrink-0">2</div>
            <div>
              <h3 className="font-bold text-lg mb-1">Router Agent Detects Topic</h3>
              <p className="text-gray-700">The system analyzes your message and determines which agent should help (Sales, Order, or Support)</p>
            </div>
          </div>

          <div className="flex items-start bg-white p-4 rounded-lg">
            <div className="bg-purple-600 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold mr-4 flex-shrink-0">3</div>
            <div>
              <h3 className="font-bold text-lg mb-1">Specialized Agent Responds</h3>
              <p className="text-gray-700">The right agent uses its expertise and access to data to give you an accurate, helpful response</p>
            </div>
          </div>

          <div className="flex items-start bg-white p-4 rounded-lg">
            <div className="bg-purple-600 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold mr-4 flex-shrink-0">4</div>
            <div>
              <h3 className="font-bold text-lg mb-1">You Get Results</h3>
              <p className="text-gray-700">Get fast, accurate, specialized responses from the agent that knows your topic best</p>
            </div>
          </div>
        </div>
      </div>

      {/* Benefits */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-green-50 p-6 rounded-xl border-2 border-green-200">
          <h3 className="font-bold text-lg mb-3 text-green-700">✅ Better Accuracy</h3>
          <p className="text-gray-700">Each agent specializes in its domain, giving you more accurate information</p>
        </div>
        
        <div className="bg-blue-50 p-6 rounded-xl border-2 border-blue-200">
          <h3 className="font-bold text-lg mb-3 text-blue-700">✅ Faster Responses</h3>
          <p className="text-gray-700">Specialized agents process requests quicker and more efficiently</p>
        </div>
        
        <div className="bg-orange-50 p-6 rounded-xl border-2 border-orange-200">
          <h3 className="font-bold text-lg mb-3 text-orange-700">✅ Smart Routing</h3>
          <p className="text-gray-700">Your questions automatically go to the right expert agent</p>
        </div>
      </div>

      {/* Example Conversations */}
      <div className="mt-12 bg-white p-8 rounded-xl shadow-lg border">
        <h2 className="text-2xl font-bold mb-6">📝 Example Questions</h2>
        
        <div className="space-y-4">
          <div className="border-l-4 border-primary pl-4">
            <p className="font-semibold text-primary">Sales Agent handles:</p>
            <p className="text-gray-700">"Show me gaming laptops under ₹50,000" or "What's the best laptop for coding?"</p>
          </div>
          
          <div className="border-l-4 border-blue-500 pl-4">
            <p className="font-semibold text-blue-600">Order Agent handles:</p>
            <p className="text-gray-700">"Where's my order?" or "Track my delivery" or "What's the status of order #123?"</p>
          </div>
          
          <div className="border-l-4 border-purple-500 pl-4">
            <p className="font-semibold text-purple-600">Support Agent handles:</p>
            <p className="text-gray-700">"What's your return policy?" or "How do I make a payment?" or "Do you have free shipping?"</p>
          </div>
        </div>
      </div>

      {/* Try It Out */}
      <div className="mt-12 bg-gradient-to-r from-primary to-primary-dark text-white p-8 rounded-xl text-center">
        <h2 className="text-2xl font-bold mb-4">Try Our Multi-Agent Assistant</h2>
        <p className="mb-6">Click the chat button in the bottom-right corner to start talking with our AI system. Ask about products, orders, or policies!</p>
        <button onClick={() => window.location.href = '/#'} className="bg-white text-primary px-8 py-3 rounded-lg font-bold hover:bg-gray-100">
          Open Chat
        </button>
      </div>
    </div>
  );
};

export default AgentInfo;
