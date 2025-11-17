import type { CommunicationEntry, EmailItem } from "../message-intake.component";
import EmailCommunicationTimeline from "./email-communication-timeline.component";

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
        <EmailCommunicationTimeline />
      </div>
    </div>
  );
}

export default MessageDetails;
export type { MessageDetailsProps };
