import type { Mood } from '../types';

const API_BASE = '/api';      
async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

export async function ask(text: string): Promise<{ mood: Mood; reply: string }> {
  const res = await fetch(`${API_BASE}/reply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  return json(res);
}

export async function transcribe(wav: Blob): Promise<string> {
  const res = await fetch(`${API_BASE}/transcribe`, {
    method: 'POST',
    headers: { 'Content-Type': 'audio/wav' },
    body: wav,
  });
  const data = await json<{ text: string }>(res);
  return data.text;
}

export async function speak(text: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}/speak`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.blob();           
}