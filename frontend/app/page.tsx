"use client";

import { useEffect, useRef, useState } from "react";
import { ChatInput } from "./components/ChatInput";
import { ChatMessageBubble } from "./components/ChatMessageBubble";
import { TypingIndicator } from "./components/TypingIndicator";
import { WaveAvatar } from "./components/WaveAvatar";
import type { ChatMessage } from "./types";

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

const MENSAGEM_BOAS_VINDAS: ChatMessage = {
  id: "boas-vindas",
  role: "assistant",
  content:
    "Oi, eu sou a pra.ia! 🌊 Te ajudo a escolher a praia ideal no Litoral Norte de São Paulo, considerando o clima do dia, o mar e dicas de segurança. O que você procura hoje?",
};

const SUGESTOES = [
  "Quero uma praia calma para ir com crianças",
  "Alguma praia boa para surfar hoje?",
  "Vai chover? Sugira uma praia abrigada",
];

function novoId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([MENSAGEM_BOAS_VINDAS]);
  const [input, setInput] = useState("");
  const [carregando, setCarregando] = useState(false);

  const fimDaListaRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    fimDaListaRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, carregando]);

  async function enviarMensagem() {
    const texto = input.trim();
    if (!texto || carregando) return;

    const mensagemUsuario: ChatMessage = {
      id: novoId(),
      role: "user",
      content: texto,
      timestamp: Date.now(),
    };

    setMessages((atual) => [...atual, mensagemUsuario]);
    setInput("");
    setCarregando(true);

    try {
      const response = await fetch(`${apiUrl}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem: texto }),
      });

      const dados = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(dados?.detail || "Não foi possível obter uma recomendação.");
      }

      setMessages((atual) => [
        ...atual,
        {
          id: novoId(),
          role: "assistant",
          content: dados.resposta as string,
          timestamp: Date.now(),
        },
      ]);
    } catch (error) {
      setMessages((atual) => [
        ...atual,
        {
          id: novoId(),
          role: "assistant",
          content:
            error instanceof Error
              ? error.message
              : "Ocorreu um erro ao falar com a pra.ia. Tente novamente.",
          error: true,
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setCarregando(false);
      textareaRef.current?.focus();
    }
  }

  function selecionarSugestao(sugestao: string) {
    setInput(sugestao);
    textareaRef.current?.focus();
  }

  const mostrarSugestoes = messages.length === 1 && !carregando;

  return (
    <div className="flex h-dvh flex-col bg-transparent">
      <header className="border-b border-ocean-100 bg-white/80 px-4 py-3 backdrop-blur-md sm:px-6">
        <div className="mx-auto flex w-full max-w-3xl items-center gap-3">
          <WaveAvatar className="h-10 w-10" />
          <div>
            <h1 className="text-base font-semibold text-ocean-900 sm:text-lg">pra.ia</h1>
            <p className="text-xs text-ocean-900/50 sm:text-sm">
              Guia do Litoral Norte de São Paulo
            </p>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-3 py-4 sm:px-6">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-4">
          {messages.map((message) => (
            <ChatMessageBubble key={message.id} message={message} />
          ))}

          {mostrarSugestoes && (
            <div className="flex flex-wrap gap-2 pl-10">
              {SUGESTOES.map((sugestao) => (
                <button
                  key={sugestao}
                  type="button"
                  onClick={() => selecionarSugestao(sugestao)}
                  className="rounded-full border border-ocean-200 bg-white px-3.5 py-1.5 text-sm text-ocean-700 shadow-sm transition hover:border-ocean-400 hover:bg-ocean-50"
                >
                  {sugestao}
                </button>
              ))}
            </div>
          )}

          {carregando && <TypingIndicator />}

          <div ref={fimDaListaRef} />
        </div>
      </main>

      <ChatInput
        value={input}
        onChange={setInput}
        onSubmit={enviarMensagem}
        disabled={carregando}
        textareaRef={textareaRef}
      />
    </div>
  );
}
