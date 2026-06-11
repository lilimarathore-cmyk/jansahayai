// app/layout.tsx
import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";


const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "JanSahayAI - छत्तीसगढ़ सरकारी योजनाएं",
  description: "जानें अपनी पात्र सरकारी योजनाओं के बारे में",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="hi">
      <body className={inter.className}>{children}</body>
    </html>
  );
}