"use client"

import { useEffect } from "react"
import { Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  disabled?: boolean
  textareaRef: React.RefObject<HTMLTextAreaElement | null>
}

export function ChatInput({
  value,
  onChange,
  onSubmit,
  disabled,
  textareaRef,
}: ChatInputProps) {
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = "auto"
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`
  }, [value, textareaRef])

  const canSubmit = !disabled && value.trim().length > 0

  return (
    <div className="rounded-2xl border bg-card p-2 shadow-lg shadow-black/5 transition-all focus-within:border-primary/40 focus-within:ring-4 focus-within:ring-primary/10 dark:shadow-black/30">
      <Textarea
        ref={textareaRef}
        rows={1}
        value={value}
        disabled={disabled}
        placeholder='Ask in natural language… e.g. "Berapa revenue bulan lalu per region?"'
        className="max-h-40 min-h-11 resize-none border-0 bg-transparent px-2 py-2 shadow-none focus-visible:border-transparent focus-visible:ring-0"
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            if (canSubmit) onSubmit()
          }
        }}
      />
      <div className="flex items-center justify-between px-2 pb-0.5 pt-1">
        <p className="text-xs text-muted-foreground">Enter to send · Shift+Enter for newline</p>
        <Button
          type="button"
          size="icon"
          className="size-8 rounded-xl"
          disabled={!canSubmit}
          onClick={onSubmit}
          aria-label="Send question"
        >
          <Send />
        </Button>
      </div>
    </div>
  )
}