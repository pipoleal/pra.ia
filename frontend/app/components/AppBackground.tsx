/**
 * Fundo sem foto (por enquanto): gradiente + manchas desfocadas nos tons
 * praianos (azul marinho profundo, turquesa e areia). Assim que houver uma
 * foto real de praia do Litoral Norte disponivel, este componente pode ser
 * trocado por uma versao com imagem de fundo.
 */
export function AppBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden bg-navy-950" aria-hidden="true">
      <div className="absolute -top-32 -left-24 h-96 w-96 rounded-full bg-turquoise-500/25 blur-3xl" />
      <div className="absolute top-1/3 -right-32 h-[28rem] w-[28rem] rounded-full bg-navy-500/25 blur-3xl" />
      <div className="absolute -bottom-40 left-1/4 h-[26rem] w-[26rem] rounded-full bg-sand-300/10 blur-3xl" />
      <div className="absolute inset-0 bg-linear-to-b from-navy-950/40 via-transparent to-navy-950/60" />
    </div>
  );
}
