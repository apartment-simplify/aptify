import { useMemo, useState } from "react";

type EmailDirection = "inbound" | "outbound";

interface EmailMessage {
  id: string;
  direction: EmailDirection;
  sender: string;
  recipients: string[];
  timestamp: string;
  subject: string;
  body: string;
}

const mockTimeline: EmailMessage[] = [
  {
    id: "1",
    direction: "inbound",
    sender: "laura.solis@northwind.co",
    recipients: ["ops@aptify.com"],
    timestamp: "2024-05-05T09:14:00Z",
    subject: "Clarification on onboarding timeline",
    body: "Hi team, could you confirm whether the onboarding automations will be live before our June rollout? We want to ensure we communicate accurate dates to our CS org."
  },
  {
    id: "2",
    direction: "outbound",
    sender: "samir.patel@aptify.com",
    recipients: ["laura.solis@northwind.co"],
    timestamp: "2024-05-05T09:32:00Z",
    subject: "Re: Clarification on onboarding timeline",
    body: "Thanks for reaching out, Laura! The automations are in final QA and will be ready by May 28. I’ve attached a brief deployment checklist so you can prep the rollout communications."
  },
  {
    id: "3",
    direction: "inbound",
    sender: "laura.solis@northwind.co",
    recipients: ["ops@aptify.com"],
    timestamp: "2024-05-05T09:48:00Z",
    subject: "Re: Clarification on onboarding timeline",
    body: "Appreciate the quick response. Could you also confirm whether message deduplication is part of this release? We have an exec review on Friday and would love to include it."
  },
  {
    id: "4",
    direction: "outbound",
    sender: "samir.patel@aptify.com",
    recipients: ["laura.solis@northwind.co"],
    timestamp: "2024-05-05T10:05:00Z",
    subject: "Re: Clarification on onboarding timeline",
    body: "Yes, deduplication will ship alongside the automations. I’ll follow up with a short Loom walkthrough this afternoon so you can showcase it during the exec review."
  }
];

const directionStyles: Record<EmailDirection, string> = {
  inbound: "border-sky-200 bg-sky-50 text-slate-800",
  outbound: "border-emerald-200 bg-emerald-50 text-slate-800"
};

const accentDot: Record<EmailDirection, string> = {
  inbound: "bg-sky-400",
  outbound: "bg-emerald-400"
};

function EmailCommunicationTimeline() {
  const [draft, setDraft] = useState("");
  const [showAIDraft, setShowAIDraft] = useState(false);

  const sortedMessages = useMemo(
    () =>
      [...mockTimeline].sort(
        (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      ),
    []
  );

  return (
    <section className="flex flex-col gap-6 rounded-3xl bg-white p-6 shadow-2xl shadow-slate-200/70 ring-1 ring-slate-200">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Conversation timeline</p>
        <h2 className="text-xl font-semibold text-slate-900">Email Communication</h2>
        <p className="text-sm text-slate-500">
          Chronological record of every inbound and outbound email within this thread.
        </p>
      </header>

      <div className="space-y-5">
        {sortedMessages.map((message, index) => {
          const isInbound = message.direction === "inbound";
          const alignment = isInbound ? "items-start" : "items-end";
          const bubbleAlignment = isInbound ? "text-left" : "text-right";
          const borderClasses = directionStyles[message.direction];

          return (
            <article key={message.id} className={`flex flex-col gap-2 ${alignment}`}>
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-slate-400">
                <span className={`h-1.5 w-1.5 rounded-full ${accentDot[message.direction]}`} />
                <span>{isInbound ? "Inbound" : "Outbound"} email</span>
                <span>·</span>
                <span>{new Date(message.timestamp).toLocaleString()}</span>
              </div>
              <div
                className={`w-full rounded-2xl border px-5 py-4 shadow-lg shadow-slate-200/70 ${borderClasses} ${bubbleAlignment}`}
              >
                <div className="space-y-2 text-sm text-slate-600">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                    From: <span className="text-slate-700">{message.sender}</span>
                  </p>
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                    To: <span className="text-slate-700">{message.recipients.join(", ")}</span>
                  </p>
                  <p className="text-sm font-semibold text-slate-900">{message.subject}</p>
                  <p>{message.body}</p>
                </div>
              </div>
              {index < sortedMessages.length - 1 && (
                <div className="flex w-full justify-center">
                  <span className="h-6 w-px bg-slate-200" aria-hidden />
                </div>
              )}
            </article>
          );
        })}
      </div>

      <div className="space-y-4 rounded-3xl border border-slate-200 bg-slate-50 p-5">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Reply</p>
          <h3 className="text-lg font-semibold text-slate-900">Respond to this thread</h3>
        </div>
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Type your reply here..."
          className="min-h-[120px] w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 shadow-inner shadow-slate-200/60 focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/30"
        />
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-full bg-slate-900 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-700"
          >
            Send Reply
          </button>
          <button
            type="button"
            onClick={() => setShowAIDraft(true)}
            className="inline-flex items-center justify-center rounded-full border border-sky-500/60 bg-white px-5 py-2 text-sm font-semibold text-sky-600 shadow-sm transition hover:border-sky-500 hover:text-sky-700"
          >
            AI Draft Response
          </button>
        </div>
        {showAIDraft && (
          <div className="space-y-2 rounded-2xl border border-dashed border-sky-200 bg-white/70 px-4 py-3 text-sm text-slate-700">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-sky-500">
              <span className="h-1.5 w-1.5 rounded-full bg-sky-400" aria-hidden />
              Suggested draft
            </div>
            <p>
              Hi Laura, confirming that onboarding automations and message deduplication will both be
              live by May 28. I’ll send a Loom walkthrough later today so you can showcase the flow
              during Friday’s exec review. Let us know if you want to include anything else.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}

export default EmailCommunicationTimeline;
