import { WaveAvatar } from "./WaveAvatar";

export function TypingIndicator() {
  return (
    <div className="flex items-end gap-2 animate-message-in">
      <WaveAvatar />
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-sm border border-ocean-100 bg-white px-4 py-3.5 shadow-sm">
        {[0, 150, 300].map((delay) => (
          <span
            key={delay}
            className="h-1.5 w-1.5 rounded-full bg-ocean-300 animate-bounce"
            style={{ animationDelay: `${delay}ms` }}
          />
        ))}
      </div>
    </div>
  );
}
