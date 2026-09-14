import type { Metadata } from "next";
import Link from "next/link";
import { buscarPraias, gerarSlug } from "../lib/praias";

export const metadata: Metadata = {
  title: "Praias do Litoral Norte de São Paulo",
  description:
    "Guia completo das praias do Litoral Norte de São Paulo: São Sebastião, Ilhabela, Caraguatatuba e Ubatuba. Mar, faixa de areia, dicas de segurança e onde ficar em cada uma.",
  openGraph: {
    title: "Praias do Litoral Norte de São Paulo | pra.ia",
    description:
      "Guia completo das praias do Litoral Norte de SP, com clima, mar e dicas de segurança.",
    images: ["/images/sunset-litoral-norte.jpg"],
  },
};

export default async function PraiasPage() {
  const praias = await buscarPraias();

  return (
    <main className="min-h-dvh px-4 py-10 sm:px-6">
      <div className="mx-auto max-w-5xl">
        <Link href="/" className="text-sm text-sand-100/70 hover:text-sand-50">
          ← Voltar para o chat
        </Link>

        <header className="mb-8 mt-4 text-center">
          <h1 className="text-2xl font-semibold text-sand-50 drop-shadow-sm sm:text-3xl">
            Praias do Litoral Norte de São Paulo
          </h1>
          <p className="mt-2 text-sand-100/70">
            {praias.length} praias com clima, características do mar e dicas de segurança
          </p>
        </header>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {praias.map((praia) => (
            <Link
              key={praia.id}
              href={`/praias/${gerarSlug(praia)}`}
              className="rounded-2xl border border-white/60 bg-sand-50/80 p-5 shadow-md backdrop-blur-md transition hover:border-turquoise-300 hover:bg-sand-50"
            >
              <h2 className="text-lg font-semibold text-navy-900">{praia.nome}</h2>
              <p className="text-sm text-navy-700">{praia.cidade}</p>
              <p className="mt-2 line-clamp-3 text-sm text-navy-800/80">{praia.descricao}</p>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
