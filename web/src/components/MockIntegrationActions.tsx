import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { triggerIntegration } from '@/api/batches'
import type { IntegrationName } from '@/api/types'

interface Props {
  batchId: string
}

const INTEGRATIONS: { key: IntegrationName; label: string }[] = [
  { key: 'salesforce', label: 'Sync to Salesforce' },
  { key: 'sharepoint', label: 'Export to SharePoint' },
  { key: 'monday', label: 'Create Monday.com task' },
]

export function MockIntegrationActions({ batchId }: Props) {
  const [busy, setBusy] = useState<IntegrationName | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function trigger(name: IntegrationName) {
    setBusy(name)
    setMessage(null)
    setError(null)
    try {
      const res = await triggerIntegration(batchId, name)
      setMessage(res.message)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Integration failed.')
    } finally {
      setBusy(null)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Integrations</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-slate-600 mb-4">
          Trigger a mock downstream action. Each click records an audit log entry.
        </p>
        <div className="flex flex-wrap gap-2">
          {INTEGRATIONS.map(({ key, label }) => (
            <Button
              key={key}
              variant="secondary"
              onClick={() => trigger(key)}
              disabled={busy !== null}
            >
              {busy === key ? 'Working…' : label}
            </Button>
          ))}
        </div>
        {message && (
          <p
            role="status"
            className="mt-3 text-sm text-emerald-700"
          >
            {message}
          </p>
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
