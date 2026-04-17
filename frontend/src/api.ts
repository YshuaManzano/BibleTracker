import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE = process.env.EXPO_PUBLIC_BACKEND_URL;

async function getToken(): Promise<string | null> {
  return AsyncStorage.getItem('auth_token');
}

async function request(path: string, options: RequestInit = {}): Promise<any> {
  const token = await getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api${path}`, { ...options, headers });
  if (res.status === 401) {
    await AsyncStorage.removeItem('auth_token');
    throw new Error('Session expired');
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail));
  }
  return res.json();
}

export const api = {
  // Auth
  register: (name: string, email: string, password: string) =>
    request('/auth/register', { method: 'POST', body: JSON.stringify({ name, email, password }) }),
  login: (email: string, password: string) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  getMe: () => request('/auth/me'),

  // Bible
  getBooks: () => request('/bible/books'),
  getChapter: (version: string, bookSlug: string, chapter: number) =>
    request(`/bible/chapter/${version}/${bookSlug}/${chapter}`),
  getDailyVerse: () => request('/bible/daily-verse'),

  // Plans
  getPlans: () => request('/plans'),
  activatePlan: (planId: string) => request(`/plans/activate/${planId}`, { method: 'POST' }),
  getActivePlans: () => request('/plans/active'),
  getUserPlan: (planDocId: string) => request(`/plans/user/${planDocId}`),

  // Progress
  markRead: (planId: string, bookSlug: string, chapter: number) =>
    request('/progress/mark-read', { method: 'POST', body: JSON.stringify({ plan_id: planId, book_slug: bookSlug, chapter }) }),
  getHeatmap: () => request('/progress/heatmap'),
  getStreak: () => request('/progress/streak'),
  useGraceDay: () => request('/progress/use-grace-day', { method: 'POST' }),
  getBooksStatus: () => request('/progress/books-status'),

  // Plans management
  recalculatePlan: (planId: string) =>
    request('/plans/recalculate', { method: 'POST', body: JSON.stringify({ plan_id: planId }) }),

  // Notes
  createNote: (bookSlug: string, chapter: number, text: string) =>
    request('/notes', { method: 'POST', body: JSON.stringify({ book_slug: bookSlug, chapter, text }) }),
  getNotes: (bookSlug?: string, chapter?: number) => {
    let path = '/notes';
    const params: string[] = [];
    if (bookSlug) params.push(`book_slug=${bookSlug}`);
    if (chapter !== undefined) params.push(`chapter=${chapter}`);
    if (params.length) path += '?' + params.join('&');
    return request(path);
  },
  updateNote: (noteId: string, text: string) =>
    request(`/notes/${noteId}`, { method: 'PUT', body: JSON.stringify({ text }) }),
  deleteNote: (noteId: string) =>
    request(`/notes/${noteId}`, { method: 'DELETE' }),

  // AI
  getSummary: (bookSlug: string, chapter: number) =>
    request(`/ai/summary/${bookSlug}/${chapter}`),
  getMoodSuggestions: () => request('/ai/mood-suggestions'),

  // Badges
  getBadges: () => request('/badges'),

  // Dashboard
  getDashboard: () => request('/dashboard'),

  // Settings
  getSettings: () => request('/settings'),
  updateTheme: (theme: string) =>
    request('/settings/theme', { method: 'PUT', body: JSON.stringify({ theme }) }),
};
