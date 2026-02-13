import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import Icon from '@/components/ui/icon';
import DiagnosticHistory from '@/components/DiagnosticHistory';
import BotInfo from '@/components/BotInfo';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import ChecklistWizard from '@/components/ChecklistWizard';
import MechanicAuth from '@/components/MechanicAuth';
import DiagnosticSelector from '@/components/DiagnosticSelector';
import DiagnosticDHCH from '@/components/DiagnosticDHCH';
import DiagnosticPriemka from '@/components/DiagnosticPriemka';
import { useChatLogic } from '@/hooks/useChatLogic';
import { DiagnosticData } from '@/types/diagnostic';

const Index = () => {
  const [mechanic, setMechanic] = useState<{ id: number; name: string } | null>(null);
  const [diagnosticView, setDiagnosticView] = useState<'selector' | 'priemka' | 'dhch' | null>(null);

  useEffect(() => {
    // Проверяем сохранённые данные авторизации
    const savedId = localStorage.getItem('mechanic_id');
    const savedName = localStorage.getItem('mechanic_name');
    
    if (savedId && savedName) {
      setMechanic({ id: parseInt(savedId), name: savedName });
    }
  }, []);

  const handleAuthenticated = (mechanicData: { id: number; name: string }) => {
    setMechanic(mechanicData);
  };

  const handleLogout = () => {
    localStorage.removeItem('mechanic_id');
    localStorage.removeItem('mechanic_name');
    setMechanic(null);
  };

  const handleStartDiagnostic = () => {
    setDiagnosticView('selector');
    setActiveTab('diagnostic');
  };

  const handleDiagnosticTypeSelect = (type: 'priemka' | 'dhch' | '5min' | 'des') => {
    if (type === 'priemka') {
      setDiagnosticView('priemka');
    } else if (type === 'dhch') {
      setDiagnosticView('dhch');
    }
  };

  const handleDiagnosticComplete = async (data: DiagnosticData) => {
    console.log('Diagnostic completed:', data);
    // TODO: Сохранение в БД
    setDiagnosticView(null);
    setActiveTab('history');
  };

  const handleDiagnosticCancel = () => {
    setDiagnosticView(null);
  };

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
    handleSendMessage,
    handleCommand,
    showChecklistWizard,
    handleChecklistComplete,
    handleChecklistCancel
  } = useChatLogic(mechanic?.name);

  // Показываем форму авторизации если не авторизован
  if (!mechanic) {
    return <MechanicAuth onAuthenticated={handleAuthenticated} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-4xl h-[90vh] flex flex-col bg-slate-950/90 border-primary/20 overflow-hidden">
        <div className="bg-gradient-to-r from-primary to-accent p-4 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
              <Icon name="Bot" size={28} className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">HEVSR Diagnostics Bot</h1>
              <p className="text-sm text-white/80">Механик: {mechanic.name}</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="text-white hover:bg-white/10"
          >
            <Icon name="LogOut" size={18} className="mr-2" />
            Выйти
          </Button>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
          <TabsList className="bg-slate-900/50 border-b border-slate-700 rounded-none w-full justify-start px-4 shrink-0">
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <Icon name="MessageSquare" size={16} />
              Чат
            </TabsTrigger>
            <TabsTrigger value="diagnostic" className="flex items-center gap-2">
              <Icon name="Wrench" size={16} />
              Диагностика
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

          <TabsContent value="chat" className="flex-1 flex flex-col m-0 data-[state=active]:flex data-[state=inactive]:hidden overflow-hidden">
            {showChecklistWizard ? (
              <div className="flex-1 overflow-y-auto p-4">
                <ChecklistWizard
                  onComplete={handleChecklistComplete}
                  onCancel={handleChecklistCancel}
                />
              </div>
            ) : (
              <>
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
                  onCommand={handleCommand}
                />
              </>
            )}
          </TabsContent>

          <TabsContent value="diagnostic" className="flex-1 p-4 m-0 data-[state=active]:flex data-[state=inactive]:hidden overflow-y-auto">
            {diagnosticView === null && (
              <div className="flex items-center justify-center h-full">
                <Button onClick={handleStartDiagnostic} size="lg" className="flex items-center gap-2">
                  <Icon name="Play" size={20} />
                  Начать новую диагностику
                </Button>
              </div>
            )}
            {diagnosticView === 'selector' && (
              <DiagnosticSelector
                onSelectType={handleDiagnosticTypeSelect}
                onCancel={handleDiagnosticCancel}
              />
            )}
            {diagnosticView === 'priemka' && (
              <DiagnosticPriemka
                onComplete={handleDiagnosticComplete}
                onCancel={handleDiagnosticCancel}
              />
            )}
            {diagnosticView === 'dhch' && (
              <DiagnosticDHCH
                onComplete={handleDiagnosticComplete}
                onCancel={handleDiagnosticCancel}
              />
            )}
          </TabsContent>

          <TabsContent value="history" className="flex-1 m-0 p-0 data-[state=active]:block data-[state=inactive]:hidden overflow-y-auto">
            <DiagnosticHistory />
          </TabsContent>

          <TabsContent value="info" className="flex-1 m-0 p-0 data-[state=active]:block data-[state=inactive]:hidden overflow-y-auto">
            <BotInfo />
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  );
};

export default Index;