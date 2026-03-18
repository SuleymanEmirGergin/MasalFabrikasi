
import { motion } from 'framer-motion';
import { Trophy, Medal, Star, Target, Users, Search, Plus, ThumbsUp, Flame, Crown } from 'lucide-react';
import { Button } from '@/components/ui/button';

// Mock Data
const LEADERBOARD_DATA = [
  { id: 1, name: 'Zeynep Yıldız', points: 1250, avatar: '👧', title: 'Hikaye Ustası', color: 'from-yellow-400 to-amber-500', icon: <Crown className="w-5 h-5 text-yellow-100" /> },
  { id: 2, name: 'Ali Kahraman', points: 980, avatar: '👦', title: 'Uzay Kaşifi', color: 'from-slate-300 to-slate-400', icon: <Medal className="w-5 h-5 text-slate-100" /> },
  { id: 3, name: 'Ayşe Peri', points: 840, avatar: '🧚‍♀️', title: 'Büyülü Yazar', color: 'from-orange-400 to-red-400', icon: <Medal className="w-5 h-5 text-orange-100" /> },
  { id: 4, name: 'Can Robot', points: 720, avatar: '🤖', title: 'Geleceğin Sesi', color: 'from-indigo-400 to-blue-500' },
  { id: 5, name: 'Ece Rüzgar', points: 650, avatar: '🌪️', title: 'Hızlı Okuyucu', color: 'from-emerald-400 to-teal-500' },
];

const CHALLENGES_DATA = [
  { id: 1, title: 'Haftalık Yazar', description: 'Bu hafta 3 yeni hikaye oluştur.', progress: 2, total: 3, reward: 150, color: 'from-violet-500 to-fuchsia-500' },
  { id: 2, title: 'Seslendirmen', description: 'Kendi sesinle 1 masal oku.', progress: 0, total: 1, reward: 200, color: 'from-blue-500 to-cyan-500' },
  { id: 3, title: 'Kitap Kurdu', description: 'Günde 15 dakika interaktif hikaye oku.', progress: 10, total: 15, reward: 50, color: 'from-rose-500 to-pink-500' },
];

const FRIENDS_ACTIVITY = [
  { id: 1, name: 'Elif', avatar: '👱‍♀️', action: 'yeni bir peri masalı oluşturdu!', time: '10 dk önce', likes: 2 },
  { id: 2, name: 'Burak', avatar: '🐱', action: '3 günlük okuma serisine ulaştı.', time: '1 saat önce', likes: 5 },
  { id: 3, name: 'Ceren', avatar: '🌸', action: 'Bilge Baykuş karakteri ile sohbet etti.', time: '2 saat önce', likes: 1 },
];

export const SocialPage = () => {

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-10">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-black bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent flex items-center gap-3 drop-shadow-sm">
            <Trophy className="w-10 h-10 text-amber-500" />
            Sosyal Maceralar
          </h1>
          <p className="text-slate-400 mt-2 font-medium">Arkadaşlarınla yarış, görevleri tamamla ve ödülleri topla!</p>
        </div>
        
        <div className="flex bg-[#1a1c23] border border-white/10 rounded-2xl p-4 gap-6 items-center shadow-lg">
          <div className="flex flex-col items-center">
            <div className="flex items-center gap-1.5 text-amber-400 font-bold mb-1"><Flame className="w-5 h-5 fill-current" /> Seri</div>
            <div className="text-2xl font-black text-white">4 Gün</div>
          </div>
          <div className="w-px h-10 bg-white/10" />
          <div className="flex flex-col items-center">
            <div className="flex items-center gap-1.5 text-indigo-400 font-bold mb-1"><Star className="w-5 h-5 fill-current" /> Puan</div>
            <div className="text-2xl font-black text-white">1,450</div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        
        {/* Left Column: Leaderboard */}
        <div className="bg-[#15171e] border border-white/5 rounded-3xl p-6 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-amber-400 to-orange-500" />
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2 text-white">
              <Medal className="w-6 h-6 text-amber-500" /> Haftanın Liderleri
            </h2>
          </div>
          
          <div className="space-y-3">
            {LEADERBOARD_DATA.map((user, idx) => (
              <motion.div
                key={user.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className={`flex items-center gap-4 p-3 rounded-2xl ${idx < 3 ? 'bg-white/5 border border-white/5' : 'hover:bg-white/5'} transition-colors relative overflow-hidden`}
              >
                {idx < 3 && (
                  <div className={`absolute top-0 right-0 w-2 h-full bg-gradient-to-b ${user.color}`} />
                )}
                
                <div className={`w-8 font-black text-lg ${idx === 0 ? 'text-amber-400' : idx === 1 ? 'text-slate-300' : idx === 2 ? 'text-orange-400' : 'text-slate-500'}`}>
                  {idx + 1}.
                </div>
                
                <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl shadow-inner ${idx < 3 ? `bg-gradient-to-br ${user.color}` : 'bg-[#1e212b]'}`}>
                  {idx < 3 && user.icon ? user.icon : user.avatar}
                </div>
                
                <div className="flex-1">
                  <div className="font-bold text-slate-100">{user.name}</div>
                  <div className="text-xs text-slate-400 font-medium">{user.title}</div>
                </div>
                
                <div className="font-black text-indigo-400">{user.points}</div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Middle Column: Challenges */}
        <div className="bg-[#15171e] border border-white/5 rounded-3xl p-6 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-violet-400 to-fuchsia-500" />
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2 text-white">
              <Target className="w-6 h-6 text-fuchsia-500" /> Meydan Okumalar
            </h2>
          </div>
          
          <div className="space-y-4">
            {CHALLENGES_DATA.map((challenge, idx) => {
              const percent = Math.round((challenge.progress / challenge.total) * 100);
              return (
                <motion.div
                  key={challenge.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="bg-[#1a1c23] border border-white/5 rounded-2xl p-4 relative overflow-hidden group hover:border-white/10 transition-colors"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-white text-lg">{challenge.title}</h3>
                    <div className="flex items-center gap-1 text-sm font-bold text-amber-400 bg-amber-400/10 px-2 py-1 rounded-lg">
                      <Star className="w-3.5 h-3.5 fill-current" /> {challenge.reward}
                    </div>
                  </div>
                  <p className="text-sm text-slate-400 mb-4">{challenge.description}</p>
                  
                  <div className="relative pt-1">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-semibold inline-block text-slate-300">İlerleme</span>
                      <span className="text-xs font-bold inline-block text-white">
                        {challenge.progress} / {challenge.total}
                      </span>
                    </div>
                    <div className="overflow-hidden h-2.5 mb-2 text-xs flex rounded-full bg-[#0a0c10] shadow-inner">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${percent}%` }}
                        transition={{ duration: 1, delay: 0.2 }}
                        className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r ${challenge.color}`} 
                      />
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Friends & Activity */}
        <div className="bg-[#15171e] border border-white/5 rounded-3xl p-6 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-400 to-teal-500" />
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2 text-white">
              <Users className="w-6 h-6 text-emerald-500" /> Arkadaşlar
            </h2>
            <Button size="icon" variant="ghost" className="rounded-full hover:bg-white/10 h-8 w-8 text-slate-300">
              <Search className="w-4 h-4" />
            </Button>
          </div>

          <div className="flex items-center gap-3 overflow-x-auto pb-4 mb-2 scrollbar-hide">
            {/* Add Friend Button */}
            <div className="flex flex-col items-center gap-2 min-w-[60px]">
              <div className="w-14 h-14 rounded-full border-2 border-dashed border-white/20 flex items-center justify-center bg-[#1a1c23] hover:bg-white/5 hover:border-white/40 transition-colors cursor-pointer">
                <Plus className="w-6 h-6 text-slate-400" />
              </div>
              <span className="text-xs font-medium text-slate-400">Ekle</span>
            </div>
            
            {/* Online Friends */}
            {FRIENDS_ACTIVITY.map((friend) => (
              <div key={friend.id} className="flex flex-col items-center gap-2 min-w-[60px] cursor-pointer group">
                <div className="w-14 h-14 rounded-full bg-[#1e212b] border border-white/10 flex items-center justify-center text-2xl relative shadow-md group-hover:border-indigo-400 transition-colors">
                  {friend.avatar}
                  <div className="absolute bottom-0 right-0 w-3.5 h-3.5 bg-green-400 border-2 border-[#15171e] rounded-full"></div>
                </div>
                <span className="text-xs font-bold text-slate-300">{friend.name}</span>
              </div>
            ))}
          </div>
          
          <div className="mt-4 pt-6 border-t border-white/5">
            <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Aktiviteler</h3>
            <div className="space-y-4">
              {FRIENDS_ACTIVITY.map((activity, idx) => (
                <motion.div 
                  key={`act-${activity.id}`}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.15 }}
                  className="flex gap-3 items-start"
                >
                  <div className="w-10 h-10 rounded-full bg-[#1e212b] border border-white/10 flex items-center justify-center text-lg shrink-0 mt-1">
                    {activity.avatar}
                  </div>
                  <div className="bg-[#1a1c23] border border-white/5 p-3 rounded-2xl rounded-tl-sm flex-1">
                    <p className="text-sm text-slate-300">
                      <span className="font-bold text-white">{activity.name}</span> {activity.action}
                    </p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-slate-500 font-medium">{activity.time}</span>
                      <button className="flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-indigo-400 transition-colors bg-white/5 px-2 py-1 rounded-md">
                        <ThumbsUp className="w-3.5 h-3.5" />
                        {activity.likes} Beğeni
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
