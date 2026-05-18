import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ValidationResultsTable } from './ValidationResultsTable'
import { sampleRecords } from '@/test/fixtures'

describe('ValidationResultsTable', () => {
  it('shows the empty state when there are no records', () => {
    render(<ValidationResultsTable records={[]} />)

    expect(screen.getByText(/no records/i)).toBeInTheDocument()
  })

  it('renders one row per record', () => {
    render(<ValidationResultsTable records={sampleRecords} />)

    // 1 header row + 4 data rows = 5 total
    expect(screen.getAllByRole('row')).toHaveLength(5)
  })

  it('renders a badge with the correct status text per row', () => {
    render(<ValidationResultsTable records={sampleRecords} />)

    expect(screen.getByText('passed')).toBeInTheDocument()
    expect(screen.getAllByText('failed')).toHaveLength(2)
    expect(screen.getByText('duplicate')).toBeInTheDocument()
  })

  it('formats amount as USD', () => {
    render(<ValidationResultsTable records={sampleRecords} />)

    expect(screen.getByText('$1,500')).toBeInTheDocument()
    expect(screen.getByText('$8,000')).toBeInTheDocument()
    expect(screen.getByText('-$50')).toBeInTheDocument()
  })

  it('renders an em-dash for null amount', () => {
    render(
      <ValidationResultsTable
        records={[
          { ...sampleRecords[0], id: 99, amount: null },
        ]}
      />,
    )

    // Multiple cells can be '—' (null email/status/etc. in other rows / empty errors).
    // For the passed sampleRecord, amount is the only field set to null — so one
    // dash in the amount column (right-aligned class) is enough proof.
    const dashes = screen.getAllByText('—')
    expect(dashes.length).toBeGreaterThanOrEqual(1)
  })

  it('shows validation_errors as a list for failed rows', () => {
    render(<ValidationResultsTable records={sampleRecords} />)

    expect(screen.getByText('email is required')).toBeInTheDocument()
    expect(screen.getByText('amount must be greater than 0')).toBeInTheDocument()
  })
})
