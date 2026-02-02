import { Avatar } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import Icon from '@/components/ui/icon';
import { Message, checklistItems5min } from '@/hooks/useChatLogic';

type ChatMessageProps = {
  message: Message;
  isLoading: boolean;
  onButtonClick: (text: string) => void;
  checkedItems?: string[];
};

const ChatMessage = ({ message, isLoading, onButtonClick, checkedItems = [] }: ChatMessageProps) => {
  const isChecklistButton = (btn: string) => checklistItems5min.includes(btn);
  const isChecked = (btn: string) => checkedItems.includes(btn);
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
              {message.buttons.map((btn, idx) => {
                const isCheckbox = isChecklistButton(btn);
                const checked = isChecked(btn);
                
                return (
                  <Button
                    key={idx}
                    variant={checked ? "default" : "outline"}
                    size="sm"
                    onClick={() => onButtonClick(btn)}
                    disabled={isLoading && !isCheckbox}
                    className={
                      isCheckbox
                        ? checked
                          ? "bg-primary hover:bg-primary/90 text-white border-primary"
                          : "bg-slate-900/50 border-slate-600 hover:bg-slate-700 hover:border-primary text-white"
                        : "bg-slate-900/50 border-slate-600 hover:bg-slate-700 hover:border-primary text-white"
                    }
                  >
                    {isCheckbox && (
                      <Icon 
                        name={checked ? "CheckSquare" : "Square"} 
                        size={16} 
                        className="mr-2" 
                      />
                    )}
                    {btn}
                  </Button>
                );
              })}
            </div>
          )}
          
          <div className="text-xs text-slate-500 mt-2">
            {message.timestamp.toLocaleTimeString('ru-RU', { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;