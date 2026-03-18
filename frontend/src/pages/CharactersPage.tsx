import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, 
  Plus, 
  Search, 
  Sparkles, 
  Wand2, 
  MoreVertical,
  Star,
  MessageSquare
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

// Varsayılan mock veriler
const SAMPLE_CHARACTERS = [
  { id: 1, name: 'Lumi', role: 'Cesur Ateşböceği', element: 'Işık', src: 'https://images.unsplash.com/photo-1518780664697-55e3ad937233?auto=format&fit=crop&q=80&w=200&h=200', isFavorite: true },
  { id: 2, name: 'Bramble', role: 'Bilge Ayı', element: 'Toprak', src: 'https://images.unsplash.com/photo-1548243604-89849ef954ad?auto=format&fit=crop&q=80&w=200&h=200', isFavorite: true },
  { id: 3, name: 'Marina', role: 'Denizkızı Prenses', element: 'Su', src: 'https://images.unsplash.com/photo-1519800642193-a5501fb7e034?auto=format&fit=crop&q=80&w=200&h=200', isFavorite: false },
  { id: 4, name: 'Elara', role: 'Rüzgar Perisi', element: 'Hava', src: 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&q=80&w=200&h=200', isFavorite: false },
  { id: 5, name: 'Korg', role: 'Taş Golem', element: 'Maden', src: 'https://images.unsplash.com/photo-1620502120379-34b868bb213c?auto=format&fit=crop&q=80&w=200&h=200', isFavorite: false },
];

export const CharactersPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const filteredCharacters = SAMPLE_CHARACTERS.filter(char => 
    char.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    char.role.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      
      {/* Header & Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-magical-violet to-magical-indigo bg-clip-text text-transparent flex items-center">
            <Users className="w-8 h-8 mr-3 text-magical-violet" />
            Karakter Koleksiyonu
          </h1>
          <p className="text-slate-400 mt-1">
            Kendi yarattığınız karakterler burada yaşar ve yeni hikayelere katılmayı bekler.
          </p>
        </div>
        
        <Button className="rounded-xl px-6 h-12 bg-gradient-to-r from-magical-violet to-magical-indigo hover:opacity-90 transition-opacity shadow-[0_0_20px_rgba(167,139,250,0.3)]">
          <Plus className="w-5 h-5 mr-2" />
          Yeni Karakter Yarat
        </Button>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-4 bg-white/5 p-4 rounded-2xl border border-white/10 backdrop-blur-sm">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <Input 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Karakterlerde ara..." 
            className="pl-10 h-12 bg-white/5 border-white/10 focus:border-magical-violet rounded-xl text-white w-full"
          />
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="h-12 border-white/10 hover:bg-white/10 rounded-xl px-6 text-slate-300">
            Tümü
          </Button>
          <Button variant="outline" className="h-12 border-white/10 hover:bg-white/10 rounded-xl px-6 text-slate-300">
            Favoriler
          </Button>
        </div>
      </div>

      {/* Empty State vs Grid */}
      {filteredCharacters.length === 0 ? (
        <div className="py-20 text-center flex flex-col items-center justify-center bg-white/5 rounded-3xl border border-white/10 border-dashed">
          <div className="w-20 h-20 bg-magical-indigo/10 rounded-full flex items-center justify-center mb-6">
            <Wand2 className="w-10 h-10 text-magical-indigo opacity-50" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">Karakter Bulunamadı</h3>
          <p className="text-slate-400 max-w-md">
            Aradığınız isme sahip bir karakter bulamadık. Hayal gücünüzü kullanarak onu hemen şimdi yaratabilirsiniz!
          </p>
          <Button className="mt-6 rounded-xl bg-white/10 hover:bg-white/20 text-white">
            <Sparkles className="w-4 h-4 mr-2" />
            Sihirli Arama Yap
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          {/* Create New Card */}
          <div className="group cursor-pointer bg-white/5 hover:bg-magical-violet/10 border border-white/10 hover:border-magical-violet/50 border-dashed rounded-3xl p-6 flex flex-col items-center justify-center text-center transition-all duration-300 min-h-[280px]">
            <div className="w-16 h-16 rounded-full bg-magical-violet/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-[0_0_15px_rgba(167,139,250,0.3)]">
              <Plus className="w-8 h-8 text-magical-violet" />
            </div>
            <h3 className="font-bold text-lg text-white mb-1">Yeni Karakter</h3>
            <p className="text-sm text-slate-400">Yapay zeka ile saniyeler içinde tasarlayın.</p>
          </div>

          {/* Character Cards */}
          {filteredCharacters.map((char) => (
            <div key={char.id} className="group relative bg-[#0b0816] border border-white/10 rounded-3xl overflow-hidden hover:border-white/20 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
              <div className="absolute top-3 right-3 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button variant="ghost" size="icon" className="h-8 w-8 bg-black/50 hover:bg-black/70 rounded-full backdrop-blur-sm border border-white/10 text-white">
                  <MoreVertical className="w-4 h-4" />
                </Button>
              </div>
              <div className="absolute top-3 left-3 z-10">
                {char.isFavorite && (
                  <div className="bg-amber-400/20 text-amber-400 p-1.5 rounded-full backdrop-blur-sm border border-amber-400/30">
                    <Star className="w-4 h-4 fill-amber-400" />
                  </div>
                )}
              </div>
              
              <div className="aspect-square w-full overflow-hidden relative">
                <div className="absolute inset-0 bg-gradient-to-t from-[#0b0816] via-transparent to-transparent z-10" />
                <img 
                  src={char.src} 
                  alt={char.name} 
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
              </div>
              
              <div className="p-5 pt-2 relative z-20">
                <div className="inline-block px-2 py-1 bg-white/5 border border-white/10 rounded-md text-xs font-medium text-slate-300 mb-3">
                  {char.element}
                </div>
                <h3 className="font-bold text-lg text-white truncate" title={char.name}>
                  {char.name}
                </h3>
                <p className="text-sm text-slate-400 truncate mb-4" title={char.role}>
                  {char.role}
                </p>
                <Button 
                  className="w-full bg-magical-violet/10 text-magical-violet hover:bg-magical-violet hover:text-white border-none transition-colors"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/chat/${char.id}`);
                  }}
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Sohbet Et
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
