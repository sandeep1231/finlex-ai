'use client';

import { useState, useEffect } from 'react';
import { UserButton } from '@clerk/nextjs';
import Sidebar from './Sidebar';
import ChatPanel from './ChatPanel';
import { api, Conversation } from '@/lib/api';
import {
  Menu,
  Scale,
  Calculator,
  FileText,
  X,
} from 'lucide-react';

type Mode = 'general' | 'accounting' | 'legal';

const MODE_CONFIG = {
  general: { label: 'General', icon: Scale, color: 'bg-primary-500' },
  accounting: { label: 'Accounting', icon: Calculator, color: 'bg-emerald-500' },
  legal: { label: 'Legal', icon: FileText, color: 'bg-amber-500' },
};

export default function ChatLayout() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>('general');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const mql = window.matchMedia('(max-width: 768px)');
    const onChange = (e: MediaQueryListEvent | MediaQueryList) => {
      setIsMobile(e.matches);
      if (!e.matches) setSidebarOpen(true); // auto-open on desktop
    };
    onChange(mql);
    mql.addEventListener('change', onChange);
    return () => mql.removeEventListener('change', onChange);
  }, []);

  useEffect(() => {
    loadConversations();
  }, []);

  async function loadConversations() {
    try {
      const convos = await api.getConversations();
      setConversations(convos);
    } catch {
      // User might not be registered yet — that's okay
    }
  }

  function handleNewChat() {
    setActiveConversationId(null);
  }

  function handleSelectConversation(id: string) {
    setActiveConversationId(id);
    const convo = conversations.find(c => c.id === id);
    if (convo) {
      setMode(convo.mode as Mode);
    }
    if (isMobile) setSidebarOpen(false);
  }

  async function handleDeleteConversation(id: string) {
    try {
      await api.deleteConversation(id);
      setConversations(prev => prev.filter(c => c.id !== id));
      if (activeConversationId === id) {
        setActiveConversationId(null);
      }
    } catch {
      // silently fail
    }
  }

  function handleConversationCreated(id: string, title: string) {
    const newConvo: Conversation = {
      id,
      title,
      mode,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    setConversations(prev => [newConvo, ...prev]);
    setActiveConversationId(id);
  }

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Mobile Backdrop */}
      {isMobile && sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-20"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar — overlay on mobile, inline on desktop */}
      <div
        className={`
          ${isMobile ? 'fixed inset-y-0 left-0 z-30' : 'relative'}
          ${sidebarOpen ? 'w-72' : 'w-0'}
          transition-all duration-300 overflow-hidden
        `}
      >
        <Sidebar
          conversations={conversations}
          activeId={activeConversationId}
          onNewChat={() => { handleNewChat(); if (isMobile) setSidebarOpen(false); }}
          onSelect={handleSelectConversation}
          onDelete={handleDeleteConversation}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between px-3 py-2.5 sm:px-4 sm:py-3 border-b border-slate-200 bg-white gap-2">
          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-slate-100 rounded-lg transition"
            >
              {sidebarOpen && !isMobile ? <X size={20} /> : <Menu size={20} />}
            </button>
            <h1 className="text-base sm:text-lg font-bold text-slate-800 hidden sm:block">
              FinLex AI
            </h1>
          </div>

          {/* Mode Switcher — icon-only on mobile */}
          <div className="flex items-center gap-0.5 sm:gap-1 bg-slate-100 rounded-lg p-0.5 sm:p-1">
            {(Object.entries(MODE_CONFIG) as [Mode, typeof MODE_CONFIG.general][]).map(
              ([key, config]) => {
                const Icon = config.icon;
                return (
                  <button
                    key={key}
                    onClick={() => setMode(key)}
                    className={`flex items-center gap-1.5 px-2 py-1.5 sm:px-3 rounded-md text-sm font-medium transition ${
                      mode === key
                        ? 'bg-white text-slate-800 shadow-sm'
                        : 'text-slate-500 hover:text-slate-700'
                    }`}
                    title={config.label}
                  >
                    <Icon size={16} />
                    <span className="hidden sm:inline">{config.label}</span>
                  </button>
                );
              }
            )}
          </div>

          <UserButton afterSignOutUrl="/sign-in" />
        </header>

        {/* Chat Area */}
        <ChatPanel
          conversationId={activeConversationId}
          mode={mode}
          onConversationCreated={handleConversationCreated}
        />
      </div>
    </div>
  );
}
