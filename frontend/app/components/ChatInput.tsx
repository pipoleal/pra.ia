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
      className="sticky bottom-0 z-10 px-4 pt-3 sm:px-6"
      style={{ paddingBottom: "max(1.5rem, env(safe-area-inset-bottom))" }}
    >
      <form
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit();
        }}
        className="mx-auto flex w-full max-w-3xl items-center gap-2 rounded-[1.75rem] border border-turquoise-300/60 bg-white/45 p-2 pl-5 shadow-[0_16px_40px_-14px_rgba(8,15,29,0.6)] backdrop-blur-2xl transition-all duration-200 focus-within:border-turquoise-400 focus-within:bg-white/60 focus-within:shadow-[0_18px_44px_-12px_rgba(16,90,90,0.45)] focus-within:ring-4 focus-within:ring-turquoise-300/25"
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Pergunte sobre praias, clima ou dicas do Litoral Norte..."
          rows={1}
          disabled={disabled}
          className="no-scrollbar max-h-40 flex-1 resize-none border-none bg-transparent py-3.5 text-[15px] leading-relaxed text-navy-900 placeholder:text-navy-700/45 outline-none focus:ring-0 disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={!podeEnviar}
          aria-label="Enviar mensagem"
          className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-linear-to-br from-turquoise-400 via-turquoise-600 to-navy-900 text-white shadow-lg transition-all duration-200 enabled:hover:scale-105 enabled:hover:brightness-110 enabled:active:scale-95 disabled:cursor-not-allowed disabled:opacity-40"
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
      <p className="mx-auto mt-2.5 hidden max-w-3xl text-center text-xs text-sand-100/60 drop-shadow-sm sm:block">
        Pressione Enter para enviar · Shift + Enter para quebrar linha
      </p>
    </div>
  );
}
