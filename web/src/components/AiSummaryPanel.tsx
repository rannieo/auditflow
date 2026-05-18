import { useState } from 'react'
import { Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { generateAiSummary } from '@/api/batches'

interface Props {
  batchId: string
}

export function AiSummaryPanel({ batchId }: Props) {
  const [summary, setSummary] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function run() {
    setBusy(true)
    setError(null)
    try {
      const res = await generateAiSummary(batchId)
      setSummary(res.summary)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate summary.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI summary</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-slate-600 mb-4">
          Generate a plain-English review of this batch using validation metrics only.
          The MVP uses deterministic logic — no record data is sent to any external LLM.
        </p>
        <Button onClick={run} disabled={busy} variant="accent">
          <Sparkles className="size-4" aria-hidden />
          {busy ? 'Generating…' : 'Generate AI summary'}
        </Button>
        {summary && (
          <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-slate-800 leading-6">
            {summary}
          </div>
        )}
        {error && (
          <p role="alert" className="mt-3 text-sm text-rose-700">
            {error}
          </p>
        )}
      </CardContent>
    </Card>
  )
}
