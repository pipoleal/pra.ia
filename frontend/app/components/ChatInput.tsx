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
      className="sticky bottom-0 z-10 px-3 pt-2 sm:px-6"
      style={{ paddingBottom: "max(1rem, env(safe-area-inset-bottom))" }}
    >
      <form
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit();
        }}
        className="mx-auto flex w-full max-w-3xl items-end gap-1.5 rounded-[1.75rem] border border-turquoise-300/50 bg-white/35 p-1.5 pl-4 shadow-[0_12px_32px_-12px_rgba(8,15,29,0.55)] backdrop-blur-2xl transition focus-within:border-turquoise-400/80 focus-within:ring-2 focus-within:ring-turquoise-300/30"
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Pergunte sobre praias, clima ou dicas do Litoral Norte..."
          rows={1}
          disabled={disabled}
          className="max-h-40 flex-1 resize-none border-none bg-transparent py-2.5 text-navy-900 placeholder:text-navy-700/50 outline-none focus:ring-0 disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={!podeEnviar}
          aria-label="Enviar mensagem"
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-linear-to-br from-turquoise-400 via-turquoise-600 to-navy-900 text-white shadow-md transition enabled:hover:brightness-110 enabled:active:scale-95 disabled:cursor-not-allowed disabled:opacity-40"
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
      <p className="mx-auto mt-2 hidden max-w-3xl text-center text-xs text-sand-100/50 sm:block">
        Pressione Enter para enviar · Shift + Enter para quebrar linha
      </p>
    </div>
  );
}
