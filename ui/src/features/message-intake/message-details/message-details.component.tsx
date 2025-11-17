import type { CommunicationEntry, EmailItem } from "../message-intake.component";

interface MessageDetailsProps {
  email: EmailItem;
  communicationLog: CommunicationEntry[];
  statusBadgeClass: string;
  onBack: () => void;
}

function MessageDetails({ email, communicationLog, statusBadgeClass, onBack }: MessageDetailsProps) {
  const receivedAt = new Date(email.receivedAt).toLocaleString();
  const lastTouchTimestamp =
    communicationLog[communicationLog.length - 1]?.timestamp ?? email.receivedAt;
  const lastTouch = new Date(lastTouchTimestamp).toLocaleString();

  return (
    <div className="flex flex-col gap-5">
      <button
        type="button"
        onClick={onBack}
        className="inline-flex w-fit items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-sky-400 hover:text-slate-900"
      >
        ← Back to intake
      </button>
      <div className="grid gap-5 lg:grid-cols-[22rem_minmax(0,1fr)]">
        <div className="space-y-5 rounded-2xl bg-white p-5 shadow-xl shadow-slate-200/60 ring-1 ring-slate-200">
          <div className="space-y-1">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Message summary</p>
            <h3 className="text-lg font-semibold text-slate-900">{email.subject}</h3>
          </div>
          <div className="space-y-4 text-sm">
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400">Sender</p>
              <p className="font-medium text-slate-900">{email.sender}</p>
              <p className="text-xs text-slate-400">Received {receivedAt}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <span className="inline-flex items-center rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-600">
                {email.category}
              </span>
              <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${statusBadgeClass}`}>
                {email.status}
              </span>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400">Last action</p>
              <p className="font-medium text-slate-900">{lastTouch}</p>
            </div>
          </div>
        </div>
        <div className="rounded-3xl bg-white p-6 shadow-xl shadow-slate-200/60 ring-1 ring-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Communication log</p>
              <h3 className="text-lg font-semibold text-slate-900">Conversation timeline</h3>
            </div>
            <span className="text-xs font-medium text-slate-400">
              {communicationLog.length} {communicationLog.length === 1 ? "entry" : "entries"}
            </span>
          </div>
          {communicationLog.length === 0 ? (
            <div className="mt-6 rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500">
              No communications recorded yet. They will appear here once synced.
            </div>
          ) : (
            <ul className="mt-6 space-y-6">
              {communicationLog.map((entry, index) => (
                <li key={entry.id} className="relative pl-10">
                  {index < communicationLog.length - 1 && (
                    <span className="absolute left-4 top-7 h-full w-px bg-slate-200" aria-hidden />
                  )}
                  <span className="absolute left-0 top-3 inline-flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 bg-white text-xs font-semibold text-slate-500 shadow-sm">
                    {index + 1}
                  </span>
                  <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 shadow-sm">
                    <div className="flex flex-wrap items-center justify-between gap-2 text-xs uppercase tracking-wide text-slate-400">
                      <span>{entry.author}</span>
                      <span>{new Date(entry.timestamp).toLocaleString()}</span>
                    </div>
                    <p className="mt-2 text-sm text-slate-700">{entry.content}</p>
                    <span className="mt-3 inline-flex items-center gap-2 text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-slate-400">
                      <span className="h-1.5 w-1.5 rounded-full bg-sky-400" />
                      {entry.channel === "email" ? "Email" : "Ops Note"}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export default MessageDetails;
export type { MessageDetailsProps };
