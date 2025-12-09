import { FormEvent, useState } from "react";
import { useKnowledgeQueryMutation } from "./knowledge-query.mutation";

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
    content:
      "Hi Aptify, can you explain how message classification is prioritized?",
    timestamp: "2024-05-05T12:05:00Z",
  },
  {
    id: "msg-2",
    author: "ai",
    content:
      "Absolutely. Messages are scored based on sender reputation, detected urgency, and topic alignment with your configured workstreams.",
    timestamp: "2024-05-05T12:06:00Z",
  },
  {
    id: "msg-3",
    author: "user",
    content: "Great. Where does the knowledge base pull context from today?",
    timestamp: "2024-05-05T12:06:30Z",
  },
  {
    id: "msg-4",
    author: "ai",
    content:
      "The current setup aggregates your curated playbooks, tagged support tickets, and the Aptify product guide. We can expand this once RAG is enabled.",
    timestamp: "2024-05-05T12:07:10Z",
  },
];

export function KnowledgeBaseChat() {
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>(mockChat);

  const { mutate: knowledgeQueryMutation, isPending: isKnowledgeQueryPending } =
    useKnowledgeQueryMutation({
      onSuccess: (data) => {
        const aiMessage: ChatMessage = {
          id: `ai-${Date.now()}`,
          author: "ai",
          content: data.answer,
          timestamp: data.generated_at,
        };
        setMessages((prev) => [...prev, aiMessage]);
      },
    });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!draft.trim()) {
      return;
    }

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      author: "user",
      content: draft.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    knowledgeQueryMutation(userMessage.content);
    setDraft("");
  };

  return (
    <section className="flex h-full flex-col gap-6">
      <header className="space-y-2 animate-fade-in-up">
        <h2 className="text-lg font-semibold text-slate-900">
          Knowledge Base Chat
        </h2>
        <p className="text-sm text-slate-500">
          Explore curated answers and contextual responses. RAG capabilities
          will plug in here soon.
        </p>
      </header>

      <div className="flex h-full flex-col overflow-hidden rounded-3xl bg-white shadow-xl shadow-slate-200/60 ring-1 ring-slate-200">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div className="space-y-1">
            <p className="text-sm font-medium text-slate-700">Live context</p>
            <p className="text-xs text-slate-500">
              Responses blend the existing knowledge base with future RAG
              enhancements.
            </p>
          </div>
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-600">
            Stable · v0.4
          </div>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
          {messages.map((message, index) => {
            const isUser = message.author === "user";
            return (
              <div
                key={message.id}
                className={`flex ${
                  isUser ? "justify-end" : "justify-start"
                } animate-fade-in-up`}
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
                      minute: "2-digit",
                    })}{" "}
                    · {message.author === "user" ? "You" : "Aptify AI"}
                  </span>
                </div>
              </div>
            );
          })}
          {isKnowledgeQueryPending && (
            <div
              className="flex justify-start animate-fade-in-up"
              aria-live="polite"
            >
              <div className="flex items-center gap-2 max-w-[80%] rounded-2xl rounded-b-2xl rounded-r-2xl px-4 py-3 text-sm shadow-lg ring-1 ring-slate-200 bg-slate-100 text-slate-700">
                <svg
                  className="h-4 w-4 animate-spin text-slate-500"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <circle cx="12" cy="12" r="10" strokeOpacity="0.2" />
                  <path d="M22 12a10 10 0 0 1-10 10" />
                </svg>
                <span>Thinking…</span>
              </div>
            </div>
          )}
        </div>

        <form
          onSubmit={handleSubmit}
          className="border-t border-slate-200 bg-slate-50 px-6 py-4"
        >
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
              disabled={!draft.trim() || isKnowledgeQueryPending}
            >
              {isKnowledgeQueryPending ? "Sending…" : "Send"}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}

export default KnowledgeBaseChat;
