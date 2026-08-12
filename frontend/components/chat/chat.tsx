"use client"

import { useEffect, useRef, useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { useTheme } from "next-themes"
import { toast } from "sonner"
import { Bot, Database, Moon, Sparkles, Sun } from "lucide-react"
import { cn } from "@/lib/utils"
import { errorMessage, runQuery, type ChatMessage, type QueryResponse } from "@/lib/api"
import { ChatInput } from "@/components/chat/chat-input"
import { Answer } from "@/components/chat/answer"
import { Button } from "@/components/ui/button"

type ChatItem =
  | { kind: "user"; content: string }
  | { kind: "assistant"; response: QueryResponse }
  | { kind: "error"; content: string }

const EXAMPLES = [
  "Tampilkan 10 customer dengan revenue terbesar dalam 3 bulan terakhir",
  "Berapa total transaksi per bulan tahun ini?",
  "Rata-rata durasi sesi pengguna per halaman",
]

function BotAvatar({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "flex size-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary/60 text-primary-foreground shadow-sm",
        className,
      )}
    >
      <Bot className="size-4" />
    </span>
  )
}

function ThemeToggle() {
  const { setTheme } = useTheme()

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      className="rounded-lg"
      onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
      aria-label="Toggle theme"
    >
      <Sun className="size-4 dark:hidden" />
      <Moon className="hidden size-4 dark:block" />
    </Button>
  )
}

function ChatBubble({ item }: { item: ChatItem }) {
  if (item.kind === "user") {
    return (
      <div className="flex animate-fade-in-up justify-end">
        <div className="max-w-[85%] rounded-2xl rounded-br-md bg-primary px-4 py-2.5 text-sm text-primary-foreground shadow-sm">
          <p className="whitespace-pre-wrap">{item.content}</p>
        </div>
      </div>
    )
  }

  if (item.kind === "error") {
    return (
      <div className="flex animate-fade-in-up justify-end">
        <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-2.5 text-sm text-destructive">
          {item.content}
        </div>
      </div>
    )
  }

  return (
    <div className="flex animate-fade-in-up items-start gap-3">
      <BotAvatar className="mt-0.5" />
      <div className="min-w-0 flex-1">
        <Answer response={item.response} />
      </div>
    </div>
  )
}

function Shimmer({ className }: { className?: string }) {
  return (
    <div className={cn("relative overflow-hidden rounded-md bg-muted", className)}>
      <div className="absolute inset-y-0 left-0 w-1/2 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-background/70 to-transparent" />
    </div>
  )
}

const PHASES = ["Memahami pertanyaan…", "Menulis SQL…", "Menjalankan query…"]

function PendingBubble() {
  const [phase, setPhase] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => setPhase((v) => (v + 1) % PHASES.length), 1600)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="flex animate-fade-in-up items-start gap-3">
      <BotAvatar className="animate-pulse" />
      <div className="w-full max-w-md rounded-2xl border bg-card p-4 shadow-sm">
        <div className="flex items-center justify-between gap-2">
          <p key={phase} className="animate-fade-in text-xs text-muted-foreground">
            {PHASES[phase]}
          </p>
          <span className="flex items-center gap-1" aria-hidden="true">
            <span className="size-1.5 animate-typing-1 rounded-full bg-primary" />
            <span className="size-1.5 animate-typing-2 rounded-full bg-primary" />
            <span className="size-1.5 animate-typing-3 rounded-full bg-primary" />
          </span>
        </div>
        <div className="mt-3 space-y-2" aria-hidden="true">
          <Shimmer className="h-3 w-11/12" />
          <Shimmer className="h-3 w-full" />
          <Shimmer className="h-3 w-8/12" />
        </div>
      </div>
    </div>
  )
}

function EmptyState({ onPick }: { onPick: (question: string) => void }) {
  return (
    <div className="flex h-full items-center justify-center px-4">
      <div className="flex max-w-md flex-col items-center text-center">
        <div className="relative mb-6">
          <div className="absolute inset-0 animate-blob rounded-3xl bg-primary/30 blur-3xl" />
          <div className="relative flex size-16 animate-fade-in-up items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg">
            <Database className="size-8" />
          </div>
        </div>
        <h2 className="animate-fade-in-up text-2xl font-semibold tracking-tight">
          Ask your data, in plain language
        </h2>
        <p className="mt-2 animate-fade-in-up text-sm text-muted-foreground [animation-delay:100ms]">
          Describe what you want to know — TextQL writes the SQL and runs the query for you.
        </p>
        <div className="mt-8 grid w-full gap-2">
          {EXAMPLES.map((example, i) => (
            <button
              key={example}
              type="button"
              onClick={() => onPick(example)}
              style={{ animationDelay: `${200 + i * 80}ms` }}
              className="group flex animate-fade-in-up cursor-pointer items-start gap-2.5 rounded-xl border bg-card px-4 py-3 text-left text-sm transition-colors hover:border-primary/40 hover:bg-primary/5"
            >
              <Sparkles className="mt-0.5 size-4 shrink-0 text-primary" />
              <span>{example}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function toHistory(items: ChatItem[]): ChatMessage[] {
  return items
    .filter((i) => i.kind !== "error")
    .map((i): ChatMessage =>
      i.kind === "user"
        ? { role: "user", content: i.content }
        : {
            role: "assistant",
            content: i.response.answer || i.response.clarify_text || i.response.reasoning,
          },
    )
}

export function Chat() {
  const [items, setItems] = useState<ChatItem[]>([])
  const [draft, setDraft] = useState("")
  const scrollRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const mutation = useMutation({
    mutationFn: runQuery,
    onSuccess: (response) => {
      setItems((prev) => [...prev, { kind: "assistant", response }])
    },
    onError: (err) => {
      const message = errorMessage(err)
      setItems((prev) => [...prev, { kind: "error", content: message }])
      toast.error(message)
    },
  })

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight })
  }, [items, mutation.isPending])

  function handleSubmit(question: string) {
    const history = toHistory(items)
    setItems((prev) => [...prev, { kind: "user", content: question }])
    mutation.mutate({ question, history })
  }

  function submitDraft() {
    if (mutation.isPending) return
    const question = draft.trim()
    if (!question) return
    setDraft("")
    handleSubmit(question)
    textareaRef.current?.focus()
  }

  function pickExample(example: string) {
    setDraft(example)
    textareaRef.current?.focus()
  }

  return (
    <div className="relative flex h-svh w-full flex-col overflow-hidden">
      <div className="pointer-events-none absolute inset-0" aria-hidden="true">
        <div className="absolute -top-[12%] left-1/2 h-80 w-[42rem] -translate-x-1/2 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute -bottom-20 right-[-10%] h-64 w-64 rounded-full bg-primary/10 blur-3xl" />
      </div>

      <div className="mx-auto flex h-full w-full max-w-3xl flex-col">
        <header className="flex items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <BotAvatar />
            <div>
              <h1 className="text-sm font-semibold tracking-tight">TextQL</h1>
              <p className="text-xs text-muted-foreground">Natural language → SQL</p>
            </div>
          </div>
          <ThemeToggle />
        </header>

        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto px-4 py-4 sm:px-6">
          {items.length === 0 && !mutation.isPending ? (
            <EmptyState onPick={pickExample} />
          ) : (
            <>
              {items.map((item, i) => (
                <div key={i} style={{ animationDelay: `${i * 60}ms` }}>
                  <ChatBubble item={item} />
                </div>
              ))}
              {mutation.isPending && <PendingBubble />}
            </>
          )}
        </div>

        <footer className="px-4 pb-4 pt-2 sm:px-6">
          <ChatInput
            textareaRef={textareaRef}
            value={draft}
            onChange={setDraft}
            disabled={mutation.isPending}
            onSubmit={submitDraft}
          />
        </footer>
      </div>
    </div>
  )
}