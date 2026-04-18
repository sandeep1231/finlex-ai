const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function apiFetch(path: string, options: RequestInit = {}) {
  const token = await (window as any).Clerk?.session?.getToken();
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: { references: Array<{ document: string; chunk: string; relevance_score: number }> };
  tool_used?: string;
  created_at?: string;
}

export interface Conversation {
  id: string;
  title: string;
  mode: string;
  created_at: string;
  updated_at: string;
  messages?: ChatMessage[];
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  sources: Array<{ document: string; chunk: string; relevance_score: number }>;
  tool_used?: string;
  tokens_used: number;
  disclaimer: string;
}

export const api = {
  // Chat
  sendMessage: (message: string, conversationId?: string, mode = 'general') =>
    apiFetch('/api/v1/chat/', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId, mode }),
    }) as Promise<ChatResponse>,

  getConversations: () =>
    apiFetch('/api/v1/chat/conversations') as Promise<Conversation[]>,

  getConversation: (id: string) =>
    apiFetch(`/api/v1/chat/conversations/${id}`) as Promise<Conversation>,

  deleteConversation: (id: string) =>
    apiFetch(`/api/v1/chat/conversations/${id}`, { method: 'DELETE' }),

  // Documents
  uploadDocument: async (file: File, category = 'general', description = '') => {
    const token = await (window as any).Clerk?.session?.getToken();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    if (description) formData.append('description', description);

    const res = await fetch(`${API_BASE}/api/v1/documents/upload`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || error.message || `Upload failed (${res.status})`);
    }
    return res.json();
  },

  getDocuments: async () => {
    const res = await apiFetch('/api/v1/documents/');
    return res.documents || [];
  },

  deleteDocument: (id: string) =>
    apiFetch(`/api/v1/documents/${id}`, { method: 'DELETE' }),

  // Calculators
  calculateIncomeTax: (data: any) =>
    apiFetch('/api/v1/calculator/income-tax', { method: 'POST', body: JSON.stringify(data) }),

  calculateGST: (data: any) =>
    apiFetch('/api/v1/calculator/gst', { method: 'POST', body: JSON.stringify(data) }),

  calculateTDS: (data: any) =>
    apiFetch('/api/v1/calculator/tds', { method: 'POST', body: JSON.stringify(data) }),

  compareRegimes: (data: any) =>
    apiFetch('/api/v1/calculator/compare-regimes', { method: 'POST', body: JSON.stringify(data) }),

  // Auth
  getProfile: () => apiFetch('/api/v1/auth/me'),
  getTenant: () => apiFetch('/api/v1/auth/tenant'),

  // Admin
  getDashboard: () => apiFetch('/api/v1/admin/dashboard'),
};
