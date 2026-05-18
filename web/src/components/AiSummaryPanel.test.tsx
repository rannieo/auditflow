import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '@/test/server'
import { AiSummaryPanel } from './AiSummaryPanel'

describe('AiSummaryPanel', () => {
  it('renders the summary returned by the API after clicking the button', async () => {
    const user = userEvent.setup()
    render(<AiSummaryPanel batchId="batch_test01" />)

    await user.click(screen.getByRole('button', { name: /generate ai summary/i }))

    expect(
      await screen.findByText(/this batch contains 4 record/i),
    ).toBeInTheDocument()
  })

  it('renders an alert when the API returns an error', async () => {
    server.use(
      http.post('/api/batches/:id/ai-summary', () =>
        HttpResponse.json({ detail: 'Batch not found.' }, { status: 404 }),
      ),
    )
    const user = userEvent.setup()
    render(<AiSummaryPanel batchId="missing" />)

    await user.click(screen.getByRole('button', { name: /generate ai summary/i }))

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent('Batch not found.')
  })
})
