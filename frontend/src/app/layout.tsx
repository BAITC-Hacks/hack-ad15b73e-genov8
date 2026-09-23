import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HackAlem MoneyGraph",
  description: "HackAlem MoneyGraph solution",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
