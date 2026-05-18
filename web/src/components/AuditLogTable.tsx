import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TBody, TD, TH, THead, TR } from '@/components/ui/table'
import type { AuditLog } from '@/api/types'

interface Props {
  logs: AuditLog[]
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString()
}

export function AuditLogTable({ logs }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Audit log</CardTitle>
      </CardHeader>
      <CardContent className="px-0">
        {logs.length === 0 ? (
          <p className="px-5 text-sm text-slate-600">No audit entries yet.</p>
        ) : (
          <Table>
            <THead>
              <TR>
                <TH>When</TH>
                <TH>Action</TH>
                <TH>Actor</TH>
                <TH>Status</TH>
                <TH>Metadata</TH>
              </TR>
            </THead>
            <TBody>
              {logs.map((log) => (
                <TR key={log.id}>
                  <TD className="text-slate-600 tabular-nums">{formatTime(log.created_at)}</TD>
                  <TD className="font-medium text-slate-900">{log.action}</TD>
                  <TD className="text-slate-600">{log.actor}</TD>
                  <TD>
                    <Badge tone={log.status === 'success' ? 'success' : 'neutral'}>
                      {log.status}
                    </Badge>
                  </TD>
                  <TD>
                    <code className="text-xs text-slate-700">
                      {JSON.stringify(log.metadata)}
                    </code>
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
