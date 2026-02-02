import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Icon from '@/components/ui/icon';
import DiagnosticHistory from '@/components/DiagnosticHistory';
import BotInfo from '@/components/BotInfo';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import { useChatLogic } from '@/hooks/useChatLogic';

const Index = () => {
  const {
    activeTab,
    setActiveTab,
    messages,
    inputValue,
    setInputValue,
    isLoading,
    messagesEndRef,
    inputRef,
    handleButtonClick,
    handleSendMessage
  } = useChatLogic();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-4xl h-[90vh] flex flex-col bg-slate-950/90 border-primary/20 overflow-hidden">
        <div className="bg-gradient-to-r from-primary to-accent p-4 flex items-center gap-3">
          <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
            <Icon name="Bot" size={28} className="text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">HEVSR Diagnostics Bot</h1>
            <p className="text-sm text-white/80">Ваш помощник для диагностики автомобилей</p>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">
          <TabsList className="bg-slate-900/50 border-b border-slate-700 rounded-none w-full justify-start px-4">
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <Icon name="MessageSquare" size={16} />
              Чат
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <Icon name="History" size={16} />
              История
            </TabsTrigger>
            <TabsTrigger value="info" className="flex items-center gap-2">
              <Icon name="Info" size={16} />
              О боте
            </TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="flex-1 flex flex-col overflow-hidden m-0">
            <div className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  isLoading={isLoading}
                  onButtonClick={handleButtonClick}
                />
              ))}
              <div ref={messagesEndRef} />
            </div>

            <ChatInput
              inputValue={inputValue}
              isLoading={isLoading}
              inputRef={inputRef}
              onInputChange={setInputValue}
              onSend={handleSendMessage}
            />
          </TabsContent>

          <TabsContent value="history" className="flex-1 overflow-y-auto m-0">
            <DiagnosticHistory />
          </TabsContent>

          <TabsContent value="info" className="flex-1 overflow-y-auto m-0">
            <BotInfo />
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  );
};

export default Index;
