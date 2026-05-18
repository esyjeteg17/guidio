import { useApi } from '~/composables/useApi'

export interface ChatMessage {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  payload: any | null
  reaction?: 'like' | 'dislike' | null
  created_at: string
}

export interface ChatSession {
  id: number
  mode: 'fonts' | 'moodboard' | 'colors' | 'free'
  title: string
  project: number | null
  messages: ChatMessage[]
  created_at: string
  updated_at: string
}

export interface ChatSummary {
  id: number
  mode: string
  title: string
  project: number | null
  last_message: { role: string; content: string } | null
  messages_count: number
  created_at: string
  updated_at: string
}

export type ChatFilters = Record<string, string>

export function useChat() {
  const api = useApi()

  return {
    async list(mode?: string, project?: number | string) {
      const qs: string[] = []
      if (mode) qs.push(`mode=${mode}`)
      if (project) qs.push(`project=${project}`)
      const query = qs.length ? `?${qs.join('&')}` : ''
      const data = await api.get<{ results: ChatSummary[] } | ChatSummary[]>(`/ai/sessions/${query}`)
      return Array.isArray(data) ? data : data.results
    },
    get: (id: number | string) => api.get<ChatSession>(`/ai/sessions/${id}/`),
    create: (mode: string, project?: number | null) =>
      api.post<ChatSession>('/ai/sessions/', { mode, project: project ?? null }),
    send: (id: number | string, content: string, filters?: ChatFilters) =>
      api.post<{ message: ChatMessage; session: ChatSession }>(
        `/ai/sessions/${id}/send/`,
        { content, filters: filters && Object.keys(filters).length ? filters : undefined },
      ),
    quickGenerate: (
      mode: string,
      content: string,
      options: { project?: number | null; filters?: ChatFilters } = {},
    ) =>
      api.post<{ session: ChatSession; message: ChatMessage }>('/ai/generate/', {
        mode,
        content,
        project: options.project ?? undefined,
        filters: options.filters && Object.keys(options.filters).length ? options.filters : undefined,
      }),
    remove: (id: number | string) => api.delete(`/ai/sessions/${id}/`),
  }
}
