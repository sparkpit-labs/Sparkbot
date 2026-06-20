import { localJsonRequest } from "./localRequests";

export type LocalChatMessage = {
  id: string;
  session_id: string;
  role: "operator" | "note";
  content: string;
  created_at: string;
};

export type LocalChatSessionSummary = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
};

export type LocalChatSession = Omit<LocalChatSessionSummary, "message_count"> & {
  messages: LocalChatMessage[];
};

export async function listLocalChatSessions(): Promise<LocalChatSessionSummary[]> {
  const payload = await localJsonRequest<{ sessions: LocalChatSessionSummary[] }>("/local/chat/sessions");
  return payload.sessions;
}

export async function createLocalChatSession(title: string): Promise<LocalChatSession> {
  return localJsonRequest<LocalChatSession>("/local/chat/sessions", {
    method: "POST",
    body: JSON.stringify({ title })
  });
}

export async function getLocalChatSession(sessionId: string): Promise<LocalChatSession> {
  return localJsonRequest<LocalChatSession>(`/local/chat/sessions/${sessionId}`);
}

export async function updateLocalChatSession(sessionId: string, title: string): Promise<LocalChatSession> {
  return localJsonRequest<LocalChatSession>(`/local/chat/sessions/${sessionId}`, {
    method: "PATCH",
    body: JSON.stringify({ title })
  });
}

export async function deleteLocalChatSession(sessionId: string): Promise<void> {
  await localJsonRequest<void>(`/local/chat/sessions/${sessionId}`, { method: "DELETE" });
}

export async function addLocalChatMessage(
  sessionId: string,
  role: LocalChatMessage["role"],
  content: string
): Promise<LocalChatMessage> {
  return localJsonRequest<LocalChatMessage>(`/local/chat/sessions/${sessionId}/messages`, {
    method: "POST",
    body: JSON.stringify({ role, content })
  });
}
