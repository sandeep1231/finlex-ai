'use client';

import { useState, useRef } from 'react';
import { Conversation, api } from '@/lib/api';
import {
  MessageSquarePlus,
  MessageSquare,
  Trash2,
  Scale,
  Calculator,
  FileText,
  Upload,
  File,
  Loader2,
  CheckCircle,
  X,
} from 'lucide-react';

interface SidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  onNewChat: () => void;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
}

interface UploadedDoc {
  id: string;
  filename: string;
  category: string;
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
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [documents, setDocuments] = useState<UploadedDoc[]>([]);
  const [showDocs, setShowDocs] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadStatus(null);

    try {
      const result = await api.uploadDocument(file, 'general');
      setUploadStatus(`✓ ${file.name} uploaded`);
      setDocuments(prev => [...prev, { id: result.id, filename: file.name, category: 'general' }]);
      setTimeout(() => setUploadStatus(null), 3000);
    } catch (err: any) {
      setUploadStatus(`✗ ${err.message || 'Upload failed'}`);
      setTimeout(() => setUploadStatus(null), 5000);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  }

  async function loadDocuments() {
    try {
      const docs = await api.getDocuments();
      setDocuments(Array.isArray(docs) ? docs : []);
    } catch {
      // ignore
    }
  }

  async function handleDeleteDoc(id: string) {
    try {
      await api.deleteDocument(id);
      setDocuments(prev => prev.filter(d => d.id !== id));
    } catch {
      // ignore
    }
  }
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

      {/* Document Upload Section */}
      <div className="px-3 py-2 border-t border-slate-700">
        {/* Hidden file input — always rendered so ref is stable */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.doc,.xlsx,.xls,.csv,.txt,.jpg,.jpeg,.png,.webp,.heic,.heif"
          onChange={handleFileUpload}
          className="hidden"
        />

        <button
          onClick={() => {
            setShowDocs(!showDocs);
            if (!showDocs && documents.length === 0) loadDocuments();
          }}
          className="flex items-center gap-2 w-full px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition"
        >
          <File size={16} className="text-slate-400" />
          <span>Documents</span>
          <span className="ml-auto text-xs text-slate-500">{documents.length || ''}</span>
        </button>

        {showDocs && (
          <div className="mt-1 space-y-1">
            {documents.map(doc => (
              <div key={doc.id} className="flex items-center gap-2 px-3 py-1.5 text-xs text-slate-400 group">
                <FileText size={12} className="shrink-0" />
                <span className="truncate flex-1">{doc.filename}</span>
                <button
                  onClick={() => handleDeleteDoc(doc.id)}
                  className="opacity-0 group-hover:opacity-100 p-0.5 hover:text-red-400 transition"
                >
                  <X size={12} />
                </button>
              </div>
            ))}

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="flex items-center gap-2 w-full px-3 py-2 text-xs text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
            >
              {uploading ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  <span>Uploading...</span>
                </>
              ) : (
                <>
                  <Upload size={14} />
                  <span>Upload Document</span>
                </>
              )}
            </button>

            {uploadStatus && (
              <div className={`px-3 py-1.5 text-xs rounded ${
                uploadStatus.startsWith('✓') ? 'text-emerald-400' : 'text-red-400'
              }`}>
                {uploadStatus}
              </div>
            )}
          </div>
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
