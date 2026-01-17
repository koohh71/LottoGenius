import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, PlusCircle, X, BarChart2, Hash, Wand2, PlusSquare, BookOpen } from 'lucide-react';

// Components
import NumberGrid from './components/NumberGrid';
import GameList from './components/GameList';
import StatsDashboard from './components/StatsDashboard';
import UserGuide from './components/UserGuide';

function App() {
  const [activeTab, setActiveTab] = useState('generate');
  
  // Generator States
  const [historyLimit, setHistoryLimit] = useState(10000); 
  const [fixedNums, setFixedNums] = useState([]);
  const [excludedNums, setExcludedNums] = useState([]);
  const [mode, setMode] = useState('fixed'); 
  
  // Games List
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(false);

  // Update & Stats States
  const [showManual, setShowManual] = useState(false);
  const [mRound, setMRound] = useState('');
  const [mNums, setMNums] = useState(['','','','','','']);
  const [mBonus, setMBonus] = useState('');
  const [latestRound, setLatestRound] = useState(0);
  const [statsData, setStatsData] = useState(null);
  const [statsLimit, setStatsLimit] = useState(10000);

  const API_BASE = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

  // --- Initial Data Fetching ---
  useEffect(() => {
    fetchLatestRound();
  }, []);

  useEffect(() => {
    if (activeTab === 'stats') fetchStats();
  }, [activeTab, statsLimit]);

  const fetchLatestRound = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/latest-round`);
      setLatestRound(res.data.latest_round);
    } catch (e) { console.error("Load failed"); }
  };

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/stats?limit=${statsLimit}`);
      setStatsData(res.data);
    } catch (e) { console.error("Stats failed", e); }
  };

  // --- Generator Logic ---
  const addManualGame = () => {
    if (games.length >= 5) return alert("최대 5게임까지만 가능합니다.");
    if (fixedNums.length !== 6) return alert("수동 게임은 번호 6개를 모두 선택해야 합니다.");
    
    const newGame = {
      id: Date.now(),
      type: 'MANUAL',
      numbers: [...fixedNums].sort((a, b) => a - b)
    };
    setGames([...games, newGame]);
    setFixedNums([]);
  };

  const fillAutoGames = async () => {
    const needed = 5 - games.length;
    if (needed <= 0) return alert("이미 5게임이 꽉 찼습니다.");

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/generate`, {
        history_limit: historyLimit,
        fixed_nums: fixedNums,
        excluded_nums: excludedNums,
        count: needed
      });
      
      const newGames = response.data.recommendations.map((nums, idx) => ({
        id: Date.now() + idx,
        type: 'AUTO',
        numbers: nums
      }));
      
      setGames([...games, ...newGames]);
    } catch (error) {
      alert("서버 통신 오류");
    }
    setLoading(false);
  };

  const handleManualSave = async () => {
    if (!mRound || mNums.some(n => !n) || !mBonus) return alert("입력 확인 필요");
    try {
      const res = await axios.post(`${API_BASE}/api/add-round`, {
        round_no: parseInt(mRound), numbers: mNums.map(n => parseInt(n)), bonus: parseInt(mBonus)
      });
      alert(res.data.message);
      fetchLatestRound();
      setShowManual(false);
      if(activeTab === 'stats') fetchStats();
    } catch { alert("저장 실패"); }
  };

  const getNumberColor = (num) => {
    if (num <= 10) return 'bg-yellow-400';
    if (num <= 20) return 'bg-blue-400';
    if (num <= 30) return 'bg-red-400';
    if (num <= 40) return 'bg-gray-400';
    return 'bg-green-400';
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-6 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-6 space-y-5">
        
        {/* Header */}
        <div className="flex justify-between items-center">
            <div>
                <h1 className="text-2xl font-bold text-gray-800">🔮 Lotto Genius</h1>
                <p className="text-gray-500 text-xs">AI Data Analytics</p>
            </div>
            <div className="flex gap-2">
                <button onClick={() => setShowManual(!showManual)} className="text-gray-600 p-2 bg-gray-100 rounded-full transition hover:bg-gray-200">
                    {showManual ? <X size={20}/> : <PlusCircle size={20}/>}
                </button>
            </div>
        </div>

        {/* Manual Input Modal */}
        {showManual && (
            <div className="bg-orange-50 p-4 rounded-xl border border-orange-100 space-y-3 animate-fade-in">
                <h3 className="font-bold text-orange-800 text-sm">회차 정보 수동 등록</h3>
                <div className="flex gap-2">
                    <input type="number" placeholder="회차" value={mRound} onChange={e=>setMRound(e.target.value)} className="w-20 p-2 rounded border border-orange-200 text-sm"/>
                </div>
                <div className="grid grid-cols-6 gap-1">
                    {mNums.map((n,i)=>(
                        <input key={i} type="number" value={n} onChange={e=>{
                            const next = [...mNums]; next[i]=e.target.value; setMNums(next);
                        }} className="w-full p-1 rounded border border-orange-200 text-center text-sm"/>
                    ))}
                </div>
                <div className="flex gap-2">
                    <input type="number" placeholder="Bonus" value={mBonus} onChange={e=>setMBonus(e.target.value)} className="w-16 p-2 rounded border border-orange-200 text-sm"/>
                    <button onClick={handleManualSave} className="flex-1 bg-orange-500 text-white font-bold rounded-lg py-2 hover:bg-orange-600">DB 저장</button>
                </div>
            </div>
        )}

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-200">
            <button onClick={() => setActiveTab('generate')} className={`flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 border-b-2 transition ${activeTab === 'generate' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-400 hover:text-gray-600'}`}>
                <Hash size={16}/> 번호 생성
            </button>
            <button onClick={() => setActiveTab('stats')} className={`flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 border-b-2 transition ${activeTab === 'stats' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-400 hover:text-gray-600'}`}>
                <BarChart2 size={16}/> 통계 분석
            </button>
            <button onClick={() => setActiveTab('guide')} className={`flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 border-b-2 transition ${activeTab === 'guide' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-400 hover:text-gray-600'}`}>
                <BookOpen size={16}/> 가이드
            </button>
        </div>

        {/* --- GENERATE TAB --- */}
        {activeTab === 'generate' && (
            <div className="space-y-6 animate-fade-in">
                <div className="flex bg-gray-100 p-1 rounded-lg">
                    <button onClick={() => setHistoryLimit(30)} className={`flex-1 py-2 text-xs font-medium rounded-md transition ${historyLimit === 30 ? 'bg-white shadow text-blue-600' : 'text-gray-500'}`}>최근 30회 분석</button>
                    <button onClick={() => setHistoryLimit(10000)} className={`flex-1 py-2 text-xs font-medium rounded-md transition ${historyLimit === 10000 ? 'bg-white shadow text-blue-600' : 'text-gray-500'}`}>전체 분석</button>
                </div>

                {/* Component: Number Grid */}
                <NumberGrid 
                    mode={mode} setMode={setMode}
                    fixedNums={fixedNums} setFixedNums={setFixedNums}
                    excludedNums={excludedNums} setExcludedNums={setExcludedNums}
                    getNumberColor={getNumberColor}
                />

                {/* Action Buttons */}
                <div className="grid grid-cols-2 gap-3">
                    <button 
                        onClick={addManualGame}
                        disabled={fixedNums.length !== 6 || games.length >= 5}
                        className="py-3 bg-white border-2 border-blue-100 text-blue-600 font-bold rounded-xl flex items-center justify-center gap-1 hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                    >
                        <PlusSquare size={18}/> 수동 추가
                    </button>
                    <button 
                        onClick={fillAutoGames}
                        disabled={games.length >= 5 || loading}
                        className="py-3 bg-indigo-600 text-white font-bold rounded-xl shadow-lg flex items-center justify-center gap-1 hover:bg-indigo-700 disabled:opacity-50 transition"
                    >
                        {loading ? <Loader2 className="animate-spin" size={18}/> : <Wand2 size={18}/>} 
                        {games.length === 0 ? "5게임 자동생성" : "나머지 자동채움"}
                    </button>
                </div>

                {/* Component: Game List & Save Image */}
                <GameList 
                    games={games} setGames={setGames}
                    getNumberColor={getNumberColor}
                    latestRound={latestRound}
                />
            </div>
        )}

        {/* --- STATS TAB --- */}
        {activeTab === 'stats' && (
            <StatsDashboard 
                statsData={statsData}
                statsLimit={statsLimit}
                setStatsLimit={setStatsLimit}
            />
        )}

        {/* --- GUIDE TAB --- */}
        {activeTab === 'guide' && <UserGuide />}

      </div>
    </div>
  );
}

export default App;
