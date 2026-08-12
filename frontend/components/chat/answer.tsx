"use client"

import { useState } from "react"
import { Check, ChevronDown, Copy, Terminal, Timer } from "lucide-react"
import type { QueryResponse } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import { ResultTable } from "@/components/chat/result-table"

function isRows(value: unknown): value is Array<Record<string, unknown>> {
  return Array.isArray(value) && value.every((row) => typeof row === "object" && row !== null)
}

function CopySql({ sql }: { sql: string }) {
  const [copied, setCopied] = useState(false)

  async function copy() {
    try {
      await navigator.clipboard.writeText(sql)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // clipboard unavailable
    }
  }

  return (
    <button
      type="button"
      onClick={copy}
      aria-label="Copy SQL"
      className="absolute right-2 top-2 flex size-7 cursor-pointer items-center justify-center rounded-lg border border-border bg-background text-muted-foreground transition-colors hover:text-foreground"
    >
      {copied ? <Check className="size-3.5 text-primary" /> : <Copy className="size-3.5" />}
    </button>
  )
}

export function Answer({ response }: { response: QueryResponse }) {
  const rows = isRows(response.result) ? response.result : null
  const hasMeta = Boolean(response.sql || response.reasoning || response.tables_used.length > 0)

  return (
    <div className="animate-fade-in-up overflow-hidden rounded-2xl border bg-card shadow-sm">
      <div className="p-4">
        {response.needs_clarify ? (
          <p className="whitespace-pre-wrap text-sm leading-relaxed">
            {response.clarify_text}
          </p>
        ) : (
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{response.answer}</p>
        )}

        {rows && <ResultTable rows={rows} />}
      </div>

      {hasMeta && (
        <Collapsible>
          <CollapsibleTrigger className="flex w-full cursor-pointer items-center gap-2 border-t bg-muted/30 px-4 py-2.5 text-xs font-medium text-muted-foreground transition-colors outline-none hover:bg-muted/60 hover:text-foreground [&[data-state=open]]:text-foreground">
            <Terminal className="size-3.5" />
            Generated SQL
            {typeof response.execution_time_ms === "number" && (
              <span className="inline-flex items-center gap-1 text-muted-foreground">
                · {response.execution_time_ms} ms
              </span>
            )}
            <ChevronDown className="ml-auto size-4 text-muted-foreground transition-transform duration-200 [&_group[data-state=open]]:rotate-180 data-[state=open]:rotate-180" />
          </CollapsibleTrigger>
          <CollapsibleContent className="space-y-3 p-4">
            {response.sql && (
              <div className="relative">
                <pre className="overflow-x-auto rounded-lg bg-muted/50 p-3 pr-10 font-mono text-xs leading-relaxed">
                  {response.sql}
                </pre>
                <CopySql sql={response.sql} />
              </div>
            )}
            {response.reasoning && (
              <p className="text-xs leading-relaxed text-muted-foreground">
                {response.reasoning}
              </p>
            )}
            {response.tables_used.length > 0 && (
              <div className="flex flex-wrap items-center gap-2">
                {response.tables_used.map((table) => (
                  <Badge key={table} variant="secondary">
                    {table}
                  </Badge>
                ))}
                {typeof response.execution_time_ms === "number" && (
                  <Badge variant="secondary" className="ml-auto">
                    <Timer className="size-3" />
                    {response.execution_time_ms} ms
                  </Badge>
                )}
              </div>
            )}
          </CollapsibleContent>
        </Collapsible>
      )}
    </div>
  )
}