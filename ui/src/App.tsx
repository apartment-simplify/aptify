import { useQuery } from "@tanstack/react-query";
import { incremented, decremented, reset } from "@/features/counter/counterSlice";
import { useAppDispatch, useAppSelector } from "@/app/hooks";

interface PlaceholderTodo {
  id: number;
  title: string;
  completed: boolean;
}

async function fetchTodo(): Promise<PlaceholderTodo> {
  const response = await fetch("https://jsonplaceholder.typicode.com/todos/1");
  if (!response.ok) {
    throw new Error("Failed to fetch TODO");
  }

  return response.json();
}

function App() {
  const dispatch = useAppDispatch();
  const count = useAppSelector((state) => state.counter.value);

  const todoQuery = useQuery({
    queryKey: ["todo", 1],
    queryFn: fetchTodo
  });

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-12 text-slate-50">
      <header className="text-center">
        <h1 className="text-4xl font-semibold tracking-tight">Aptify UI</h1>
        <p className="mt-2 text-lg text-slate-300">
          React + Vite with Tailwind, Redux Toolkit, and TanStack Query
        </p>
      </header>
      <section className="mt-10 flex w-full max-w-xl flex-col gap-8 rounded-xl border border-slate-800 bg-slate-900/70 p-8 shadow-xl">
        <div>
          <h2 className="text-2xl font-semibold text-violet-300">Global Counter</h2>
          <p className="mt-2 text-sm text-slate-400">
            State managed via Redux Toolkit. Use the buttons to update the global value.
          </p>
          <div className="mt-6 flex items-center gap-3">
            <button
              type="button"
              className="rounded bg-slate-800 px-3 py-2 text-sm font-semibold hover:bg-slate-700"
              onClick={() => dispatch(decremented())}
            >
              -1
            </button>
            <span className="min-w-[5rem] text-center text-xl font-medium">{count}</span>
            <button
              type="button"
              className="rounded bg-slate-800 px-3 py-2 text-sm font-semibold hover:bg-slate-700"
              onClick={() => dispatch(incremented())}
            >
              +1
            </button>
            <button
              type="button"
              className="rounded border border-violet-400 px-3 py-2 text-sm font-semibold text-violet-300 transition-colors hover:bg-violet-500/10"
              onClick={() => dispatch(reset())}
            >
              Reset
            </button>
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-semibold text-emerald-300">Todo Query</h2>
          <p className="mt-2 text-sm text-slate-400">
            Data fetched with TanStack Query. Check Devtools in the bottom-right corner.
          </p>

          <div className="mt-6 rounded-lg border border-slate-800 bg-slate-950/80 p-4">
            {todoQuery.isPending && <p>Loading placeholder TODO…</p>}
            {todoQuery.isError && (
              <p className="text-rose-300">
                Could not load data: {todoQuery.error.message}
              </p>
            )}
            {todoQuery.isSuccess && (
              <dl className="space-y-2">
                <div className="flex items-center justify-between">
                  <dt className="text-slate-400">ID</dt>
                  <dd className="font-mono text-sm text-slate-100">{todoQuery.data.id}</dd>
                </div>
                <div>
                  <dt className="text-slate-400">Title</dt>
                  <dd className="text-slate-100">{todoQuery.data.title}</dd>
                </div>
                <div className="flex items-center justify-between">
                  <dt className="text-slate-400">Completed</dt>
                  <dd className="font-semibold">
                    {todoQuery.data.completed ? "Yes" : "Not yet"}
                  </dd>
                </div>
              </dl>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

export default App;
