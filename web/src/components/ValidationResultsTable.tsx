import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TBody, TD, TH, THead, TR } from '@/components/ui/table'
import type { BatchRecord, ValidationStatus } from '@/api/types'

interface Props {
  records: BatchRecord[]
}

const STATUS_TO_TONE: Record<ValidationStatus, 'success' | 'warning' | 'danger'> = {
  passed: 'success',
  duplicate: 'warning',
  failed: 'danger',
}

const ROW_TINT: Record<ValidationStatus, string> = {
  passed: '',
  duplicate: 'bg-amber-50/40',
  failed: 'bg-rose-50/40',
}

function formatAmount(amount: number | null): string {
  if (amount === null) return '—'
  return amount.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  })
}

export function ValidationResultsTable({ records }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Validation results</CardTitle>
      </CardHeader>
      <CardContent className="px-0">
        {records.length === 0 ? (
          <p className="px-5 text-sm text-slate-600">No records to display.</p>
        ) : (
          <Table>
            <THead>
              <TR>
                <TH>Client</TH>
                <TH>Email</TH>
                <TH className="text-right">Amount</TH>
                <TH>Service</TH>
                <TH>Status</TH>
                <TH>Date</TH>
                <TH>Result</TH>
                <TH>Issues</TH>
              </TR>
            </THead>
            <TBody>
              {records.map((r) => (
                <TR key={r.id} className={ROW_TINT[r.validation_status]}>
                  <TD className="font-medium text-slate-900">{r.client_name ?? '—'}</TD>
                  <TD className="text-slate-600">{r.email ?? '—'}</TD>
                  <TD className="text-right tabular-nums">{formatAmount(r.amount)}</TD>
                  <TD className="text-slate-600">{r.service_type ?? '—'}</TD>
                  <TD className="text-slate-600">{r.status ?? '—'}</TD>
                  <TD className="text-slate-600 tabular-nums">{r.date ?? '—'}</TD>
                  <TD>
                    <Badge tone={STATUS_TO_TONE[r.validation_status]}>
                      {r.validation_status}
                    </Badge>
                  </TD>
                  <TD className="text-slate-600">
                    {r.validation_errors.length === 0 ? (
                      '—'
                    ) : (
                      <ul className="list-disc pl-4 space-y-0.5">
                        {r.validation_errors.map((e, i) => (
                          <li key={i}>{e}</li>
                        ))}
                      </ul>
                    )}
                  </TD>
                </TR>
              ))}
            </TBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}
