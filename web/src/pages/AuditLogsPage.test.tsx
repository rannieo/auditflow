import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '@/test/server'
import { sampleAuditLog } from '@/test/fixtures'
import { AuditLogsPage } from './AuditLogsPage'

describe('AuditLogsPage', () => {
  it('renders fetched audit logs on mount', async () => {
    render(<AuditLogsPage />)

    expect(await screen.findByText('csv_uploaded')).toBeInTheDocument()
  })

  it('re-fetches when the Refresh button is clicked', async () => {
    let callCount = 0
    server.use(
      http.get('/api/audit-logs', () => {
        callCount += 1
        return HttpResponse.json([sampleAuditLog])
      }),
    )
    const user = userEvent.setup()
    render(<AuditLogsPage />)

    await screen.findByText('csv_uploaded')
    expect(callCount).toBe(1)

    await user.click(screen.getByRole('button', { name: /refresh/i }))

    expect(callCount).toBeGreaterThanOrEqual(2)
  })

  it('renders an alert when the API fails', async () => {
    server.use(
      http.get('/api/audit-logs', () =>
        HttpResponse.json({ detail: 'boom' }, { status: 500 }),
      ),
    )
    render(<AuditLogsPage />)

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/boom|failed/i)
  })
})
