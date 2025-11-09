import { useState } from "react";
import DashboardLayout from "@/features/DashboardLayout";
import MessageIntake from "@/features/MessageIntake";
import KnowledgeBaseChat from "@/features/KnowledgeBaseChat";

type TabId = "message-intake" | "knowledge-base";

interface TabDefinition {
  id: TabId;
  label: string;
  description: string;
}

const tabs: TabDefinition[] = [
  {
    id: "message-intake",
    label: "Message Intake Orchestration",
    description: "Categorize and triage inbox traffic by intent and urgency."
  },
  {
    id: "knowledge-base",
    label: "Knowledge Base Chat",
    description: "Surface curated answers and future RAG responses."
  }
];

export function AptifyDashboard() {
  const [activeTab, setActiveTab] = useState<TabId>("message-intake");

  const renderActivePanel = () => {
    switch (activeTab) {
      case "knowledge-base":
        return <KnowledgeBaseChat />;
      case "message-intake":
      default:
        return <MessageIntake />;
    }
  };

  return (
    <DashboardLayout title="Aptify Dashboard">
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-[18rem_minmax(0,1fr)]">
        <aside className="rounded-3xl bg-white shadow-xl shadow-slate-200/60 ring-1 ring-slate-200">
          <div className="flex flex-col gap-6 p-6">
            <header className="space-y-2">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Navigation</p>
              <h2 className="text-lg font-semibold text-slate-900">Control Center</h2>
              <p className="text-sm text-slate-500">
                Switch between orchestration and knowledge capabilities.
              </p>
            </header>
            <div role="tablist" aria-orientation="vertical" className="flex flex-col gap-3">
              {tabs.map((tab) => {
                const isActive = tab.id === activeTab;
                return (
                  <button
                    key={tab.id}
                    id={`${tab.id}-tab`}
                    type="button"
                    role="tab"
                    aria-selected={isActive}
                    aria-controls={`${tab.id}-panel`}
                    onClick={() => setActiveTab(tab.id)}
                    className={`group rounded-2xl border px-4 py-4 text-left transition ${
                      isActive
                        ? "border-sky-500/60 bg-sky-50 text-slate-900 shadow-inner shadow-slate-200/40"
                        : "border-transparent bg-slate-100 text-slate-600 hover:border-slate-300/70 hover:bg-slate-50 hover:text-slate-900"
                    }`}
                  >
                    <span className="text-sm font-semibold">{tab.label}</span>
                    <span className="mt-2 block text-xs text-slate-400 group-hover:text-slate-600">
                      {tab.description}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </aside>
        <div
          role="tabpanel"
          id={`${activeTab}-panel`}
          aria-labelledby={`${activeTab}-tab`}
          className="flex flex-col"
        >
          {renderActivePanel()}
        </div>
      </div>
    </DashboardLayout>
  );
}

export default AptifyDashboard;
