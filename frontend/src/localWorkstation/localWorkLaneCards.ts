import { localJsonRequest } from "./localRequests";

export type WorkLaneName = "inbox" | "planned" | "active" | "review" | "done";
export type WorkLaneCardStatus = "open" | "in-progress" | "blocked" | "done";

export type LocalWorkLaneCard = {
  id: string;
  lane: WorkLaneName;
  title: string;
  body: string;
  status: WorkLaneCardStatus;
  chat_session_id: string | null;
  linked_chat_session_title: string | null;
  created_at: string;
  updated_at: string;
};

export const workLaneNames: WorkLaneName[] = ["inbox", "planned", "active", "review", "done"];
export const workLaneCardStatuses: WorkLaneCardStatus[] = ["open", "in-progress", "blocked", "done"];

export async function listLocalWorkLaneCards(): Promise<LocalWorkLaneCard[]> {
  const payload = await localJsonRequest<{ cards: LocalWorkLaneCard[] }>("/local/work-lane-cards");
  return payload.cards;
}

export async function createLocalWorkLaneCard(
  lane: WorkLaneName,
  title: string,
  body: string,
  status: WorkLaneCardStatus,
  chatSessionId?: string
): Promise<LocalWorkLaneCard> {
  return localJsonRequest<LocalWorkLaneCard>("/local/work-lane-cards", {
    method: "POST",
    body: JSON.stringify({ lane, title, body, status, chat_session_id: chatSessionId || undefined })
  });
}

export async function updateLocalWorkLaneCard(
  cardId: string,
  updates: Partial<Pick<LocalWorkLaneCard, "lane" | "title" | "body" | "status" | "chat_session_id">>
): Promise<LocalWorkLaneCard> {
  return localJsonRequest<LocalWorkLaneCard>(`/local/work-lane-cards/${cardId}`, {
    method: "PATCH",
    body: JSON.stringify(updates)
  });
}

export async function deleteLocalWorkLaneCard(cardId: string): Promise<void> {
  await localJsonRequest<void>(`/local/work-lane-cards/${cardId}`, { method: "DELETE" });
}
