import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DashboardPage } from './DashboardPage'

describe('DashboardPage', () => {
  it('renders the upload card initially with no batch loaded', () => {
    render(<DashboardPage />)

    expect(screen.getByText('Upload CSV')).toBeInTheDocument()
    expect(screen.queryByText('Total records')).not.toBeInTheDocument()
    expect(screen.queryByText('Validation results')).not.toBeInTheDocument()
  })

  it('shows summary cards and the validation table after a successful upload', async () => {
    const user = userEvent.setup()
    render(<DashboardPage />)

    const input = document.querySelector('input[type=file]') as HTMLInputElement
    await user.upload(
      input,
      new File(['client_name\nAcme\n'], 'sample.csv', { type: 'text/csv' }),
    )
    await user.click(screen.getByRole('button', { name: /upload & validate/i }))

    expect(await screen.findByText('Total records')).toBeInTheDocument()
    expect(await screen.findByText('Validation results')).toBeInTheDocument()
    expect(screen.getByText('AI summary')).toBeInTheDocument()
    expect(screen.getByText('Integrations')).toBeInTheDocument()
  })
})
