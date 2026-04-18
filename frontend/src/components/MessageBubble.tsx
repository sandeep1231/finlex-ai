'use client';

import ReactMarkdown from 'react-markdown';
import { ChatMessage } from '@/lib/api';
import {
  User,
  Scale,
  Wrench,
  BookOpen,
  AlertTriangle,
  Info,
} from 'lucide-react';

interface MessageBubbleProps {
  message: ChatMessage;
  onRetry?: () => void;
}

export default function MessageBubble({ message, onRetry }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isError = message.tool_used === '__error__';

  return (
    <div
      className={`flex items-start gap-2 sm:gap-3 message-enter ${
        isUser ? 'flex-row-reverse' : ''
      }`}
    >
      {/* Avatar */}
      <div
        className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center shrink-0 ${
          isUser
            ? 'bg-primary-100'
            : 'bg-accent-100'
        }`}
      >
        {isUser ? (
          <User className="text-primary-600" size={14} />
        ) : (
          <Scale className="text-accent-600" size={14} />
        )}
      </div>

      {/* Message Content */}
      <div
        className={`max-w-[88%] sm:max-w-[80%] rounded-2xl px-3 py-2.5 sm:px-4 sm:py-3 ${
          isUser
            ? 'bg-primary-600 text-white rounded-tr-sm'
            : isError
            ? 'bg-red-50 border border-red-200 rounded-tl-sm'
            : 'bg-white border border-slate-200 rounded-tl-sm'
        }`}
      >
        {/* Tool Used Badge */}
        {message.tool_used && message.tool_used !== '__error__' && (
          <div className="flex items-center gap-1.5 mb-2 text-xs">
            <Wrench size={12} className="text-amber-500" />
            <span className="text-amber-600 font-medium bg-amber-50 px-2 py-0.5 rounded-full">
              Used: {message.tool_used.replace(/_/g, ' ')}
            </span>
          </div>
        )}

        {/* Error Icon */}
        {isError && (
          <div className="flex items-center gap-1.5 mb-2 text-xs">
            <AlertTriangle size={12} className="text-red-500" />
            <span className="text-red-600 font-medium">Error</span>
          </div>
        )}

        {/* Message Text */}
        {isUser ? (
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className={`markdown-content text-sm ${isError ? 'text-red-700' : 'text-slate-800'}`}>
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {/* Retry Button for Errors */}
        {isError && onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 text-xs text-red-600 hover:text-red-800 font-medium underline"
          >
            Try again
          </button>
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

        {/* Disclaimer for AI messages (non-error) */}
        {!isUser && !isError && message.content.length > 100 && (
          <div className="mt-3 pt-2 border-t border-slate-100 flex items-start gap-1.5">
            <Info size={11} className="text-slate-300 shrink-0 mt-0.5" />
            <p className="text-[10px] text-slate-400 leading-snug">
              AI-generated. Verify with a qualified CA/Advocate before acting.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
