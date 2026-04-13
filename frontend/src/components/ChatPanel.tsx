'use client';

import { useState, useRef, useEffect } from 'react';
import { api, ChatMessage, ChatResponse } from '@/lib/api';
import MessageBubble from './MessageBubble';
import {
  Send,
  Loader2,
  Calculator,
  Scale,
  FileText,
  Sparkles,
} from 'lucide-react';

interface ChatPanelProps {
  conversationId: string | null;
  mode: string;
  onConversationCreated: (id: string, title: string) => void;
}

const WELCOME_SUGGESTIONS: Record<string, string[]> = {
  general: [
    'Calculate income tax for ₹15 lakh salary under new regime',
    'What are the GST rates for professional services?',
    'Draft an NDA between two companies',
    'What are the ITR filing due dates for FY 2025-26?',
  ],
  accounting: [
    'Compare old vs new tax regime for ₹20L income with ₹2.5L deductions',
    'Calculate TDS on rent of ₹60,000/month',
    'What deductions are available under Section 80C?',
    'Explain the advance tax installment schedule',
  ],
  legal: [
    'Draft a legal notice for breach of contract',
    'What are the key clauses in an employment agreement?',
    'Explain non-compete enforceability in India',
    'What changed with Bharatiya Nyaya Sanhita 2023?',
  ],
};

export default function ChatPanel({
  conversationId,
  mode,
  onConversationCreated,
}: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentConvoId, setCurrentConvoId] = useState<string | null>(conversationId);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Load conversation messages when conversation changes
  useEffect(() => {
    setCurrentConvoId(conversationId);
    if (conversationId) {
      loadConversation(conversationId);
    } else {
      setMessages([]);
    }
  }, [conversationId]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function loadConversation(id: string) {
    try {
      const convo = await api.getConversation(id);
      setMessages(convo.messages || []);
    } catch {
      setMessages([]);
    }
  }

  async function handleSend(messageText?: string) {
    const text = messageText || input.trim();
    if (!text || isLoading) return;

    const userMessage: ChatMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response: ChatResponse = await api.sendMessage(
        text,
        currentConvoId || undefined,
        mode
      );

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
        tool_used: response.tool_used || undefined,
        sources: response.sources?.length
          ? { references: response.sources }
          : undefined,
      };

      setMessages(prev => [...prev, assistantMessage]);

      // If new conversation, notify parent
      if (!currentConvoId) {
        setCurrentConvoId(response.conversation_id);
        onConversationCreated(response.conversation_id, text.slice(0, 100));
      }
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Sorry, an error occurred: ${err.message}. Please try again.`,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  const suggestions = WELCOME_SUGGESTIONS[mode] || WELCOME_SUGGESTIONS.general;

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {messages.length === 0 ? (
          <div className="max-w-2xl mx-auto text-center mt-16">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center">
                <Sparkles className="text-primary-600" size={32} />
              </div>
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-2">
              Welcome to FinLex AI
            </h2>
            <p className="text-slate-500 mb-8">
              Your AI assistant for Indian Accounting & Law.
              Ask me anything about taxes, GST, legal drafting, compliance, and more.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {suggestions.map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(suggestion)}
                  className="text-left p-4 bg-white border border-slate-200 rounded-xl hover:border-primary-300 hover:shadow-sm transition text-sm text-slate-700"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((msg, idx) => (
              <MessageBubble key={idx} message={msg} />
            ))}

            {isLoading && (
              <div className="flex items-start gap-3 message-enter">
                <div className="w-8 h-8 bg-accent-100 rounded-full flex items-center justify-center shrink-0">
                  <Scale className="text-accent-600" size={16} />
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm px-4 py-3">
                  <div className="flex gap-1.5">
                    <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full" />
                    <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full" />
                    <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-200 bg-white px-4 py-3">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 focus-within:border-primary-400 focus-within:ring-2 focus-within:ring-primary-100 transition">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask about ${mode === 'accounting' ? 'tax, GST, TDS...' : mode === 'legal' ? 'contracts, compliance, legal drafting...' : 'accounting or legal queries...'}`}
              className="flex-1 bg-transparent resize-none outline-none text-sm text-slate-800 placeholder-slate-400 max-h-32"
              rows={1}
              disabled={isLoading}
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || isLoading}
              className="p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-40 disabled:cursor-not-allowed transition shrink-0"
            >
              {isLoading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Send size={18} />
              )}
            </button>
          </div>
          <p className="text-xs text-slate-400 text-center mt-2">
            AI-generated responses. Verify with a qualified professional before acting on this information.
          </p>
        </div>
      </div>
    </div>
  );
}
