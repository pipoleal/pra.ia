export function WaveAvatar({ className = "" }: { className?: string }) {
  return (
    <div
      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-linear-to-br from-turquoise-400 via-turquoise-600 to-navy-900 shadow-md ${className}`}
      aria-hidden="true"
    >
      <svg viewBox="0 0 24 24" className="h-4.5 w-4.5 text-white" fill="none">
        <path
          d="M2 17c1.6 1.4 3.2 1.4 4.8 0 1.6-1.4 3.2-1.4 4.8 0 1.6 1.4 3.2 1.4 4.8 0 1.6-1.4 3.2-1.4 4.8 0"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M2 12c1.6 1.4 3.2 1.4 4.8 0 1.6-1.4 3.2-1.4 4.8 0 1.6 1.4 3.2 1.4 4.8 0 1.6-1.4 3.2-1.4 4.8 0"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.6"
        />
        <circle cx="17.5" cy="6.5" r="2.2" fill="currentColor" opacity="0.9" />
      </svg>
    </div>
  );
}
