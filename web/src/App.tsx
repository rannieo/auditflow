import { useState } from 'react'
import { cn } from '@/lib/utils'
import { DashboardPage } from '@/pages/DashboardPage'
import { AuditLogsPage } from '@/pages/AuditLogsPage'

type Tab = 'dashboard' | 'audit'

const TABS: { key: Tab; label: string }[] = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'audit', label: 'Audit log' },
]

function App() {
  const [tab, setTab] = useState<Tab>('dashboard')

  return (
    <div className="min-h-dvh bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-base font-semibold tracking-tight">AuditFlow AI Lite</h1>
            <p className="text-xs text-slate-500">Client services validation & audit</p>
          </div>
          <nav className="flex gap-1" aria-label="Primary">
            {TABS.map((t) => (
              <button
                key={t.key}
                onClick={() => setTab(t.key)}
                aria-current={tab === t.key ? 'page' : undefined}
                className={cn(
                  'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                  tab === t.key
                    ? 'bg-slate-900 text-white'
                    : 'text-slate-600 hover:bg-slate-100',
                )}
              >
                {t.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        {tab === 'dashboard' && <DashboardPage />}
        {tab === 'audit' && <AuditLogsPage />}
      </main>
    </div>
  )
}

export default App
