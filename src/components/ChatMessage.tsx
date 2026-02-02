import { Avatar } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Message } from '@/hooks/useChatLogic';

type ChatMessageProps = {
  message: Message;
  isLoading: boolean;
  onButtonClick: (text: string) => void;
};

const ChatMessage = ({ message, isLoading, onButtonClick }: ChatMessageProps) => {
  return (
    <div className={`flex gap-3 ${message.type === 'user' ? 'flex-row-reverse' : ''}`}>
      <Avatar className={`w-10 h-10 flex-shrink-0 ${
        message.type === 'bot' 
          ? 'bg-gradient-to-br from-primary to-accent' 
          : 'bg-slate-700'
      }`}>
        <div className="w-full h-full flex items-center justify-center text-white">
          {message.type === 'bot' ? '🤖' : '👤'}
        </div>
      </Avatar>
      
      <div className={`flex-1 ${message.type === 'user' ? 'flex justify-end' : ''}`}>
        <div className={`rounded-2xl px-4 py-3 max-w-[85%] ${
          message.type === 'bot'
            ? 'bg-slate-800/50 text-slate-100'
            : 'bg-gradient-to-br from-primary to-accent text-white'
        }`}>
          <div className="whitespace-pre-wrap break-words">{message.text}</div>
          
          {message.buttons && message.buttons.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {message.buttons.map((btn, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  size="sm"
                  onClick={() => onButtonClick(btn)}
                  disabled={isLoading}
                  className="bg-slate-900/50 border-slate-600 hover:bg-slate-700 hover:border-primary text-white"
                >
                  {btn}
                </Button>
              ))}
            </div>
          )}
          
          <div className="text-xs text-slate-500 mt-2">
            {message.timestamp.toLocaleTimeString('ru-RU', { 
              hour: '2-digit', 
              minute: '2-digit',
              timeZone: 'Asia/Krasnoyarsk'
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;