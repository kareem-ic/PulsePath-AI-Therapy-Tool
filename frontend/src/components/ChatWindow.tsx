import { useState } from 'react';
import type { Message } from '@/types';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import MessageBubble from './MessageBubble';
import MicButton from './MicButton';
import { v4 as uuid } from 'uuid';
import { ask } from '@/lib/api';          
import { cn } from '@/lib/utils';

export default function ChatWindow() {
  const [text, setText] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: uuid(),
      role: 'ai',
      text: "Hi, I'm PulsePath. How are you feeling today?",
    },
  ]);
  const [loading, setLoading] = useState(false);  

  async function send() {
    if (!text.trim() || loading) return;

    const userMsg: Message = { id: uuid(), role: 'user', text };
    setMessages((m) => [...m, userMsg]);
    setText('');
    setLoading(true);                              

    try {
      const { mood, reply } = await ask(userMsg.text);   
      const aiMsg: Message = {
        id: uuid(),
        role: 'ai',
        text: reply,
        mood,
      };
      setMessages((m) => [...m, aiMsg]);
    } catch (err) {
      console.error(err);
      setMessages((m) => [
        ...m,
        {
          id: uuid(),
          role: 'ai',
          text: 'Sorry, something went wrong. Please try again.',
        },
      ]);
    } finally {
      setLoading(false);                           
    }
  }

  return (
    <div className="mx-auto flex h-[90vh] max-w-lg flex-col gap-4">
      {/* scrollable message list */}
      <div className="flex-1 space-y-3 overflow-y-auto px-2">
        {messages.map((m) => (
          <MessageBubble key={m.id} msg={m} />
        ))}

        {/* tiny loader bubble */}
        {loading && (
          <div className="flex">
            <div className={cn(
              'animate-pulse rounded-2xl bg-white px-3 py-2 text-sm text-zinc-500 shadow',
            )}>
              …
            </div>
          </div>
        )}
      </div>

      {/* composer */}
      <div className="flex items-center gap-2">
        <Input
          placeholder="Type a message"
          value={text}
          disabled={loading}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) =>
            e.key === 'Enter' && !e.nativeEvent.isComposing && send()
          }
        />
        <Button onClick={send} disabled={loading}>
          Send
        </Button>
        <MicButton
          onClick={() => alert('mic coming soon')}
          disabled={loading}
        />
      </div>
    </div>
  );
}
