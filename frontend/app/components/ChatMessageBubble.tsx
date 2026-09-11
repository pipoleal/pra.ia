import type { ChatMessage } from "../types";
import { WaveAvatar } from "./WaveAvatar";

function formatarHora(timestamp: number) {
  return new Date(timestamp).toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

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
          className={`whitespace-pre-wrap wrap-break-word px-4 py-3 text-[15px] leading-relaxed shadow-md ${
            isUser
              ? "rounded-2xl rounded-br-sm bg-linear-to-br from-turquoise-400 via-turquoise-600 to-navy-900 text-white"
              : message.error
                ? "rounded-2xl rounded-bl-sm border border-red-300/70 bg-red-50/90 text-red-700 backdrop-blur-sm"
                : "rounded-2xl rounded-bl-sm border border-white/70 bg-sand-50/90 text-navy-900 backdrop-blur-sm"
          }`}
        >
          {message.content}
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
