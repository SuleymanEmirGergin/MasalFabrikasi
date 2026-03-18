import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Send, ArrowLeft, Mic, Sparkles, Image as ImageIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useCharacterChat } from '@/api/hooks';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'character';
  timestamp: Date;
}

const CHARACTERS: Record<string, { name: string; avatar: string; color: string; greeting: string; responses: string[] }> = {
  'owl': {
    name: 'Bilge Baykuş',
    avatar: '🦉',
    color: 'from-amber-400 to-orange-500',
    greeting: 'Merhaba genç kaşif! Ormanda kaybolduysan sana yol gösterebilirim. Ne bilmek istersin?',
    responses: [
      'Hoo hoo! Çok ilginç bir soru.',
      'Ormanın sınırlarında sihirli çiçekler açar. Gördün mü onları?',
      'Akşam karanlığı çöktüğünde yıldızları izlemeyi çok severim.',
      'Bunu daha önce hiç düşünmemiştim... Senin fikrin harika!',
      'Kanatlarım biraz yoruldu ama seninle konuşmak çok keyifli.'
    ]
  },
  'knight': {
    name: 'Cesur Şövalye',
    avatar: '🛡️',
    color: 'from-blue-400 to-indigo-500',
    greeting: 'Selamlar! Ben Krallığın en cesur savaşçısıyım! Birlikte hangi efsanevi yaratıkla savaşacağız?',
    responses: [
      'Kılıcım her zaman adaleti savunur!',
      'Gümüş zırhımı parlatmam gerekiyor ammma seninle sohbet etmek daha önemli.',
      'Ejderhalar göründüğü kadar korkutucu değildir, sadece anlaşılmak isterler.',
      'Çok iyi bir nokta! Beraber çok iyi bir takım olabiliriz.',
      'Korku nedir bilmem! Sen de benim gibi cesur musun?'
    ]
  },
  'default': {
    name: 'Gizemli Arkadaş',
    avatar: '✨',
    color: 'from-purple-400 to-pink-500',
    greeting: 'Merhaba! Seninle konuştuğuma çok sevindim.',
    responses: [
      'Ne kadar güzel bir düşünce!',
      'Biraz daha anlatır mısın?',
      'Birlikte harika hikayeler oluşturabiliriz.',
      'Sihir her yerdedir, yeter ki bakmasını bil!'
    ]
  }
};

export const CharacterChatPage = () => {
  const { characterId } = useParams<{ characterId: string }>();
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const character = CHARACTERS[characterId || ''] || CHARACTERS['default'];

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'msg-0',
      text: character.greeting,
      sender: 'character',
      timestamp: new Date()
    }
  ]);
  const [history, setHistory] = useState<{ role: string; content: string }[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const { loading: isTyping, error: apiError, sendMessage } = useCharacterChat();

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isTyping) return;

    const userText = inputMessage.trim();
    const newUserMsg: Message = {
      id: `msg-${Date.now()}`,
      text: userText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newUserMsg]);
    setInputMessage('');

    // Call API
    const responseText = await sendMessage(
      characterId || 'owl', 
      userText, 
      history
    );

    if (responseText) {
      const newCharMsg: Message = {
        id: `msg-${Date.now() + 1}`,
        text: responseText,
        sender: 'character',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, newCharMsg]);
      
      // Update history for next turns
      setHistory(prev => [
        ...prev,
        { role: 'user', content: userText },
        { role: 'assistant', content: responseText }
      ]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-3xl mx-auto rounded-3xl overflow-hidden shadow-2xl border border-white/10 bg-[#0f1115]">
      {/* Chat Header */}
      <div className={`p-4 sm:p-6 bg-gradient-to-r ${character.color} flex items-center justify-between shadow-md z-10 relative`}>
        <div className="flex items-center gap-4">
          <Button 
            variant="ghost" 
            size="icon" 
            className="text-white hover:bg-white/20 rounded-full"
            onClick={() => navigate('/characters')}
          >
            <ArrowLeft className="w-6 h-6" />
          </Button>
          
          <div className="relative">
            <div className="w-14 h-14 bg-white/20 rounded-full flex items-center justify-center text-3xl shadow-inner border border-white/20 backdrop-blur-sm">
              {character.avatar}
            </div>
            <div className="absolute bottom-0 right-0 w-4 h-4 rounded-full bg-green-400 border-2 border-[#1a1b26] shadow-sm"></div>
          </div>
          
          <div>
            <h2 className="text-xl sm:text-2xl font-black text-white drop-shadow-sm">{character.name}</h2>
            <p className="text-white/80 text-sm font-medium flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
              Çevrimiçi
            </p>
          </div>
        </div>
        
        <div className="hidden sm:flex items-center gap-2">
          <Button variant="ghost" size="icon" className="text-white hover:bg-white/20 rounded-full">
            <Sparkles className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 scroll-smooth bg-gradient-to-b from-[#15171e] to-[#0f1115]">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          return (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.3 }}
              className={`flex ${isUser ? 'justify-end' : 'justify-start'} w-full`}
            >
              <div 
                className={`flex gap-3 max-w-[85%] sm:max-w-[75%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
              >
                {!isUser && (
                  <div className="w-10 h-10 shrink-0 bg-white/10 rounded-full flex items-center justify-center text-xl shadow-sm border border-white/5 mt-auto">
                    {character.avatar}
                  </div>
                )}
                
                <div 
                  className={`
                    px-5 py-4 rounded-3xl shadow-md text-[17px] leading-relaxed relative
                    ${isUser 
                      ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-br-sm' 
                      : 'bg-[#1e212b] text-slate-100 border border-white/5 rounded-bl-sm'}
                  `}
                >
                  {msg.text}
                  <div className={`text-[11px] mt-2 opacity-50 flex items-center gap-1 ${isUser ? 'justify-end text-indigo-100' : 'justify-start text-slate-400'}`}>
                    {msg.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}

        {/* Typing Indicator */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start w-full"
          >
            <div className="flex gap-3 max-w-[75%] flex-row">
              <div className="w-10 h-10 shrink-0 bg-white/10 rounded-full flex items-center justify-center text-xl shadow-sm border border-white/5 mt-auto">
                {character.avatar}
              </div>
              <div className="px-5 py-4 rounded-3xl bg-[#1e212b] border border-white/5 rounded-bl-sm flex items-center gap-2">
                <span className="w-2.5 h-2.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span className="w-2.5 h-2.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-2.5 h-2.5 bg-slate-400 rounded-full animate-bounce"></span>
              </div>
            </div>
          </motion.div>
        )}
        
        {apiError && (
          <div className="mx-6 mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs text-center">
            {apiError}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 sm:p-5 bg-[#171921] border-t border-white/5 flex gap-3 sm:gap-4 items-end">
        <Button variant="ghost" size="icon" className="shrink-0 rounded-full text-slate-400 hover:text-white hover:bg-white/10 h-12 w-12 hidden sm:flex">
          <ImageIcon className="w-6 h-6" />
        </Button>
        <div className="flex-1 relative">
          <Input
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder={`${character.name} sana mesaj yazmanı bekliyor...`}
            className="w-full bg-[#0a0c10] border-white/10 rounded-2xl pl-5 pr-12 py-6 text-[16px] text-white shadow-inner focus-visible:ring-indigo-500 placeholder:text-slate-500"
          />
          <Button 
            variant="ghost" 
            size="icon" 
            className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-indigo-400 hover:bg-transparent"
          >
            <Mic className="w-5 h-5" />
          </Button>
        </div>
        <Button 
          onClick={handleSendMessage}
          disabled={!inputMessage.trim() || isTyping}
          className="shrink-0 h-14 w-14 rounded-2xl bg-gradient-to-r from-indigo-500 to-purple-500 hover:opacity-90 transition-opacity disabled:opacity-50 shadow-lg shadow-indigo-500/20"
        >
          <Send className="w-6 h-6 text-white" />
        </Button>
      </div>
    </div>
  );
};
