'use client';

import { Conversation } from '@/lib/api';
import {
  MessageSquarePlus,
  MessageSquare,
  Trash2,
  Scale,
  Calculator,
  FileText,
  Upload,
} from 'lucide-react';

interface SidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  onNewChat: () => void;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
}

const MODE_ICONS: Record<string, typeof Scale> = {
  general: Scale,
  accounting: Calculator,
  legal: FileText,
};

export default function Sidebar({
  conversations,
  activeId,
  onNewChat,
  onSelect,
  onDelete,
}: SidebarProps) {
  return (
    <div className="flex flex-col h-full bg-slate-900 text-slate-200">
      {/* Logo */}
      <div className="px-4 py-4 border-b border-slate-700">
        <div className="flex items-center gap-2">
          <Scale className="text-primary-400" size={24} />
          <span className="text-lg font-bold text-white">FinLex AI</span>
        </div>
        <p className="text-xs text-slate-400 mt-1">Accounting & Law Assistant</p>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="flex items-center gap-2 w-full px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition font-medium text-sm"
        >
          <MessageSquarePlus size={18} />
          New Conversation
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto px-2">
        <p className="px-2 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Recent Chats
        </p>
        {conversations.length === 0 ? (
          <p className="px-3 py-4 text-sm text-slate-500 text-center">
            No conversations yet.
            <br />Start a new chat!
          </p>
        ) : (
          conversations.map((convo) => {
            const Icon = MODE_ICONS[convo.mode] || MessageSquare;
            return (
              <div
                key={convo.id}
                className={`group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer mb-0.5 transition ${
                  activeId === convo.id
                    ? 'bg-slate-700 text-white'
                    : 'hover:bg-slate-800 text-slate-300'
                }`}
                onClick={() => onSelect(convo.id)}
              >
                <Icon size={16} className="shrink-0 text-slate-400" />
                <span className="flex-1 truncate text-sm">
                  {convo.title}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(convo.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-600 rounded transition"
                >
                  <Trash2 size={14} className="text-slate-400" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-slate-700">
        <div className="text-xs text-slate-500 text-center">
          FY 2025-26 • Indian Tax & Law
        </div>
      </div>
    </div>
  );
}
