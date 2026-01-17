import React, { useRef } from 'react';
import { Trash2, Hash, X, Camera } from 'lucide-react';
import html2canvas from 'html2canvas';

const GameList = ({ games, setGames, getNumberColor, latestRound }) => {
    const captureRef = useRef(null);

    const removeGame = (id) => {
        setGames(games.filter(g => g.id !== id));
    };

    const clearAllGames = () => {
        setGames([]);
    };

    const handleSaveImage = async () => {
        if (!captureRef.current || games.length === 0) return;
        try {
            const canvas = await html2canvas(captureRef.current, {
                backgroundColor: '#ffffff',
                scale: 2
            });
            const link = document.createElement('a');
            link.download = `lotto_genius_${latestRound > 0 ? latestRound + 1 : 'next'}_recommendation.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
        } catch (err) {
            alert("이미지 저장 실패: " + err);
        }
    };

    return (
        <>
            <div ref={captureRef} className="bg-gray-100 rounded-xl p-4 min-h-[200px] transition-all duration-300">
                <div className="flex justify-between items-center mb-3">
                    <span className="text-xs font-bold text-gray-500">생성된 게임 ({games.length}/5)</span>
                    {games.length > 0 && (
                        <button onClick={clearAllGames} className="text-xs text-red-400 flex items-center gap-1 hover:text-red-600" data-html2canvas-ignore="true">
                            <Trash2 size={12}/> 전체삭제
                        </button>
                    )}
                </div>
                
                {games.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-32 text-gray-400 space-y-2">
                        <Hash size={32} className="opacity-20"/>
                        <p className="text-xs">번호를 선택해 수동 추가하거나,<br/>자동 생성 버튼을 눌러주세요.</p>
                    </div>
                ) : (
                    <div className="space-y-2">
                        {games.map((game) => (
                            <div key={game.id} className="bg-white p-3 rounded-lg flex justify-between items-center shadow-sm animate-fade-in-up">
                                <div className="flex items-center gap-3">
                                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${game.type === 'MANUAL' ? 'bg-blue-50 text-blue-600 border-blue-100' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>
                                        {game.type === 'MANUAL' ? '수동' : '자동'}
                                    </span>
                                    <div className="flex gap-1.5">
                                        {game.numbers.map(n => (
                                            <div key={n} className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-[10px] font-bold shadow-sm ${getNumberColor(n)}`}>
                                                {n}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <button onClick={() => removeGame(game.id)} className="text-gray-300 hover:text-red-500" data-html2canvas-ignore="true">
                                    <X size={16}/>
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {games.length > 0 && (
                <button 
                    onClick={handleSaveImage}
                    className="w-full bg-teal-500 text-white font-bold py-3 rounded-xl shadow-lg flex items-center justify-center gap-2 hover:bg-teal-600 transition transform active:scale-95"
                >
                    <Camera size={18}/> 게임 확정 및 이미지 저장
                </button>
            )}
        </>
    );
};

export default GameList;
