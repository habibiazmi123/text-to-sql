"use client"

import { Database } from "lucide-react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

function cellText(value: unknown): string {
  if (value === null || value === undefined) return "—"
  if (typeof value === "object") return JSON.stringify(value)
  return String(value)
}

export function ResultTable({ rows }: { rows: Array<Record<string, unknown>> }) {
  if (rows.length === 0) {
    return <p className="py-4 text-sm text-muted-foreground">Query returned no rows.</p>
  }

  const columns = Object.keys(rows[0])

  return (
    <div className="mt-3 overflow-hidden rounded-xl border">
      <div className="flex items-center justify-between gap-2 border-b bg-muted/50 px-3 py-1.5 text-xs text-muted-foreground">
        <span>
          {rows.length} row{rows.length === 1 ? "" : "s"}
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
            {rows.map((row, i) => (
              <TableRow key={i} className="hover:bg-muted/40">
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
    </div>
  )
}