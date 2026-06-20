import { localJsonRequest } from "./localRequests";

export type WorkLaneName = "inbox" | "planned" | "active" | "review" | "done";
export type WorkLaneCardStatus = "open" | "in-progress" | "blocked" | "done";

export type LocalWorkLaneCard = {
  id: string;
  lane: WorkLaneName;
  title: string;
  body: string;
  status: WorkLaneCardStatus;
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
  status: WorkLaneCardStatus
): Promise<LocalWorkLaneCard> {
  return localJsonRequest<LocalWorkLaneCard>("/local/work-lane-cards", {
    method: "POST",
    body: JSON.stringify({ lane, title, body, status })
  });
}

export async function updateLocalWorkLaneCard(
  cardId: string,
  updates: Partial<Pick<LocalWorkLaneCard, "lane" | "title" | "body" | "status">>
): Promise<LocalWorkLaneCard> {
  return localJsonRequest<LocalWorkLaneCard>(`/local/work-lane-cards/${cardId}`, {
    method: "PATCH",
    body: JSON.stringify(updates)
  });
}

export async function deleteLocalWorkLaneCard(cardId: string): Promise<void> {
  await localJsonRequest<void>(`/local/work-lane-cards/${cardId}`, { method: "DELETE" });
}
