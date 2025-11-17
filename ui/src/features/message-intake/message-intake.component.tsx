import { useMemo, useState } from "react";

type EmailCategory =
  | "Billing"
  | "Product Inquiry"
  | "Support"
  | "Partnerships"
  | "Uncategorized";

type EmailStatus = "New" | "In Review" | "Resolved";

export interface EmailItem {
  id: string;
  sender: string;
  subject: string;
  category: EmailCategory;
  status: EmailStatus;
  receivedAt: string;
}

const mockEmails: EmailItem[] = [
  {
    id: "1",
    sender: "lena.hart@lumoshealth.io",
    subject: "Monthly invoice for the premium plan",
    category: "Billing",
    status: "Resolved",
    receivedAt: "2024-05-02T14:20:00Z"
  },
  {
    id: "2",
    sender: "mason.lee@northwind.com",
    subject: "Clarification needed on onboarding flow",
    category: "Product Inquiry",
    status: "In Review",
    receivedAt: "2024-05-03T09:45:00Z"
  },
  {
    id: "3",
    sender: "support@evergreenpartners.co",
    subject: "Unable to access archived reports",
    category: "Support",
    status: "New",
    receivedAt: "2024-05-04T12:02:00Z"
  },
  {
    id: "4",
    sender: "jasmine@orbitalsystems.ai",
    subject: "Partnership inquiry for embedded knowledge base",
    category: "Partnerships",
    status: "In Review",
    receivedAt: "2024-05-04T18:22:00Z"
  },
  {
    id: "5",
    sender: "ryan.fischer@paperplaneapps.com",
    subject: "Bug report: message deduplication failing",
    category: "Support",
    status: "Resolved",
    receivedAt: "2024-05-05T10:10:00Z"
  },
  {
    id: "6",
    sender: "general@unknown.com",
    subject: "Need help understanding Aptify pricing tiers",
    category: "Uncategorized",
    status: "New",
    receivedAt: "2024-05-06T08:15:00Z"
  }
];

const categoryFilterOptions: Array<EmailCategory | "All"> = [
  "All",
  "Billing",
  "Product Inquiry",
  "Support",
  "Partnerships",
  "Uncategorized"
];

const statusFilterOptions: Array<EmailStatus | "All"> = ["All", "New", "In Review", "Resolved"];

const statusAccentClass: Record<EmailStatus, string> = {
  New: "border border-amber-500 bg-amber-500 text-white shadow-[0_0_0_1px_rgba(249,115,22,0.35)] dark:bg-amber-500 dark:text-amber-50",
  "In Review":
    "border border-sky-500 bg-sky-500 text-white shadow-[0_0_0_1px_rgba(14,165,233,0.35)] dark:bg-sky-500 dark:text-sky-50",
  Resolved:
    "border border-emerald-500 bg-emerald-500 text-white shadow-[0_0_0_1px_rgba(16,185,129,0.35)] dark:bg-emerald-500 dark:text-emerald-50"
};

const categoryAccentClass: Record<EmailCategory, string> = {
  Billing: "text-amber-500",
  "Product Inquiry": "text-sky-500",
  Support: "text-emerald-500",
  Partnerships: "text-fuchsia-500",
  Uncategorized: "text-slate-400"
};

export function MessageIntake() {
  const [selectedCategory, setSelectedCategory] = useState<EmailCategory | "All">("All");
  const [selectedStatus, setSelectedStatus] = useState<EmailStatus | "All">("All");

  const summary = useMemo(() => {
    const categorizedCount = mockEmails.filter((email) => email.category !== "Uncategorized").length;
    const uncategorizedCount = mockEmails.length - categorizedCount;
    return {
      total: mockEmails.length,
      categorized: categorizedCount,
      uncategorized: uncategorizedCount
    };
  }, []);

  const filteredEmails = useMemo(() => {
    return mockEmails.filter((email) => {
      const matchesCategory =
        selectedCategory === "All" ? true : email.category === selectedCategory;
      const matchesStatus = selectedStatus === "All" ? true : email.status === selectedStatus;
      return matchesCategory && matchesStatus;
    });
  }, [selectedCategory, selectedStatus]);

  return (
    <section className="flex h-full flex-col gap-6">
      <header className="space-y-2 animate-fade-in-up">
        <h2 className="text-lg font-semibold text-slate-900">Message Intake Orchestration</h2>
        <p className="text-sm text-slate-500">
          Monitor and categorize recent messages funneled through the Aptify intake pipeline.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-3">
        <SummaryCard label="Total messages" value={summary.total} accent="from-slate-500 to-slate-700" />
        <SummaryCard
          label="Categorized"
          value={summary.categorized}
          accent="from-sky-500 to-indigo-600"
        />
        <SummaryCard
          label="Uncategorized"
          value={summary.uncategorized}
          accent="from-amber-500 to-orange-600"
        />
      </div>

      <div className="flex flex-col gap-4 rounded-2xl bg-white p-5 shadow-xl shadow-slate-200/60 ring-1 ring-slate-200">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <p className="text-sm font-medium text-slate-600">Filter messages</p>
          <div className="flex flex-wrap gap-3">
            <label className="flex items-center gap-2 text-sm text-slate-600">
              <span className="hidden">Category</span>
              <select
                aria-label="Filter by category"
                value={selectedCategory}
                onChange={(event) =>
                  setSelectedCategory(event.target.value as EmailCategory | "All")
                }
                className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm transition focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
              >
                {categoryFilterOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-600">
              <span className="hidden">Status</span>
              <select
                aria-label="Filter by status"
                value={selectedStatus}
                onChange={(event) => setSelectedStatus(event.target.value as EmailStatus | "All")}
                className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm transition focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
              >
                {statusFilterOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-100 text-xs uppercase tracking-tight text-slate-500">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Sender</th>
                <th className="px-4 py-3 text-left font-medium">Subject</th>
                <th className="px-4 py-3 text-left font-medium">Category</th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {filteredEmails.map((email, index) => (
                <tr
                  key={email.id}
                  className="animate-fade-in-up transition hover:bg-slate-50"
                  style={{ animationDelay: `${index * 60}ms` }}
                >
                  <td className="px-4 py-4 align-top text-sm font-medium">
                    <div className="flex flex-col">
                      <span>{email.sender}</span>
                      <span className="text-xs text-slate-400">
                        {new Date(email.receivedAt).toLocaleString()}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-4 align-top text-sm text-slate-600">{email.subject}</td>
                  <td className="px-4 py-4 align-top text-sm font-medium">
                    <span className={categoryAccentClass[email.category]}>{email.category}</span>
                  </td>
                  <td className="px-4 py-4 align-top">
                    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${statusAccentClass[email.status]}`}>
                      {email.status}
                    </span>
                  </td>
                </tr>
              ))}
              {filteredEmails.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-4 py-10 text-center text-sm text-slate-400">
                    No messages found for the selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

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

export default MessageIntake;
