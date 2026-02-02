import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import Icon from '@/components/ui/icon';

type ChatInputProps = {
  inputValue: string;
  isLoading: boolean;
  inputRef: React.RefObject<HTMLInputElement>;
  onInputChange: (value: string) => void;
  onSend: () => void;
};

const ChatInput = ({ inputValue, isLoading, inputRef, onInputChange, onSend }: ChatInputProps) => {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="border-t border-slate-700 bg-slate-900/50 p-4">
      <div className="flex gap-2">
        <Input
          ref={inputRef}
          placeholder="Введите сообщение..."
          value={inputValue}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={isLoading}
          className="flex-1 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-500"
        />
        <Button
          onClick={onSend}
          disabled={isLoading || !inputValue.trim()}
          className="px-6"
        >
          {isLoading ? (
            <Icon name="Loader2" size={20} className="animate-spin" />
          ) : (
            <Icon name="Send" size={20} />
          )}
        </Button>
      </div>
    </div>
  );
};

export default ChatInput;
