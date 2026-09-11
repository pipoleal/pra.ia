import Image from "next/image";

/**
 * Foto: Praia de Maresias, Sao Sebastiao (SP). Autor: Jorge Morales Piderit.
 * Licenca: CC0 / dominio publico (Wikimedia Commons) - uso livre, sem atribuicao obrigatoria.
 */
export function BeachBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden" aria-hidden="true">
      <Image
        src="/images/maresias-background.jpg"
        alt=""
        fill
        priority
        sizes="100vw"
        className="scale-105 object-cover object-center blur-[2px]"
      />
      <div className="absolute inset-0 bg-linear-to-b from-navy-950/65 via-navy-900/35 to-navy-950/70" />
    </div>
  );
}
