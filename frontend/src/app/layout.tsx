import type { Metadata } from "next";
import "./globals.css";
import { LanguageProvider } from "@/components/language-provider";

export const metadata: Metadata = {
  title: "MoneyGraph",
  description: "Анализ графа переводов и объяснимые гипотезы расследования MoneyGraph.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body><LanguageProvider>{children}</LanguageProvider></body>
    </html>
  );
}
