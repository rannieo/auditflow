import { useEffect, useState } from 'react'
import { UploadCsvCard } from '@/components/UploadCsvCard'
import { BatchSummaryCards } from '@/components/BatchSummaryCards'
import { ValidationResultsTable } from '@/components/ValidationResultsTable'
import { AiSummaryPanel } from '@/components/AiSummaryPanel'
import { MockIntegrationActions } from '@/components/MockIntegrationActions'
import { getBatchDetail } from '@/api/batches'
import type { BatchDetail, BatchSummary } from '@/api/types'

export function DashboardPage() {
  const [summary, setSummary] = useState<BatchSummary | null>(null)
  const [detail, setDetail] = useState<BatchDetail | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!summary) return
    let cancelled = false
    setError(null)
    getBatchDetail(summary.batch_id)
      .then((d) => {
        if (!cancelled) setDetail(d)
      })
      .catch((err) => {
        if (!cancelled)
          setError(err instanceof Error ? err.message : 'Failed to load batch.')
      })
    return () => {
      cancelled = true
    }
  }, [summary])

  return (
    <div className="space-y-6">
      <UploadCsvCard onUploaded={setSummary} />

      {error && (
        <p role="alert" className="text-sm text-rose-700">
          {error}
        </p>
      )}

      {summary && <BatchSummaryCards summary={summary} />}

      {summary && (
        <div className="grid lg:grid-cols-2 gap-6">
          <AiSummaryPanel batchId={summary.batch_id} />
          <MockIntegrationActions batchId={summary.batch_id} />
        </div>
      )}

      {detail && <ValidationResultsTable records={detail.records} />}
    </div>
  )
}
