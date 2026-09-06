import type { Metadata } from "next";

import { AppNav } from "@/components/nav/AppNav";
import { SynthesisSessionProvider } from "@/lib/hooks/useSynthesisSession";

import "./globals.css";

export const metadata: Metadata = {
  title: "VaaniLab — Indic TTS Studio",
  description: "Interactive pronunciation-aware, controllable, streaming Indic text-to-speech.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex h-screen flex-col overflow-hidden">
        <SynthesisSessionProvider>
          <AppNav />
          <main className="min-h-0 flex-1 overflow-auto">{children}</main>
        </SynthesisSessionProvider>
      </body>
    </html>
  );
}
