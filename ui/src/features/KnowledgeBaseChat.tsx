import { FormEvent, useState } from "react";

type ChatAuthor = "user" | "ai";

interface ChatMessage {
  id: string;
  author: ChatAuthor;
  content: string;
  timestamp: string;
}

const mockChat: ChatMessage[] = [
  {
    id: "msg-1",
    author: "user",
    content: "Hi Aptify, can you explain how message classification is prioritized?",
    timestamp: "2024-05-05T12:05:00Z"
  },
  {
    id: "msg-2",
    author: "ai",
    content:
      "Absolutely. Messages are scored based on sender reputation, detected urgency, and topic alignment with your configured workstreams.",
    timestamp: "2024-05-05T12:06:00Z"
  },
  {
    id: "msg-3",
    author: "user",
    content: "Great. Where does the knowledge base pull context from today?",
    timestamp: "2024-05-05T12:06:30Z"
  },
  {
    id: "msg-4",
    author: "ai",
    content:
      "The current setup aggregates your curated playbooks, tagged support tickets, and the Aptify product guide. We can expand this once RAG is enabled.",
    timestamp: "2024-05-05T12:07:10Z"
  }
];

export function KnowledgeBaseChat() {
  const [draft, setDraft] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!draft.trim()) {
      return;
    }

    // Future implementation will handle message submission to the Aptify backend.
    setDraft("");
  };

  return (
    <section className="flex h-full flex-col gap-6">
      <header className="space-y-2 animate-fade-in-up">
        <h2 className="text-lg font-semibold text-slate-900">Knowledge Base Chat</h2>
        <p className="text-sm text-slate-500">
          Explore curated answers and contextual responses. RAG capabilities will plug in here soon.
        </p>
      </header>

      <div className="flex h-full flex-col overflow-hidden rounded-3xl bg-white shadow-xl shadow-slate-200/60 ring-1 ring-slate-200">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div className="space-y-1">
            <p className="text-sm font-medium text-slate-700">Live context</p>
            <p className="text-xs text-slate-500">
              Responses blend the existing knowledge base with future RAG enhancements.
            </p>
          </div>
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-600">
            Stable · v0.4
          </div>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
          {mockChat.map((message, index) => {
            const isUser = message.author === "user";
            return (
              <div
                key={message.id}
                className={`flex ${isUser ? "justify-end" : "justify-start"} animate-fade-in-up`}
                style={{ animationDelay: `${index * 70}ms` }}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-lg ring-1 ${
                    isUser
                      ? "bg-sky-100 text-sky-900 ring-sky-400/50"
                      : "bg-slate-100 text-slate-700 ring-slate-200"
                  }`}
                >
                  <p>{message.content}</p>
                  <span className="mt-2 block text-[0.7rem] uppercase tracking-wide text-slate-400">
                    {new Date(message.timestamp).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit"
                    })}{" "}
                    · {message.author === "user" ? "You" : "Aptify AI"}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        <form onSubmit={handleSubmit} className="border-t border-slate-200 bg-slate-50 px-6 py-4">
          <label htmlFor="aptify-chat-input" className="sr-only">
            Ask something about Aptify
          </label>
          <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 shadow-inner shadow-slate-200/60 focus-within:border-sky-500 focus-within:ring-2 focus-within:ring-sky-500/30">
            <input
              id="aptify-chat-input"
              name="prompt"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask something about Aptify…"
              className="w-full bg-transparent placeholder:text-slate-400 focus:outline-none"
            />
            <button
              type="submit"
              className="inline-flex items-center gap-2 rounded-full bg-sky-500/90 px-4 py-2 font-semibold text-white shadow-sm transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
              disabled={!draft.trim()}
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}

export default KnowledgeBaseChat;
