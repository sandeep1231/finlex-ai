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
  IndianRupee,
  FileCheck,
  BarChart3,
  RefreshCw,
} from 'lucide-react';

interface ChatPanelProps {
  conversationId: string | null;
  mode: string;
  onConversationCreated: (id: string, title: string) => void;
}

const QUICK_ACTIONS: Record<string, Array<{ icon: typeof Calculator; label: string; prompt: string; color: string }>> = {
  general: [
    { icon: Calculator, label: 'Income Tax', prompt: 'Calculate income tax for ₹15 lakh salary under new regime for FY 2025-26', color: 'text-emerald-600 bg-emerald-50 border-emerald-200' },
    { icon: Scale, label: 'Compare Regimes', prompt: 'Compare old vs new tax regime for ₹20L income with ₹2.5L in 80C deductions', color: 'text-blue-600 bg-blue-50 border-blue-200' },
    { icon: IndianRupee, label: 'GST Calculator', prompt: 'Calculate GST at 18% on a service worth ₹1,00,000', color: 'text-purple-600 bg-purple-50 border-purple-200' },
    { icon: FileText, label: 'Draft NDA', prompt: 'Draft an NDA between two companies for a consulting engagement', color: 'text-amber-600 bg-amber-50 border-amber-200' },
    { icon: FileCheck, label: 'TDS Calculator', prompt: 'Calculate TDS on professional fees of ₹50,000 under section 194J', color: 'text-rose-600 bg-rose-50 border-rose-200' },
    { icon: BarChart3, label: 'Financial Ratios', prompt: 'Calculate financial ratios: revenue 50L, net income 8L, total assets 30L, total liabilities 12L, current assets 15L, current liabilities 8L, inventory 5L', color: 'text-teal-600 bg-teal-50 border-teal-200' },
  ],
  accounting: [
    { icon: Calculator, label: 'Income Tax', prompt: 'Calculate income tax for ₹25 lakh salary under new regime for FY 2025-26', color: 'text-emerald-600 bg-emerald-50 border-emerald-200' },
    { icon: Scale, label: 'Compare Regimes', prompt: 'Compare old vs new tax regime for ₹18L income with ₹3L deductions under 80C, 80D, and 80CCD(1B)', color: 'text-blue-600 bg-blue-50 border-blue-200' },
    { icon: IndianRupee, label: 'Advance Tax', prompt: 'Calculate advance tax schedule for estimated annual tax liability of ₹3,00,000', color: 'text-purple-600 bg-purple-50 border-purple-200' },
    { icon: FileCheck, label: 'TDS on Rent', prompt: 'Calculate TDS on monthly rent of ₹60,000 paid to an individual landlord', color: 'text-rose-600 bg-rose-50 border-rose-200' },
    { icon: BarChart3, label: 'Depreciation', prompt: 'Calculate depreciation for a computer worth ₹1,50,000 using WDV method at 40% for 5 years', color: 'text-teal-600 bg-teal-50 border-teal-200' },
    { icon: FileText, label: 'Section 80C', prompt: 'What are all the deductions available under Section 80C, 80D, and 80CCD(1B) for FY 2025-26?', color: 'text-amber-600 bg-amber-50 border-amber-200' },
  ],
  legal: [
    { icon: FileText, label: 'Legal Notice', prompt: 'Draft a legal notice for breach of contract for non-payment of ₹5,00,000 for services rendered', color: 'text-amber-600 bg-amber-50 border-amber-200' },
    { icon: FileCheck, label: 'Board Resolution', prompt: 'Draft a board resolution for appointment of a new director under Companies Act 2013', color: 'text-blue-600 bg-blue-50 border-blue-200' },
    { icon: Scale, label: 'Engagement Letter', prompt: 'Draft a CA engagement letter for statutory audit of a private limited company', color: 'text-emerald-600 bg-emerald-50 border-emerald-200' },
    { icon: FileText, label: 'Draft NDA', prompt: 'Draft a non-disclosure agreement with 3-year confidentiality period and Delhi jurisdiction', color: 'text-purple-600 bg-purple-50 border-purple-200' },
    { icon: Calculator, label: 'BNS 2023', prompt: 'What are the key changes in Bharatiya Nyaya Sanhita 2023 compared to the Indian Penal Code?', color: 'text-rose-600 bg-rose-50 border-rose-200' },
    { icon: BarChart3, label: 'DPDP Act', prompt: 'Explain the key compliance requirements under the Digital Personal Data Protection Act 2023', color: 'text-teal-600 bg-teal-50 border-teal-200' },
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
  const justCreatedIdRef = useRef<string | null>(null);

  // Load conversation messages when conversation changes
  useEffect(() => {
    setCurrentConvoId(conversationId);
    if (conversationId && conversationId !== justCreatedIdRef.current) {
      // Only load from server if this conversation wasn't just created locally
      loadConversation(conversationId);
    } else if (!conversationId) {
      setMessages([]);
    }
    justCreatedIdRef.current = null;
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
        justCreatedIdRef.current = response.conversation_id;
        onConversationCreated(response.conversation_id, text.slice(0, 100));
      }
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `⚠️ ${err.message || 'Something went wrong'}. Please try again.`,
        tool_used: '__error__',
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

  const actions = QUICK_ACTIONS[mode] || QUICK_ACTIONS.general;

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-3 py-4 sm:px-4 sm:py-6">
        {messages.length === 0 ? (
          <div className="max-w-2xl mx-auto mt-6 sm:mt-12">
            <div className="text-center mb-6 sm:mb-8">
              <div className="flex justify-center mb-3 sm:mb-4">
                <div className="w-12 h-12 sm:w-16 sm:h-16 bg-primary-100 rounded-2xl flex items-center justify-center">
                  <Sparkles className="text-primary-600" size={28} />
                </div>
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-800 mb-2">
                What can I help you with?
              </h2>
              <p className="text-sm sm:text-base text-slate-500">
                Choose a quick action or type your question.
              </p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-3">
              {actions.map((action, idx) => {
                const Icon = action.icon;
                return (
                  <button
                    key={idx}
                    onClick={() => handleSend(action.prompt)}
                    className={`flex flex-col items-center gap-1.5 sm:gap-2 p-3 sm:p-4 border rounded-xl hover:shadow-md transition text-center ${action.color}`}
                  >
                    <Icon size={22} />
                    <span className="text-xs sm:text-sm font-medium">{action.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((msg, idx) => (
              <MessageBubble
                key={idx}
                message={msg}
                onRetry={
                  msg.tool_used === '__error__' && idx === messages.length - 1
                    ? () => {
                        // Find the last user message and retry
                        const lastUserMsg = [...messages].reverse().find(m => m.role === 'user');
                        if (lastUserMsg) {
                          setMessages(prev => prev.filter((_, i) => i !== idx));
                          handleSend(lastUserMsg.content);
                        }
                      }
                    : undefined
                }
              />
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
      <div className="border-t border-slate-200 bg-white px-3 py-2 sm:px-4 sm:py-3 pb-[env(safe-area-inset-bottom,8px)]">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-xl px-3 sm:px-4 py-2 focus-within:border-primary-400 focus-within:ring-2 focus-within:ring-primary-100 transition">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask about ${mode === 'accounting' ? 'tax, GST, TDS...' : mode === 'legal' ? 'contracts, compliance...' : 'accounting or legal...'}`}
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
          <p className="text-xs text-slate-400 text-center mt-1.5 sm:mt-2 hidden sm:block">
            AI-generated responses. Verify with a qualified professional before acting on this information.
          </p>
        </div>
      </div>
    </div>
  );
}
