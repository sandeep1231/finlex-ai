'use client';

import ReactMarkdown from 'react-markdown';
import { ChatMessage } from '@/lib/api';
import {
  User,
  Scale,
  Calculator,
  FileText,
  Wrench,
  BookOpen,
} from 'lucide-react';

interface MessageBubbleProps {
  message: ChatMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex items-start gap-3 message-enter ${
        isUser ? 'flex-row-reverse' : ''
      }`}
    >
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
          isUser
            ? 'bg-primary-100'
            : 'bg-accent-100'
        }`}
      >
        {isUser ? (
          <User className="text-primary-600" size={16} />
        ) : (
          <Scale className="text-accent-600" size={16} />
        )}
      </div>

      {/* Message Content */}
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-primary-600 text-white rounded-tr-sm'
            : 'bg-white border border-slate-200 rounded-tl-sm'
        }`}
      >
        {/* Tool Used Badge */}
        {message.tool_used && (
          <div className="flex items-center gap-1.5 mb-2 text-xs">
            <Wrench size={12} className="text-amber-500" />
            <span className="text-amber-600 font-medium bg-amber-50 px-2 py-0.5 rounded-full">
              Used: {message.tool_used.replace(/_/g, ' ')}
            </span>
          </div>
        )}

        {/* Message Text */}
        {isUser ? (
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="markdown-content text-sm text-slate-800">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {/* Sources */}
        {message.sources?.references && message.sources.references.length > 0 && (
          <div className="mt-3 pt-2 border-t border-slate-100">
            <div className="flex items-center gap-1 text-xs text-slate-500 mb-1">
              <BookOpen size={12} />
              <span className="font-medium">Sources</span>
            </div>
            {message.sources.references.map((ref, idx) => (
              <div
                key={idx}
                className="text-xs text-slate-400 bg-slate-50 px-2 py-1 rounded mt-1"
              >
                {ref.document}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
