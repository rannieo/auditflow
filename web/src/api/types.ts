export type ValidationStatus = 'passed' | 'failed' | 'duplicate'

export interface BatchSummary {
  batch_id: string
  filename: string
  total_records: number
  passed_records: number
  failed_records: number
  duplicate_records: number
  created_at: string
}

export interface BatchRecord {
  id: number
  client_name: string | null
  email: string | null
  amount: number | null
  service_type: string | null
  status: string | null
  date: string | null
  validation_status: ValidationStatus
  validation_errors: string[]
}

export interface BatchDetail {
  summary: BatchSummary
  records: BatchRecord[]
}

export interface AiSummaryResponse {
  summary: string
}

export interface IntegrationResponse {
  status: string
  message: string
}

export type IntegrationName = 'salesforce' | 'sharepoint' | 'monday'

export interface AuditLog {
  id: number
  action: string
  actor: string
  status: string
  metadata: Record<string, unknown>
  created_at: string
}
