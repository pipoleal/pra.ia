import Image from "next/image";

/**
 * Foto de por do sol no Litoral Norte, fornecida pelo designer.
 * Arquivo: public/images/sunset-litoral-norte.jpg
 */
export function AppBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden bg-navy-950" aria-hidden="true">
      <Image
        src="/images/sunset-litoral-norte.jpg"
        alt=""
        fill
        priority
        sizes="100vw"
        className="scale-105 object-cover object-center blur-[3px]"
      />
      <div className="absolute inset-0 bg-linear-to-b from-navy-950/55 via-navy-900/25 to-navy-950/65" />
    </div>
  );
}
