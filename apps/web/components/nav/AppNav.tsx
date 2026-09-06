"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/studio", label: "Synthesis Studio" },
  { href: "/lexicon", label: "Pronunciation Lexicon" },
  { href: "/diagnostics", label: "Diagnostics" },
  { href: "/status", label: "System Status" },
];

export function AppNav() {
  const pathname = usePathname();
  return (
    <header className="flex h-12 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4">
      <div className="flex items-center gap-6">
        <span className="text-sm font-semibold tracking-tight text-slate-900">VaaniLab</span>
        <nav className="flex gap-1" aria-label="Primary">
          {LINKS.map((link) => {
            const active = pathname?.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`focus-ring rounded-md px-2.5 py-1 text-sm transition-colors ${
                  active ? "bg-sky-50 text-sky-700" : "text-slate-600 hover:bg-slate-100"
                }`}
                aria-current={active ? "page" : undefined}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
      <span className="text-xs text-slate-400">Mock providers — Phase 1 vertical slice</span>
    </header>
  );
}
