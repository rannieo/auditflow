import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AuditLogTable } from './AuditLogTable'
import { sampleAuditLog } from '@/test/fixtures'

describe('AuditLogTable', () => {
  it('shows the empty state when there are no logs', () => {
    render(<AuditLogTable logs={[]} />)

    expect(screen.getByText(/no audit entries/i)).toBeInTheDocument()
  })

  it('renders one row per log entry', () => {
    render(
      <AuditLogTable
        logs={[
          sampleAuditLog,
          { ...sampleAuditLog, id: 2, action: 'ai_summary_generated' },
        ]}
      />,
    )

    // 1 header row + 2 data rows = 3 total
    expect(screen.getAllByRole('row')).toHaveLength(3)
  })

  it('renders the action and metadata for each row', () => {
    render(<AuditLogTable logs={[sampleAuditLog]} />)

    expect(screen.getByText('csv_uploaded')).toBeInTheDocument()
    expect(screen.getByText(/"filename":"sample.csv"/)).toBeInTheDocument()
  })
})
