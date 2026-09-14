import type { MetadataRoute } from "next";
import { buscarPraias, gerarSlug } from "./lib/praias";

const SITE_URL = "https://pra-ia.vercel.app";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const praias = await buscarPraias();

  const paginasPraias = praias.map((praia) => ({
    url: `${SITE_URL}/praias/${gerarSlug(praia)}`,
    lastModified: new Date(),
  }));

  return [
    { url: SITE_URL, lastModified: new Date() },
    { url: `${SITE_URL}/praias`, lastModified: new Date() },
    ...paginasPraias,
  ];
}
