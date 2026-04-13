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
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(false);

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
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-72' : 'w-0'
        } transition-all duration-300 overflow-hidden`}
      >
        <Sidebar
          conversations={conversations}
          activeId={activeConversationId}
          onNewChat={handleNewChat}
          onSelect={handleSelectConversation}
          onDelete={handleDeleteConversation}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-slate-200 bg-white">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-slate-100 rounded-lg transition"
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <h1 className="text-lg font-bold text-slate-800">
              FinLex AI
            </h1>
          </div>

          {/* Mode Switcher */}
          <div className="flex items-center gap-1 bg-slate-100 rounded-lg p-1">
            {(Object.entries(MODE_CONFIG) as [Mode, typeof MODE_CONFIG.general][]).map(
              ([key, config]) => {
                const Icon = config.icon;
                return (
                  <button
                    key={key}
                    onClick={() => setMode(key)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition ${
                      mode === key
                        ? 'bg-white text-slate-800 shadow-sm'
                        : 'text-slate-500 hover:text-slate-700'
                    }`}
                  >
                    <Icon size={16} />
                    {config.label}
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
