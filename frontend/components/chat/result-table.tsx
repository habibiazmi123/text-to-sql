"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight, Database } from "lucide-react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"

// ponytail: frontend slices the fetched rows; server-side LIMIT/OFFSET only
// when payload size becomes a problem (the summarize call already caps input)
const PAGE_SIZE = 50

function cellText(value: unknown): string {
  if (value === null || value === undefined) return "—"
  if (typeof value === "object") return JSON.stringify(value)
  return String(value)
}

export function ResultTable({ rows }: { rows: Array<Record<string, unknown>> }) {
  const [page, setPage] = useState(1)

  if (rows.length === 0) {
    return <p className="py-4 text-sm text-muted-foreground">Query returned no rows.</p>
  }

  const columns = Object.keys(rows[0])
  const pageCount = Math.max(1, Math.ceil(rows.length / PAGE_SIZE))
  const start = (page - 1) * PAGE_SIZE
  const pageRows = rows.slice(start, start + PAGE_SIZE)

  return (
    <div className="mt-3 overflow-hidden rounded-xl border">
      <div className="flex items-center justify-between gap-2 border-b bg-muted/50 px-3 py-1.5 text-xs text-muted-foreground">
        <span>
          {start + 1}–{Math.min(start + pageRows.length, rows.length)} of {rows.length} rows
        </span>
        <Database className="size-3.5" />
      </div>
      <div className="max-h-96 overflow-auto">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              {columns.map((col) => (
                <TableHead key={col} className="sticky top-0 whitespace-nowrap bg-muted/30">
                  {col}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {pageRows.map((row, i) => (
              <TableRow key={start + i} className="hover:bg-muted/40">
                {columns.map((col) => (
                  <TableCell key={col} className="whitespace-nowrap font-mono text-xs">
                    {cellText(row[col])}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      {pageCount > 1 && (
        <div className="flex items-center justify-between border-t bg-muted/30 px-3 py-1.5">
          <span className="text-xs text-muted-foreground">
            Page {page} of {pageCount}
          </span>
          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="gap-1 px-2"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft className="size-3.5" />
              Previous
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="gap-1 px-2"
              disabled={page >= pageCount}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
              <ChevronRight className="size-3.5" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}