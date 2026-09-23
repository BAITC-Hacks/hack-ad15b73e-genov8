import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MoneyGraph | Investigation Workspace",
  description: "Explainable AML network investigation workspace for HackAlem.",
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
