import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BatchSummaryCards } from './BatchSummaryCards'
import { sampleSummary } from '@/test/fixtures'

describe('BatchSummaryCards', () => {
  it('renders four metric cards', () => {
    render(<BatchSummaryCards summary={sampleSummary} />)

    expect(screen.getByText('Total records')).toBeInTheDocument()
    expect(screen.getByText('Passed')).toBeInTheDocument()
    expect(screen.getByText('Failed')).toBeInTheDocument()
    expect(screen.getByText('Duplicates')).toBeInTheDocument()
  })

  it('shows the exact counts from the summary', () => {
    const { container } = render(<BatchSummaryCards summary={sampleSummary} />)

    const values = Array.from(
      container.querySelectorAll('.tabular-nums'),
    ).map((el) => el.textContent)
    expect(values).toEqual(['4', '1', '2', '1'])
  })
})
