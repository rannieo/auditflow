export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? '/api',
  appTitle: import.meta.env.VITE_APP_TITLE ?? 'AuditFlow AI Lite',
} as const
