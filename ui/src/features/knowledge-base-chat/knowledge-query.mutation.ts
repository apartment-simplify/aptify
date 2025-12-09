import {
  useMutation,
  UseMutationOptions,
  UseMutationResult
} from "@tanstack/react-query";

export interface KnowledgeAnswer {
  answer: string;
  generated_at: string;
  sources: { source: string; snippet: string }[];
}

interface KnowledgeQueryVariables {
  question: string;
  onChunk?: (chunk: string) => void;
}

interface StreamEvent {
  type: "chunk" | "done";
  chunk?: string;
  answer?: string;
  sources?: { source: string; snippet: string }[];
  generated_at?: string;
}

const streamKnowledge = async (
  question: string,
  onChunk?: (chunk: string) => void
): Promise<KnowledgeAnswer> => {
  const response = await fetch("http://localhost:8000/knowledge/query/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      question
    })
  });

  if (!response.ok) {
    throw new Error("Failed to stream knowledge answer");
  }

  if (!response.body) {
    throw new Error("Server did not return a streaming response");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  const finalize = (event: StreamEvent): KnowledgeAnswer => ({
    answer: event.answer ?? "",
    sources: event.sources ?? [],
    generated_at: event.generated_at ?? new Date().toISOString()
  });

  const processLine = (line: string): KnowledgeAnswer | null => {
    const trimmed = line.trim();
    if (!trimmed) {
      return null;
    }
    let event: StreamEvent;
    try {
      event = JSON.parse(trimmed) as StreamEvent;
    } catch {
      return null;
    }
    if (event.type === "chunk" && event.chunk) {
      onChunk?.(event.chunk);
      return null;
    }
    if (event.type === "done") {
      return finalize(event);
    }
    return null;
  };

  while (true) {
    const { done, value } = await reader.read();
    if (value) {
      buffer += decoder.decode(value, { stream: true });
    }
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      const maybeResult = processLine(line);
      if (maybeResult) {
        return maybeResult;
      }
    }
    if (done) {
      break;
    }
  }

  if (buffer.trim()) {
    const finalResult = processLine(buffer);
    if (finalResult) {
      return finalResult;
    }
  }

  throw new Error("Knowledge stream ended unexpectedly");
};

export type UseKnowledgeQueryMutationOptions = UseMutationOptions<
  KnowledgeAnswer,
  Error,
  KnowledgeQueryVariables
>;

export function useKnowledgeQueryMutation(
  options?: UseKnowledgeQueryMutationOptions
): UseMutationResult<
  KnowledgeAnswer,
  Error,
  KnowledgeQueryVariables
> {
  return useMutation<KnowledgeAnswer, Error, KnowledgeQueryVariables>({
    mutationFn: ({ question, onChunk }) => streamKnowledge(question, onChunk),
    ...options
  });
}
