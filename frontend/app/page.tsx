"use client";

import { FormEvent, useState } from "react";


const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";


export default function Home() {
  const [mensagem, setMensagem] = useState("");
  const [resposta, setResposta] = useState("");
  const [carregando, setCarregando] = useState(false);

  async function enviarMensagem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!mensagem.trim()) return;

    setCarregando(true);
    try {
      const response = await fetch(`${apiUrl}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem }),
      });

      if (!response.ok) {
        throw new Error("Nao foi possivel obter uma recomendacao.");
      }

      const data: { resposta: string } = await response.json();
      setResposta(data.resposta);
    } catch (error) {
      setResposta(error instanceof Error ? error.message : "Ocorreu um erro.");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <main>
      <h1>pra.ia</h1>
      <form onSubmit={enviarMensagem}>
        <label htmlFor="mensagem">Como posso ajudar?</label>
        <textarea
          id="mensagem"
          value={mensagem}
          onChange={(event) => setMensagem(event.target.value)}
          placeholder="Ex.: Quero uma praia tranquila para ir com criancas"
          required
        />
        <button type="submit" disabled={carregando}>
          {carregando ? "Buscando..." : "Enviar"}
        </button>
      </form>
      {resposta && <p>{resposta}</p>}
    </main>
  );
}
