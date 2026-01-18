import { SendIcon } from 'lucide-react'
import { type FormEvent, useState } from 'react'

interface MessageInputProps {
  onSend: (text: string) => void
  isSending: boolean
}

export function MessageInput({ onSend, isSending }: MessageInputProps) {
  const [value, setValue] = useState('')

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const trimmed = value.trim()
    if (!trimmed || isSending) return
    onSend(trimmed)
    setValue('')
  }

  return (
    <form onSubmit={handleSubmit} autoComplete="off">
      <div className="chat-input-row">
        <input
          className="chat-input"
          type="text"
          placeholder="Ask anything to get onboarded faster..."
          value={value}
          onChange={(event) => setValue(event.target.value)}
        />
        <button
          type="submit"
          className="chat-send-button"
          disabled={!value.trim() || isSending}
        >
          <span className="chat-send-button-icon" aria-hidden="true">
            <SendIcon />
          </span>
          <span>{isSending ? 'Sending' : 'Send'}</span>
        </button>
      </div>
    </form>
  )
}
