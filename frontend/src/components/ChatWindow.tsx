import { useState } from 'react';
import type { Message } from '@/types';
import MessageBubble from './MessageBubble';
import MicButton from './MicButton';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { v4 as uuid } from 'uuid';

export default function ChatWindow() {
  const [text, setText] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: uuid(),
      role: 'ai',
      text: "Hi, I'm PulsePath. How are you feeling today?",
    },
  ]);

  const send = () => {
    if (!text.trim()) return;
    setMessages((m) => [
      ...m,
      { id: uuid(), role: 'user', text },
    ]);
    setText('');
  };

  return (
    <div className="mx-auto flex h-[90vh] max-w-lg flex-col gap-4">
      {/* scrollable message list */}
      <div className="flex-1 space-y-3 overflow-y-auto px-2">
        {messages.map((m) => (
          <MessageBubble key={m.id} msg={m} />
        ))}
      </div>

      {/* composer */}
      <div className="flex items-center gap-2">
        <Input
          placeholder="Type a message"
          value={text}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setText(e.target.value)}
          onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && send()}
          />
        <Button onClick={send}>Send</Button>
        <MicButton onClick={() => alert('mic coming soon')} />
      </div>
    </div>
  );
}
