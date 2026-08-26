"use client";

import { useState, useRef, useEffect } from 'react';
import { apiFetch } from '@/lib/api';

export default function ChatbotPage() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: 'Hello! I am your LegalGuard Advisor. Ask me anything about regulatory compliance rules, seller policy guidelines, or flagged product details.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { id: Date.now(), sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setLoading(true);

    try {
      const data = await apiFetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentInput }),
      });

      const botMessage = {
        id: Date.now() + 1,
        sender: 'bot',
        text: data.reply || 'No response generated.',
        sources: data.sources || [],
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'bot',
          text: `Error: ${err.message}`,
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto flex flex-col h-[80vh] bg-zinc-900/90 backdrop-blur-2xl rounded-2xl border border-zinc-800 shadow-[0_0_50px_rgba(0,0,0,0.8)] overflow-hidden relative">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-[2px] bg-gradient-to-r from-transparent via-emerald-500 to-transparent" />

      {/* Header */}
      <div className="px-6 py-4 bg-zinc-950/80 border-b border-zinc-800/80 flex justify-between items-center">
        <div>
          <h1 className="text-base font-bold text-white tracking-wide">Legal Advisor AI</h1>
          <p className="text-xs text-emerald-400 font-mono mt-0.5">FAISS Vector RAG Engine Active</p>
        </div>
        <span className="flex h-2.5 w-2.5 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 p-6 overflow-y-auto space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-md ${
                msg.sender === 'user'
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-zinc-950 font-medium rounded-br-xs'
                  : msg.isError
                  ? 'bg-red-950/60 border border-red-500/50 text-red-200 rounded-bl-xs'
                  : 'bg-zinc-950 border border-zinc-800 text-zinc-200 rounded-bl-xs'
              }`}
            >
              <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-2 border-t border-zinc-800 text-xs text-zinc-400">
                  <span className="font-semibold text-emerald-400">Sources:</span> {msg.sources.join(', ')}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-zinc-950 text-zinc-400 rounded-2xl rounded-bl-xs px-4 py-3 text-xs border border-zinc-800 flex items-center space-x-2">
              <span className="inline-block w-2 h-2 bg-emerald-400 rounded-full animate-bounce"></span>
              <span>Retrieving regulatory vectors & generating response...</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSend} className="p-4 bg-zinc-950/80 border-t border-zinc-800 flex gap-3">
        <input
          type="text"
          placeholder="Ask about compliance policies or regulatory guidelines..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 px-4 py-3 bg-zinc-900 border border-zinc-800 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/20 text-sm transition-all"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-zinc-950 font-bold uppercase tracking-wider text-xs rounded-xl shadow-lg shadow-emerald-950/50 transition-all active:scale-95 disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}