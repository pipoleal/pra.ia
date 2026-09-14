import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { buscarPraiaPorSlug, buscarPraias, gerarSlug } from "../../lib/praias";

export async function generateStaticParams() {
  const praias = await buscarPraias();
  return praias.map((praia) => ({ slug: gerarSlug(praia) }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const praia = await buscarPraiaPorSlug(slug);
  if (!praia) return { title: "Praia não encontrada" };

  const tituloBase = `${praia.nome} — ${praia.cidade}`;
  const descricao = praia.descricao.slice(0, 155);

  return {
    title: tituloBase,
    description: descricao,
    openGraph: {
      title: `${tituloBase} | pra.ia`,
      description: descricao,
      type: "article",
      images: ["/images/sunset-litoral-norte.jpg"],
    },
    twitter: {
      card: "summary_large_image",
      title: `${tituloBase} | pra.ia`,
      description: descricao,
    },
  };
}

export default async function PraiaDetalhePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const praia = await buscarPraiaPorSlug(slug);
  if (!praia) notFound();

  const pousada = praia.comercios.find((c) => c.categoria === "Pousada" || c.categoria === "Hotel");
  const alimentacao = praia.comercios.find(
    (c) => c.categoria !== "Pousada" && c.categoria !== "Hotel"
  );

  return (
    <main className="min-h-dvh px-4 py-10 sm:px-6">
      <div className="mx-auto max-w-2xl">
        <Link href="/praias" className="text-sm text-sand-100/70 hover:text-sand-50">
          ← Todas as praias
        </Link>

        <h1 className="mt-4 text-2xl font-semibold text-sand-50 drop-shadow-sm sm:text-3xl">
          {praia.nome}
        </h1>
        <p className="text-sand-100/70">{praia.cidade} · Litoral Norte de São Paulo</p>

        <div className="mt-6 space-y-5 rounded-2xl border border-white/60 bg-sand-50/85 p-6 text-navy-900 shadow-lg backdrop-blur-md">
          <section>
            <h2 className="font-semibold">Sobre a praia</h2>
            <p className="mt-1 text-navy-800">{praia.descricao}</p>
          </section>

          <section>
            <h2 className="font-semibold">Características do mar</h2>
            <p className="mt-1 text-navy-800">{praia.caracteristicas_mar}</p>
          </section>

          <section>
            <h2 className="font-semibold">Faixa de areia</h2>
            <p className="mt-1 text-navy-800">{praia.faixa_areia}</p>
          </section>

          <section className="rounded-xl border border-red-200 bg-red-50 p-4">
            <h2 className="font-semibold text-red-800">Dicas de segurança</h2>
            <p className="mt-1 text-red-700">{praia.dicas_seguranca}</p>
          </section>

          {(pousada || alimentacao) && (
            <section className="grid gap-3 sm:grid-cols-2">
              {pousada && (
                <a
                  href={pousada.link_afiliado ?? undefined}
                  target="_blank"
                  rel="sponsored noopener noreferrer"
                  className="rounded-xl border border-turquoise-300 bg-white px-4 py-3 transition hover:border-turquoise-500"
                >
                  <p className="text-xs font-medium tracking-wide text-turquoise-700 uppercase">
                    Onde ficar
                  </p>
                  <p className="font-semibold text-navy-900">{pousada.nome}</p>
                  {pousada.destaque && (
                    <span className="mt-1 inline-block rounded-full bg-turquoise-100 px-2 py-0.5 text-[11px] font-medium text-turquoise-800">
                      Recomendado
                    </span>
                  )}
                </a>
              )}
              {alimentacao && (
                <a
                  href={alimentacao.link_afiliado ?? undefined}
                  target="_blank"
                  rel="sponsored noopener noreferrer"
                  className="rounded-xl border border-turquoise-300 bg-white px-4 py-3 transition hover:border-turquoise-500"
                >
                  <p className="text-xs font-medium tracking-wide text-turquoise-700 uppercase">
                    Onde comer
                  </p>
                  <p className="font-semibold text-navy-900">{alimentacao.nome}</p>
                  {alimentacao.destaque && (
                    <span className="mt-1 inline-block rounded-full bg-turquoise-100 px-2 py-0.5 text-[11px] font-medium text-turquoise-800">
                      Recomendado
                    </span>
                  )}
                </a>
              )}
            </section>
          )}
        </div>

        <Link
          href={`/?praia=${encodeURIComponent(praia.nome)}`}
          className="mt-6 inline-flex items-center gap-2 rounded-full bg-linear-to-br from-turquoise-500 to-navy-900 px-5 py-3 font-medium text-white shadow-md transition hover:brightness-110"
        >
          Perguntar pra pra.ia sobre {praia.nome}
        </Link>
      </div>
    </main>
  );
}
