import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "Placement Twin AI - Personalized Career Mentor",
  description: "An autonomous, multi-agent AI career twin that guides students to recruitment readiness.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`} suppressHydrationWarning>
      <body className="min-h-full bg-[#090d1a] text-slate-100 selection:bg-blue-500/30 selection:text-blue-200" suppressHydrationWarning>
        <div className="glow-bg" />
        <main className="relative z-10 flex flex-col min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
