import { Mic } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Props {
  onClick: () => void;
  disabled?: boolean;
}

export default function MicButton({ onClick, disabled }: Props) {
  return (
    <Button
      size="icon"
      variant="secondary"
      disabled={disabled}
      onClick={onClick}
      className="rounded-full"
    >
      <Mic className="h-5 w-5" />
    </Button>
  );
}
