export type Mood   = 'positive' | 'neutral' | 'negative';
export type Role   = 'user' | 'ai';

export interface Message {
  id: string;          // uuid or nano-id
  role: Role;
  text: string;
  mood?: Mood;         // present only on AI messages
  audioUrl?: string;   // filled after /speak fetch
}