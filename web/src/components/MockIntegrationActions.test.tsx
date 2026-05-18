import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '@/test/server'
import { MockIntegrationActions } from './MockIntegrationActions'

describe('MockIntegrationActions', () => {
  it('renders the three integration buttons', () => {
    render(<MockIntegrationActions batchId="batch_test01" />)

    expect(screen.getByRole('button', { name: /sync to salesforce/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /export to sharepoint/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /create monday\.com task/i })).toBeInTheDocument()
  })

  it('hits the matching endpoint when a button is clicked', async () => {
    let receivedName = ''
    server.use(
      http.post('/api/batches/:id/integrations/:name', ({ params }) => {
        receivedName = String(params.name)
        return HttpResponse.json({
          status: 'success',
          message: `Mock ${params.name} sync completed.`,
        })
      }),
    )
    const user = userEvent.setup()
    render(<MockIntegrationActions batchId="batch_test01" />)

    await user.click(screen.getByRole('button', { name: /export to sharepoint/i }))

    await screen.findByRole('status')
    expect(receivedName).toBe('sharepoint')
  })

  it('renders a success status message after a successful click', async () => {
    const user = userEvent.setup()
    render(<MockIntegrationActions batchId="batch_test01" />)

    await user.click(screen.getByRole('button', { name: /sync to salesforce/i }))

    const status = await screen.findByRole('status')
    expect(status).toHaveTextContent(/salesforce/i)
  })

  it('renders an alert when the API returns an error', async () => {
    server.use(
      http.post('/api/batches/:id/integrations/:name', () =>
        HttpResponse.json({ detail: 'Unsupported integration' }, { status: 400 }),
      ),
    )
    const user = userEvent.setup()
    render(<MockIntegrationActions batchId="batch_test01" />)

    await user.click(screen.getByRole('button', { name: /sync to salesforce/i }))

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent('Unsupported integration')
  })
})
