import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { AppBackground } from "./components/AppBackground";
import { ServiceWorkerRegister } from "./components/ServiceWorkerRegister";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const DESCRICAO =
  "Guia do Litoral Norte de São Paulo com IA: descubra a praia ideal em São Sebastião, Ilhabela, Caraguatatuba e Ubatuba, com clima, dicas de segurança e onde ficar.";

export const metadata: Metadata = {
  metadataBase: new URL("https://pra-ia.vercel.app"),
  title: {
    default: "pra.ia — Guia do Litoral Norte de São Paulo",
    template: "%s | pra.ia",
  },
  description: DESCRICAO,
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "pra.ia",
  },
  icons: {
    icon: [
      { url: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
      { url: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
    ],
    apple: [{ url: "/icons/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
  },
  openGraph: {
    title: "pra.ia — Guia do Litoral Norte de São Paulo",
    description: DESCRICAO,
    url: "https://pra-ia.vercel.app",
    siteName: "pra.ia",
    locale: "pt_BR",
    type: "website",
    images: ["/images/sunset-litoral-norte.jpg"],
  },
  twitter: {
    card: "summary_large_image",
    title: "pra.ia — Guia do Litoral Norte de São Paulo",
    description: DESCRICAO,
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#0d182c",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR" className={inter.variable}>
      <body>
        <AppBackground />
        <ServiceWorkerRegister />
        {children}
      </body>
    </html>
  );
}
