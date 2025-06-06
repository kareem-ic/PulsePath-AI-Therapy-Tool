import type { Message } from '@/types';
import { cn } from '@/lib/utils';  // if you don’t have a classNames helper, create a tiny one

interface Props {
  msg: Message;
}

export default function MessageBubble({ msg }: Props) {
  const isUser = msg.role === 'user';

  return (
    <div
      className={cn(
        'flex w-full',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      <div
        className={cn(
          'max-w-[75%] rounded-2xl px-4 py-2 shadow',
          isUser
            ? 'bg-brand text-white rounded-br-sm'
            : 'bg-white text-zinc-800 rounded-bl-sm'
        )}
      >
        {msg.text}
      </div>
    </div>
  );
}
