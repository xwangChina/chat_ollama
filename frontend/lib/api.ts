export interface ChatCompletionRequest {
  message: string;
  fileIds?: string[];
}

export interface ChatCompletionResponse {
  id?: string;
  content?: string;
  createdAt?: string;
}

export interface ChatMessage {
  id: string;
  author: "user" | "assistant" | "system";
  content: string;
  createdAt: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function postChatCompletion(
  chatId: string,
  payload: ChatCompletionRequest
): Promise<ChatCompletionResponse> {
  const response = await fetch(`${API_BASE}/chat/${chatId}/respond`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Backend returned ${response.status}`);
  }

  return response.json();
}

export async function uploadFiles(chatId: string, files: File[]): Promise<string[]> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await fetch(`${API_BASE}/chat/${chatId}/files`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    throw new Error(`File upload failed with status ${response.status}`);
  }

  const { fileIds } = await response.json();
  return fileIds;
}

export async function fetchChatMessages(chatId: string): Promise<ChatMessage[]> {
  const response = await fetch(`${API_BASE}/chat/${chatId}/messages`);
  if (!response.ok) {
    throw new Error(`Failed to load chat history: ${response.status}`);
  }

  const data = await response.json();
  return data.messages ?? [];
}
