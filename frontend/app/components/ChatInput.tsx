import { KeyboardEvent, RefObject, useEffect } from "react";

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled: boolean;
  textareaRef: RefObject<HTMLTextAreaElement | null>;
}

export function ChatInput({ value, onChange, onSubmit, disabled, textareaRef }: ChatInputProps) {
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`;
  }, [value, textareaRef]);

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSubmit();
    }
  }

  const podeEnviar = value.trim().length > 0 && !disabled;

  return (
    <div
      className="sticky bottom-0 z-10 border-t border-ocean-100 bg-white/90 px-3 pt-3 backdrop-blur-md sm:px-6"
      style={{ paddingBottom: "max(0.75rem, env(safe-area-inset-bottom))" }}
    >
      <form
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit();
        }}
        className="mx-auto flex w-full max-w-3xl items-end gap-2"
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Pergunte sobre praias, clima ou dicas do Litoral Norte..."
          rows={1}
          disabled={disabled}
          className="max-h-40 flex-1 resize-none rounded-2xl border border-ocean-200 bg-sand-50/40 px-4 py-3 text-ocean-900 placeholder:text-ocean-900/40 outline-none transition focus:border-ocean-400 focus:ring-2 focus:ring-ocean-200 disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={!podeEnviar}
          aria-label="Enviar mensagem"
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-linear-to-br from-ocean-500 to-ocean-600 text-white shadow-sm transition enabled:hover:brightness-110 enabled:active:scale-95 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none">
            <path
              d="M4 12L20 4L13 20L11 13L4 12Z"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          </svg>
        </button>
      </form>
      <p className="mx-auto mt-1.5 hidden max-w-3xl text-center text-xs text-ocean-900/35 sm:block">
        Pressione Enter para enviar · Shift + Enter para quebrar linha
      </p>
    </div>
  );
}
