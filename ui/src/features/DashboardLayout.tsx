import type { ReactNode } from "react";

interface DashboardLayoutProps {
  title: string;
  children: ReactNode;
}

export function DashboardLayout({ title, children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-white text-slate-900 antialiased">
      <header className="border-b border-slate-200 bg-white">
        <nav className="flex w-full items-center justify-between py-5">
          <div className="flex items-center gap-3">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-sky-500/10 text-sky-500">
              <span className="text-lg font-semibold">A</span>
            </div>
            <div>
              <p className="text-lg font-semibold text-slate-900">{title}</p>
              <span className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Insight Control Hub
              </span>
            </div>
          </div>
          <div className="hidden items-center gap-3 text-sm text-slate-500 sm:flex">
            <span>Last sync · 3m ago</span>
            <span className="h-1 w-1 rounded-full bg-emerald-500" />
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
