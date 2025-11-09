import type { ReactNode } from "react";

interface DashboardLayoutProps {
  title: string;
  children: ReactNode;
}

export function DashboardLayout({ title, children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 antialiased">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,_rgba(68,94,255,0.18),_transparent_55%)]" />
      <div className="absolute inset-0 -z-20 bg-[radial-gradient(circle_at_bottom,_rgba(16,176,255,0.15),_transparent_45%)]" />

      <header className="border-b border-slate-900/80 bg-slate-950/90 backdrop-blur">
        <nav className="flex w-full items-center justify-between py-5">
          <div className="flex items-center gap-3">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-sky-500/10">
              <span className="text-lg font-semibold text-sky-400">A</span>
            </div>
            <div>
              <p className="text-lg font-semibold text-slate-100">{title}</p>
              <span className="text-xs uppercase tracking-[0.2em] text-slate-500">
                Insight Control Hub
              </span>
            </div>
          </div>
          <div className="hidden items-center gap-2 text-sm text-slate-400 sm:flex">
            <span>Last sync · 3m ago</span>
            <span className="h-1 w-1 rounded-full bg-emerald-400" />
            <span>Status: Healthy</span>
          </div>
        </nav>
      </header>

      <main className="flex w-full flex-1 flex-col gap-8 py-10">
        {children}
      </main>
    </div>
  );
}

export default DashboardLayout;
