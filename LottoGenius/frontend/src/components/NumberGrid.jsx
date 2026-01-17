import React from 'react';
import { RotateCcw } from 'lucide-react';

const NumberGrid = ({ 
    mode, setMode, 
    fixedNums, setFixedNums, 
    excludedNums, setExcludedNums, 
    getNumberColor 
}) => {
    
    const handleNumberClick = (n) => {
        if (mode === 'fixed') {
            if (excludedNums.includes(n)) return;
            if (fixedNums.includes(n)) {
                setFixedNums(fixedNums.filter(x => x !== n));
            } else {
                if (fixedNums.length < 6) {
                    setFixedNums([...fixedNums, n].sort((a, b) => a - b));
                }
            }
        } else {
            if (fixedNums.includes(n)) return;
            if (excludedNums.includes(n)) {
                setExcludedNums(excludedNums.filter(x => x !== n));
            } else {
                setExcludedNums([...excludedNums, n].sort((a, b) => a - b));
            }
        }
    };

    return (
        <div className="space-y-2">
            <div className="flex justify-between items-center px-1">
                <span className="text-xs font-bold text-gray-500 flex items-center gap-1">
                    {mode === 'fixed' ? '선택한 번호를' : '선택한 번호를'} 
                    <span className={mode === 'fixed' ? 'text-blue-600' : 'text-red-500'}> 
                        {mode === 'fixed' ? '포함(수동)' : '제외'}
                    </span>
                    {(fixedNums.length > 0 || excludedNums.length > 0) && (
                        <button 
                            onClick={() => { setFixedNums([]); setExcludedNums([]); }} 
                            className="ml-2 text-gray-400 hover:text-gray-600" 
                            title="선택 초기화"
                        >
                            <RotateCcw size={12}/>
                        </button>
                    )}
                </span>
                <div className="flex gap-1">
                    <button onClick={() => setMode('fixed')} className={`px-3 py-1 rounded-full text-[10px] font-bold border transition ${mode === 'fixed' ? 'bg-blue-100 text-blue-700 border-blue-200' : 'bg-white text-gray-400 border-gray-200'}`}>포함/수동</button>
                    <button onClick={() => setMode('excluded')} className={`px-3 py-1 rounded-full text-[10px] font-bold border transition ${mode === 'excluded' ? 'bg-red-100 text-red-700 border-red-200' : 'bg-white text-gray-400 border-gray-200'}`}>제외</button>
                </div>
            </div>
            <div className="grid grid-cols-7 gap-1.5">
                {Array.from({ length: 45 }, (_, i) => i + 1).map(n => (
                    <button 
                        key={n} 
                        onClick={() => handleNumberClick(n)} 
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
    );
};

export default NumberGrid;
