const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export interface Comercio {
  nome: string;
  categoria: string;
  link_afiliado: string | null;
  distancia_areia_metros: number | null;
}

export interface Praia {
  id: number;
  nome: string;
  cidade: string;
  latitude: number;
  longitude: number;
  nivel_infraestrutura: number;
  descricao: string;
  caracteristicas_mar: string;
  faixa_areia: string;
  dicas_seguranca: string;
  comercios: Comercio[];
}

export async function buscarPraias(): Promise<Praia[]> {
  try {
    const resposta = await fetch(`${apiUrl}/praias/`, {
      next: { revalidate: 3600 },
    });
    if (!resposta.ok) return [];
    return (await resposta.json()) as Praia[];
  } catch {
    return [];
  }
}

function normalizar(texto: string): string {
  return texto
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function gerarSlug(praia: Pick<Praia, "nome" | "cidade">): string {
  const nomeBase = praia.nome.includes(praia.cidade)
    ? praia.nome.replace(`(${praia.cidade})`, "").trim()
    : praia.nome;
  return `${normalizar(nomeBase)}-${normalizar(praia.cidade)}`;
}

export async function buscarPraiaPorSlug(slug: string): Promise<Praia | null> {
  const praias = await buscarPraias();
  return praias.find((praia) => gerarSlug(praia) === slug) ?? null;
}
