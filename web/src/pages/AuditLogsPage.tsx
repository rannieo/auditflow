import { useEffect, useState } from 'react'
import { RefreshCw } from 'lucide-react'
import { AuditLogTable } from '@/components/AuditLogTable'
import { Button } from '@/components/ui/button'
import { listAuditLogs } from '@/api/auditLogs'
import type { AuditLog } from '@/api/types'

export function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function refresh() {
    setBusy(true)
    setError(null)
    try {
      setLogs(await listAuditLogs(100))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load audit logs.')
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-600">
          Latest entries first. Each upload, validation, AI summary, and integration
          action records an entry here.
        </p>
        <Button variant="secondary" onClick={refresh} disabled={busy}>
          <RefreshCw className="size-4" aria-hidden />
          {busy ? 'Refreshing…' : 'Refresh'}
        </Button>
      </div>

      {error && (
        <p role="alert" className="text-sm text-rose-700">
          {error}
        </p>
      )}

      <AuditLogTable logs={logs} />
    </div>
  )
}
