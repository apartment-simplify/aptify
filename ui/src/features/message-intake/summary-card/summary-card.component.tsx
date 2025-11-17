interface SummaryCardProps {
  label: string;
  value: number;
  accent: string;
}

function SummaryCard({ label, value, accent }: SummaryCardProps) {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-white p-5 shadow-lg shadow-slate-200/70 ring-1 ring-slate-200 animate-fade-in-up">
      <div
        aria-hidden
        className={`pointer-events-none absolute inset-y-8 -right-6 h-32 w-32 rounded-full bg-gradient-to-br opacity-40 blur-2xl ${accent}`}
      />
      <div className="space-y-1">
        <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
        <p className="text-3xl font-semibold text-slate-900">{value}</p>
      </div>
    </div>
  );
}

export default SummaryCard;
export type { SummaryCardProps };
