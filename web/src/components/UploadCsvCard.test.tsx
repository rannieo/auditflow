import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '@/test/server'
import { UploadCsvCard } from './UploadCsvCard'
import { sampleSummary } from '@/test/fixtures'

function makeFile(name = 'sample.csv', text = 'client_name\nAcme\n'): File {
  return new File([text], name, { type: 'text/csv' })
}

describe('UploadCsvCard', () => {
  it('disables the submit button until a file is selected', () => {
    render(<UploadCsvCard onUploaded={() => {}} />)

    expect(screen.getByRole('button', { name: /upload & validate/i })).toBeDisabled()
  })

  it('enables the submit button after a file is selected', async () => {
    const user = userEvent.setup()
    render(<UploadCsvCard onUploaded={() => {}} />)

    const input = document.querySelector('input[type=file]') as HTMLInputElement
    await user.upload(input, makeFile())

    expect(screen.getByRole('button', { name: /upload & validate/i })).toBeEnabled()
  })

  it('calls onUploaded with the response after a successful upload', async () => {
    const user = userEvent.setup()
    const onUploaded = vi.fn()
    render(<UploadCsvCard onUploaded={onUploaded} />)

    const input = document.querySelector('input[type=file]') as HTMLInputElement
    await user.upload(input, makeFile())
    await user.click(screen.getByRole('button', { name: /upload & validate/i }))

    await vi.waitFor(() => {
      expect(onUploaded).toHaveBeenCalledTimes(1)
    })
    expect(onUploaded).toHaveBeenCalledWith(sampleSummary)
  })

  it('renders an alert when the server returns an error', async () => {
    server.use(
      http.post('/api/batches/upload', () =>
        HttpResponse.json({ detail: 'CSV is missing required headers: date' }, { status: 400 }),
      ),
    )
    const user = userEvent.setup()
    render(<UploadCsvCard onUploaded={() => {}} />)

    const input = document.querySelector('input[type=file]') as HTMLInputElement
    await user.upload(input, makeFile())
    await user.click(screen.getByRole('button', { name: /upload & validate/i }))

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent('missing required headers')
  })
})
