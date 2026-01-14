import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, PlusCircle, X, BarChart2, Hash, Trash2, Wand2, PlusSquare, RotateCcw, BookOpen, Info, CheckCircle2, AlertCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from 'recharts';

function App() {
  const [activeTab, setActiveTab] = useState('generate');
  
  // Generator States
  const [historyLimit, setHistoryLimit] = useState(10000); // 30 -> 10000 (전체)
  const [fixedNums, setFixedNums] = useState([]);      // 수동 입력 시 선택된 번호들로도 사용
  const [excludedNums, setExcludedNums] = useState([]);
  const [mode, setMode] = useState('fixed'); // 'fixed' | 'excluded'
  
  // Games List (최대 5게임)
  // Item structure: { id: Date.now(), type: 'AUTO' | 'MANUAL', numbers: [1, 2, 3, 4, 5, 6] }
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(false);

  // Update & Stats States
  const [showManual, setShowManual] = useState(false);
  const [mRound, setMRound] = useState('');
  const [mNums, setMNums] = useState(['','','','','','']);
  const [mBonus, setMBonus] = useState('');
  const [latestRound, setLatestRound] = useState(0);
  const [statsData, setStatsData] = useState(null);
  const [statsLimit, setStatsLimit] = useState(10000); // 30 -> 10000 (전체)

  // 환경 변수 또는 현재 호스트 기반 동적 주소 (모바일/PC 모두 호환)
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
      console.log(`Fetching stats from: ${API_BASE}/api/stats?limit=${statsLimit}`);
      const res = await axios.get(`${API_BASE}/api/stats?limit=${statsLimit}`);
      setStatsData(res.data);
    } catch (e) { console.error("통계 로드 실패", e); }
  };

  // --- Generator Logic ---
  
  // 수동 게임 추가
  const addManualGame = () => {
    if (games.length >= 5) return alert("최대 5게임까지만 가능합니다.");
    if (fixedNums.length !== 6) return alert("수동 게임은 번호 6개를 모두 선택해야 합니다.");
    
    const newGame = {
      id: Date.now(),
      type: 'MANUAL',
      numbers: [...fixedNums].sort((a, b) => a - b)
    };
    setGames([...games, newGame]);
    setFixedNums([]); // 추가 후 초기화
  };

  // 나머지 자동 채우기
  const fillAutoGames = async () => {
    const needed = 5 - games.length;
    if (needed <= 0) return alert("이미 5게임이 꽉 찼습니다.");

    setLoading(true);
    try {
      // 고정수가 있다면 자동 생성 시 포함됨
      const response = await axios.post(`${API_BASE}/api/generate`, {
        history_limit: historyLimit,
        fixed_nums: fixedNums, // 현재 선택된 번호를 고정수로 사용
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

  const removeGame = (id) => {
    setGames(games.filter(g => g.id !== id));
  };

  const clearAllGames = () => {
    setGames([]);
    setFixedNums([]);
    setExcludedNums([]);
  };

  // --- Update Logic ---

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

  // --- UI Helpers ---
  const getNumberColor = (num) => {
    if (num <= 10) return 'bg-yellow-400';
    if (num <= 20) return 'bg-blue-400';
    if (num <= 30) return 'bg-red-400';
    if (num <= 40) return 'bg-gray-400';
    return 'bg-green-400';
  };
  
  const COLORS = ['#FACC15', '#60A5FA', '#F87171', '#9CA3AF', '#4ADE80'];

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
                <button onClick={() => setShowManual(!showManual)} title="최신 회차 수동 등록" className="text-gray-600 p-2 bg-gray-100 rounded-full transition hover:bg-gray-200">
                    {showManual ? <X size={20}/> : <PlusCircle size={20}/>}
                </button>
            </div>
        </div>

        {/* Manual Input Modal (DB Update) */}
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
                
                {/* 1. History Limit Options */}
                <div className="flex bg-gray-100 p-1 rounded-lg">
                    <button onClick={() => setHistoryLimit(30)} className={`flex-1 py-2 text-xs font-medium rounded-md transition ${historyLimit === 30 ? 'bg-white shadow text-blue-600' : 'text-gray-500'}`}>최근 30회 분석</button>
                    <button onClick={() => setHistoryLimit(10000)} className={`flex-1 py-2 text-xs font-medium rounded-md transition ${historyLimit === 10000 ? 'bg-white shadow text-blue-600' : 'text-gray-500'}`}>전체 분석</button>
                </div>

                {/* 2. Number Selector */}
                <div className="space-y-2">
                     <div className="flex justify-between items-center px-1">
                        <span className="text-xs font-bold text-gray-500 flex items-center gap-1">
                             {mode === 'fixed' ? '선택한 번호를' : '선택한 번호를'} 
                             <span className={mode==='fixed' ? 'text-blue-600' : 'text-red-500'}> {mode === 'fixed' ? '포함(수동)' : '제외'}</span>
                             {(fixedNums.length > 0 || excludedNums.length > 0) && (
                                <button onClick={()=>{setFixedNums([]); setExcludedNums([]);}} className="ml-2 text-gray-400 hover:text-gray-600" title="선택 초기화">
                                    <RotateCcw size={12}/>
                                </button>
                             )}
                        </span>
                        <div className="flex gap-1">
                             <button onClick={()=>setMode('fixed')} className={`px-3 py-1 rounded-full text-[10px] font-bold border transition ${mode==='fixed'?'bg-blue-100 text-blue-700 border-blue-200':'bg-white text-gray-400 border-gray-200'}`}>포함/수동</button>
                             <button onClick={()=>setMode('excluded')} className={`px-3 py-1 rounded-full text-[10px] font-bold border transition ${mode==='excluded'?'bg-red-100 text-red-700 border-red-200':'bg-white text-gray-400 border-gray-200'}`}>제외</button>
                        </div>
                     </div>
                     <div className="grid grid-cols-7 gap-1.5">
                        {Array.from({length:45},(_,i)=>i+1).map(n=>(
                            <button 
                                key={n} 
                                onClick={()=>{
                                    if(mode==='fixed'){
                                        if(excludedNums.includes(n)) return;
                                        fixedNums.includes(n) ? setFixedNums(fixedNums.filter(x=>x!==n)) : (fixedNums.length<6 && setFixedNums([...fixedNums,n].sort((a,b)=>a-b)));
                                    } else {
                                        if(fixedNums.includes(n)) return;
                                        excludedNums.includes(n) ? setExcludedNums(excludedNums.filter(x=>x!==n)) : setExcludedNums([...excludedNums,n].sort((a,b)=>a-b));
                                    }
                                }} 
                                className={`aspect-square rounded-lg text-xs font-bold transition-all duration-200 transform shadow-sm
                                    ${fixedNums.includes(n) 
                                        ? `${getNumberColor(n)} text-white scale-110 z-10 ring-2 ring-white` 
                                        : excludedNums.includes(n) 
                                        ? 'bg-gray-800 text-gray-500 line-through scale-90 opacity-70' 
                                        : `${getNumberColor(n).replace('bg-', 'bg-opacity-20 bg-')} ${getNumberColor(n).replace('bg-', 'text-').replace('400', '700')} hover:bg-opacity-40`
                                    }`}
                            >
                                {n}
                            </button>
                        ))}
                    </div>
                </div>

                {/* 3. Action Buttons (Manual Add & Auto Fill) */}
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

                {/* 4. Games List */}
                <div className="bg-gray-100 rounded-xl p-4 min-h-[200px]">
                    <div className="flex justify-between items-center mb-3">
                        <span className="text-xs font-bold text-gray-500">생성된 게임 ({games.length}/5)</span>
                        {games.length > 0 && (
                            <button onClick={clearAllGames} className="text-xs text-red-400 flex items-center gap-1 hover:text-red-600"><Trash2 size={12}/> 전체삭제</button>
                        )}
                    </div>
                    
                    {games.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-32 text-gray-400 space-y-2">
                            <Hash size={32} className="opacity-20"/>
                            <p className="text-xs">번호를 선택해 수동 추가하거나,<br/>자동 생성 버튼을 눌러주세요.</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {games.map((game, i) => (
                                <div key={game.id} className="bg-white p-3 rounded-lg flex justify-between items-center shadow-sm animate-fade-in-up">
                                    <div className="flex items-center gap-3">
                                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${game.type === 'MANUAL' ? 'bg-blue-50 text-blue-600 border-blue-100' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>
                                            {game.type === 'MANUAL' ? '수동' : '자동'}
                                        </span>
                                        <div className="flex gap-1.5">
                                            {game.numbers.map(n => (
                                                <div key={n} className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-[10px] font-bold shadow-sm ${getNumberColor(n)}`}>{n}</div>
                                            ))}
                                        </div>
                                    </div>
                                    <button onClick={() => removeGame(game.id)} className="text-gray-300 hover:text-red-500"><X size={16}/></button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        )}

        {/* --- STATS TAB --- */}
        {activeTab === 'stats' && (
            <div className="space-y-6 animate-fade-in">
                 <div className="flex bg-gray-100 p-1 rounded-lg">
                    <button onClick={() => setStatsLimit(30)} className={`flex-1 py-2 text-xs font-medium rounded-md transition ${statsLimit === 30 ? 'bg-white shadow text-indigo-600' : 'text-gray-500'}`}>최근 30회</button>
                    <button onClick={() => setStatsLimit(10000)} className={`flex-1 py-2 text-xs font-medium rounded-md transition ${statsLimit === 10000 ? 'bg-white shadow text-indigo-600' : 'text-gray-500'}`}>전체</button>
                </div>
                {!statsData ? (<div className="flex justify-center py-10"><Loader2 className="animate-spin text-gray-400"/></div>) : (
                    <>
                        {/* 1. Bar Chart: Most Frequent Numbers */}
                        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
                            <h3 className="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2">🔥 최다 당첨 번호 (Top 10)</h3>
                            <div className="h-48 w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={statsData.frequency}>
                                        <XAxis dataKey="num" tick={{fontSize: 10}} />
                                        <YAxis hide />
                                        <Tooltip cursor={{fill: '#f3f4f6'}} contentStyle={{borderRadius: '8px', fontSize: '12px'}} />
                                        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                                            {statsData.frequency.map((entry, index) => <Cell key={`cell-${index}`} fill={index < 3 ? '#6366f1' : '#cbd5e1'} />)}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* 2. Bar Chart: Least Frequent Numbers (NEW) */}
                        {statsData.min_frequency && (
                            <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
                                <h3 className="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2">❄️ 최소 당첨 번호 (Bottom 10)</h3>
                                <div className="h-48 w-full">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={statsData.min_frequency}>
                                            <XAxis dataKey="num" tick={{fontSize: 10}} />
                                            <YAxis hide />
                                            <Tooltip cursor={{fill: '#fff1f2'}} contentStyle={{borderRadius: '8px', fontSize: '12px'}} />
                                            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                                                {statsData.min_frequency.map((entry, index) => <Cell key={`cell-min-${index}`} fill={index < 3 ? '#ef4444' : '#fdba74'} />)}
                                            </Bar>
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        )}

                        {/* 3. Pie Chart: Number Range Distribution */}
                        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
                            <h3 className="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2">🎨 구간별 분포</h3>
                            <div className="h-64 w-full relative">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie 
                                            data={statsData.ranges} 
                                            innerRadius={50} 
                                            outerRadius={65} 
                                            paddingAngle={5} 
                                            dataKey="value"
                                            label={({name, percent}) => `${name} (${(percent * 100).toFixed(0)}%)`}
                                            labelLine={true}
                                            style={{ fontSize: '11px', fontWeight: 'bold' }}
                                        >
                                            {statsData.ranges.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                                        </Pie>
                                        <Legend iconSize={8} wrapperStyle={{fontSize: '11px', bottom: '0px'}}/>
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="absolute inset-0 flex items-center justify-center pointer-events-none pb-8"><span className="text-xs font-bold text-gray-400">비율</span></div>
                            </div>
                        </div>
                    </>
                )}
            </div>
        )}

        {/* --- GUIDE TAB --- */}
        {activeTab === 'guide' && (
            <div className="space-y-6 animate-fade-in text-gray-700">
                
                {/* 1. Intro */}
                <div className="bg-indigo-50 p-4 rounded-xl border border-indigo-100">
                    <h3 className="font-bold text-indigo-800 text-sm flex items-center gap-2 mb-2">
                        <Info size={16}/> Lotto Genius란?
                    </h3>
                    <p className="text-xs leading-relaxed text-indigo-700">
                        과거 당첨 데이터를 정밀 분석하여, 과학적인 가중치 알고리즘으로 최적의 번호를 추천해주는 AI 기반 로또 분석기입니다.
                    </p>
                </div>

                {/* 2. Number Selection */}
                <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm space-y-3">
                    <h3 className="font-bold text-gray-800 text-sm flex items-center gap-2">
                        <Hash size={16} className="text-blue-500"/> 번호 조합 및 생성
                    </h3>
                    <ul className="space-y-2 text-xs">
                        <li className="flex gap-2">
                            <CheckCircle2 size={14} className="text-blue-500 shrink-0"/>
                            <span>
                                <strong>포함/수동:</strong> 고정할 번호를 선택하세요. 6개를 다 채우면 <strong>[수동 추가]</strong>로 내 리스트에 담을 수 있습니다.
                            </span>
                        </li>
                        <li className="flex gap-2">
                            <X size={14} className="text-red-500 shrink-0"/>
                            <span>
                                <strong>제외수:</strong> 분석에서 뺄 번호를 선택하세요. AI가 추천 번호를 만들 때 이 번호들은 제외됩니다.
                            </span>
                        </li>
                        <li className="flex gap-2">
                            <Wand2 size={14} className="text-indigo-500 shrink-0"/>
                            <span>
                                <strong>자동 채움:</strong> 내가 고른 번호 외에 빈 자리를 AI가 가중치 알고리즘으로 채워 총 5게임을 완성합니다.
                            </span>
                        </li>
                    </ul>
                </div>

                {/* 3. Stats Analysis */}
                <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm space-y-3">
                    <h3 className="font-bold text-gray-800 text-sm flex items-center gap-2">
                        <BarChart2 size={16} className="text-purple-500"/> 통계 데이터 활용법
                    </h3>
                    <div className="space-y-3 text-xs">
                        <div className="p-2 bg-gray-50 rounded">
                            <p className="font-bold text-indigo-700">🔥 최다 당첨 번호 (HOT)</p>
                            <p className="text-gray-500 mt-1">최근 가장 기세가 좋은 번호들입니다. 흐름을 따르고 싶을 때 참고하세요.</p>
                        </div>
                        <div className="p-2 bg-gray-50 rounded">
                            <p className="font-bold text-red-600">❄️ 최소 당첨 번호 (COLD)</p>
                            <p className="text-gray-500 mt-1">오랫동안 나오지 않은 번호들입니다. 곧 나올 때가 된 번호를 예측할 때 유용합니다.</p>
                        </div>
                        <div className="p-2 bg-gray-50 rounded">
                            <p className="font-bold text-green-600">🎨 구간별 분포</p>
                            <p className="text-gray-500 mt-1">번호 대역별 비율을 확인하여 특정 구간에 번호가 쏠리지 않도록 균형 있게 조합하세요.</p>
                        </div>
                    </div>
                </div>

                {/* 4. Update */}
                <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm space-y-3">
                    <h3 className="font-bold text-gray-800 text-sm flex items-center gap-2">
                        <PlusCircle size={16} className="text-orange-500"/> 데이터 관리
                    </h3>
                    <p className="text-xs text-gray-600 leading-relaxed">
                        매주 토요일 추첨이 끝나면 상단의 <strong>[+]</strong> 버튼을 눌러 당첨 번호를 입력해 주세요. 
                        <strong> 즉시 DB에 반영</strong>되어 더욱 정교한 AI 분석이 가능해집니다.
                    </p>
                </div>

            </div>
        )}

      </div>
    </div>
  );
}

export default App;