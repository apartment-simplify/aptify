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

const queryKnowledge = async (question: string) => {
  const response = await fetch("http://localhost:8000/knowledge/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      question
    })
  });

  if (!response.ok) {
    throw new Error("Failed to fetch knowledge answer");
  }

  return response.json() as Promise<KnowledgeAnswer>;
};

export function useKnowledgeQueryMutation(
  options?: UseMutationOptions<KnowledgeAnswer, Error, string>
): UseMutationResult<KnowledgeAnswer, Error, string> {
  return useMutation<KnowledgeAnswer, Error, string>({
    mutationFn: queryKnowledge,
    ...options
  });
}
