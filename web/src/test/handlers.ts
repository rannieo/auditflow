import { http, HttpResponse } from 'msw'
import { sampleAuditLog, sampleDetail, sampleSummary } from './fixtures'

export const handlers = [
  http.get('/api/health', () => HttpResponse.json({ status: 'ok' })),

  http.post('/api/batches/upload', () =>
    HttpResponse.json(sampleSummary, { status: 201 }),
  ),

  http.get('/api/batches/:batchId', () => HttpResponse.json(sampleDetail)),

  http.post('/api/batches/:batchId/ai-summary', () =>
    HttpResponse.json({
      summary:
        'This batch contains 4 record(s). 3 record(s) require review. Recommended action: clean failed records before syncing to downstream systems.',
    }),
  ),

  http.post(
    '/api/batches/:batchId/integrations/:name',
    ({ params }) =>
      HttpResponse.json({
        status: 'success',
        message: `Mock ${String(params.name)} sync completed.`,
      }),
  ),

  http.get('/api/audit-logs', () => HttpResponse.json([sampleAuditLog])),
]
