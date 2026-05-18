import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { BatchSummary } from '@/api/types'

interface Props {
  summary: BatchSummary
}

interface Metric {
  label: string
  value: number
  accentClass: string
}

export function BatchSummaryCards({ summary }: Props) {
  const metrics: Metric[] = [
    { label: 'Total records', value: summary.total_records, accentClass: 'text-slate-900' },
    { label: 'Passed', value: summary.passed_records, accentClass: 'text-emerald-700' },
    { label: 'Failed', value: summary.failed_records, accentClass: 'text-rose-700' },
    { label: 'Duplicates', value: summary.duplicate_records, accentClass: 'text-amber-700' },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {metrics.map((m) => (
        <Card key={m.label}>
          <CardHeader>
            <CardTitle>{m.label}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-semibold tabular-nums ${m.accentClass}`}>
              {m.value}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
