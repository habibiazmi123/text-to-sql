import axios from "axios"
import { z } from "zod"

export const chatMessageSchema = z.object({
  role: z.enum(["user", "assistant"]),
  content: z.string(),
})

export const queryRequestSchema = z.object({
  question: z.string().trim().min(1, "Question is required"),
  history: z.array(chatMessageSchema).default([]),
})

export const queryResponseSchema = z.object({
  id: z.string().nullish().transform((v) => v ?? ""),
  question: z.string(),
  sql: z.string().nullish().transform((v) => v ?? ""),
  reasoning: z.string().nullish().transform((v) => v ?? ""),
  tables_used: z.array(z.string()).catch([]),
  result: z.unknown().nullable(),
  answer: z.string().nullish().transform((v) => v ?? ""),
  execution_time_ms: z.number().catch(0),
  rows_returned: z.number().catch(0),
  needs_clarify: z.boolean().catch(false),
  clarify_text: z.string().catch(""),
})

export type ChatMessage = z.infer<typeof chatMessageSchema>
export type QueryRequest = z.infer<typeof queryRequestSchema>
export type QueryResponse = z.infer<typeof queryResponseSchema>

const client = axios.create({
  baseURL: "/api",
  timeout: 60_000,
})

export async function runQuery(input: QueryRequest): Promise<QueryResponse> {
  const payload = queryRequestSchema.parse(input)
  const res = await client.post<unknown>("/query", payload)
  return queryResponseSchema.parse(res.data)
}

export function errorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data as { error?: string } | undefined
    return data?.error ?? err.message
  }
  return err instanceof Error ? err.message : "Something went wrong"
}