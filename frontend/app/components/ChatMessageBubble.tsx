import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage } from "../types";
import { WaveAvatar } from "./WaveAvatar";

function formatarHora(timestamp: number) {
  return new Date(timestamp).toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

const markdownComponents: Components = {
  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="font-medium text-turquoise-700 underline decoration-turquoise-400/60 underline-offset-2 hover:text-turquoise-800"
    >
      {children}
    </a>
  ),
  ul: ({ children }) => <ul className="mb-2 ml-4 list-disc space-y-1 last:mb-0">{children}</ul>,
  ol: ({ children }) => <ol className="mb-2 ml-4 list-decimal space-y-1 last:mb-0">{children}</ol>,
  li: ({ children }) => <li>{children}</li>,
  h1: ({ children }) => <h3 className="mb-1 mt-2 text-base font-semibold first:mt-0">{children}</h3>,
  h2: ({ children }) => <h3 className="mb-1 mt-2 text-base font-semibold first:mt-0">{children}</h3>,
  h3: ({ children }) => <h3 className="mb-1 mt-2 text-base font-semibold first:mt-0">{children}</h3>,
  code: ({ children }) => (
    <code className="rounded bg-navy-900/10 px-1 py-0.5 text-[13px]">{children}</code>
  ),
  table: ({ children }) => (
    <div className="mb-2 overflow-x-auto last:mb-0">
      <table className="w-full min-w-max border-collapse text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="border-b border-current/20">{children}</thead>,
  th: ({ children }) => <th className="px-2 py-1.5 text-left font-semibold">{children}</th>,
  td: ({ children }) => (
    <td className="border-t border-current/10 px-2 py-1.5 align-top">{children}</td>
  ),
};

export function ChatMessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex items-end gap-2 animate-message-in ${
        isUser ? "flex-row-reverse" : "flex-row"
      }`}
    >
      {!isUser && <WaveAvatar />}

      <div
        className={`flex max-w-[85%] flex-col gap-1 sm:max-w-[70%] ${
          isUser ? "items-end" : "items-start"
        }`}
      >
        <div
          className={`wrap-break-word px-4 py-3 text-[15px] leading-relaxed shadow-md ${
            isUser
              ? "whitespace-pre-wrap rounded-2xl rounded-br-sm bg-linear-to-br from-turquoise-400/90 via-turquoise-600/90 to-navy-900/90 text-white backdrop-blur-sm"
              : message.error
                ? "rounded-2xl rounded-bl-sm border border-red-300/60 bg-red-50/70 text-red-700 backdrop-blur-md"
                : "rounded-2xl rounded-bl-sm border border-white/60 bg-sand-50/70 text-navy-900 backdrop-blur-md"
          }`}
        >
          {isUser ? (
            message.content
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
              {message.content}
            </ReactMarkdown>
          )}
        </div>
        {message.timestamp !== undefined && (
          <span className="px-1 text-xs text-sand-50/80 drop-shadow-sm">
            {formatarHora(message.timestamp)}
          </span>
        )}
      </div>
    </div>
  );
}
