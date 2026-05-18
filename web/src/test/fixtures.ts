import type {
  AuditLog,
  BatchDetail,
  BatchRecord,
  BatchSummary,
} from '@/api/types'

export const sampleSummary: BatchSummary = {
  batch_id: 'batch_test01',
  filename: 'sample.csv',
  total_records: 4,
  passed_records: 1,
  failed_records: 2,
  duplicate_records: 1,
  created_at: '2026-05-18T10:00:00.000000',
}

export const sampleRecords: BatchRecord[] = [
  {
    id: 1,
    client_name: 'Acme Inc',
    email: 'ops@acme.com',
    amount: 1500,
    service_type: 'tax_filing',
    status: 'pending',
    date: '2026-05-18',
    validation_status: 'passed',
    validation_errors: [],
  },
  {
    id: 2,
    client_name: 'XYZ LLC',
    email: null,
    amount: 8000,
    service_type: 'audit_review',
    status: 'pending',
    date: '2026-05-18',
    validation_status: 'failed',
    validation_errors: ['email is required'],
  },
  {
    id: 3,
    client_name: 'Dup Corp',
    email: 'dup@x.co',
    amount: 100,
    service_type: 'tax_filing',
    status: 'pending',
    date: '2026-05-18',
    validation_status: 'duplicate',
    validation_errors: ['duplicate record'],
  },
  {
    id: 4,
    client_name: 'Bad',
    email: 'b@b.co',
    amount: -50,
    service_type: 'tax_filing',
    status: 'pending',
    date: '2026-05-18',
    validation_status: 'failed',
    validation_errors: ['amount must be greater than 0'],
  },
]

export const sampleDetail: BatchDetail = {
  summary: sampleSummary,
  records: sampleRecords,
}

export const sampleAuditLog: AuditLog = {
  id: 1,
  action: 'csv_uploaded',
  actor: 'demo-user',
  status: 'success',
  metadata: { batch_id: 'batch_test01', filename: 'sample.csv', total: 4 },
  created_at: '2026-05-18T10:00:00.000000',
}
