const API_BASE = '/api';

async function fetchApi(endpoint: string, options?: RequestInit) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: { message: 'Unknown error' } }));
    throw new Error(error.error?.message || `HTTP ${response.status}`);
  }

  return response.json();
}

// Settings API
export const settingsApi = {
  get: () => fetchApi('/settings'),
  saveJira: (data: { baseUrl: string; username: string; apiToken: string }) =>
    fetchApi('/settings/jira', { method: 'POST', body: JSON.stringify(data) }),
  saveLLM: (data: { provider: string; groq?: any; ollama?: any }) =>
    fetchApi('/settings/llm', { method: 'POST', body: JSON.stringify(data) }),
  testJira: () => fetchApi('/settings/jira/test'),
  testGroq: () => fetchApi('/settings/llm/groq/test'),
  testOllama: () => fetchApi('/settings/llm/ollama/test'),
  getOllamaModels: () => fetchApi('/settings/llm/ollama/models'),
};

// JIRA API
export const jiraApi = {
  fetchTicket: (ticketId: string) =>
    fetchApi('/jira/fetch', { method: 'POST', body: JSON.stringify({ ticketId }) }),
  getRecent: () => fetchApi('/jira/recent'),
};

// Templates API
export const templatesApi = {
  list: () => fetchApi('/templates'),
  get: (id: string) => fetchApi(`/templates/${id}`),
  upload: (file: File, name: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);
    return fetch(`${API_BASE}/templates/upload`, {
      method: 'POST',
      body: formData,
    }).then((r) => r.json());
  },
  delete: (id: string) => fetchApi(`/templates/${id}`, { method: 'DELETE' }),
};

// Test Plan API
export const testPlanApi = {
  generate: (data: { ticketId: string; templateId?: string; provider?: string }) =>
    fetchApi('/testplan/generate', { method: 'POST', body: JSON.stringify(data) }),
  getHistory: () => fetchApi('/testplan/history'),
  getHistoryItem: (id: string) => fetchApi(`/testplan/history/${id}`),
};
