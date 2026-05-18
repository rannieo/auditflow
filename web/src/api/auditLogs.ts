import { getJson } from './client'
import type { AuditLog } from './types'

export const listAuditLogs = (limit = 50) =>
  getJson<AuditLog[]>(`/audit-logs?limit=${limit}`)
