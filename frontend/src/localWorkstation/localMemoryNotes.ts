import { localJsonRequest } from "./localRequests";

export type LocalMemoryNote = {
  id: string;
  title: string;
  body: string;
  source: string;
  created_at: string;
  updated_at: string;
};

export async function listLocalMemoryNotes(): Promise<LocalMemoryNote[]> {
  const payload = await localJsonRequest<{ notes: LocalMemoryNote[] }>("/local/memory-notes");
  return payload.notes;
}

export async function createLocalMemoryNote(title: string, body: string, source = "operator"): Promise<LocalMemoryNote> {
  return localJsonRequest<LocalMemoryNote>("/local/memory-notes", {
    method: "POST",
    body: JSON.stringify({ title, body, source })
  });
}

export async function updateLocalMemoryNote(
  noteId: string,
  updates: Partial<Pick<LocalMemoryNote, "title" | "body" | "source">>
): Promise<LocalMemoryNote> {
  return localJsonRequest<LocalMemoryNote>(`/local/memory-notes/${noteId}`, {
    method: "PATCH",
    body: JSON.stringify(updates)
  });
}

export async function deleteLocalMemoryNote(noteId: string): Promise<void> {
  await localJsonRequest<void>(`/local/memory-notes/${noteId}`, { method: "DELETE" });
}
