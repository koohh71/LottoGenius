import React from 'react';
import { Info, Hash, CheckCircle2, X, RotateCcw, Wand2, PlusSquare, PlusCircle, BarChart2, AlertCircle } from 'lucide-react';

const UserGuide = () => {
    return (
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
                    <Hash size={16} className="text-blue-500"/> 번호 조합 및 AI 필터링
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
                            <strong>제외수:</strong> 분석에서 뺄 번호를 선택하세요.
                        </span>
                    </li>
                    <li className="flex gap-2">
                        <Wand2 size={14} className="text-indigo-500 shrink-0"/>
                        <div className="flex flex-col gap-1">
                            <span><strong>스마트 AI 필터링:</strong> 자동 생성 시 비현실적인 패턴을 자동으로 걸러냅니다.</span>
                            <ul className="list-disc pl-4 text-gray-500 space-y-0.5">
                                <li>3개 이상 연속된 번호 제외 (예: 11,12,13)</li>
                                <li>특정 구간 쏠림 현상 방지</li>
                                <li>홀수/짝수 비율 균형 조정</li>
                            </ul>
                        </div>
                    </li>
                </ul>
            </div>

            {/* 3. Game Modes */}
            <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm space-y-3">
                <h3 className="font-bold text-gray-800 text-sm flex items-center gap-2">
                    <Wand2 size={16} className="text-purple-500"/> 생성 모드 (자동/수동)
                </h3>
                <div className="space-y-2 text-xs">
                    <div className="flex items-start gap-2 bg-gray-50 p-2 rounded">
                        <PlusSquare size={14} className="text-blue-600 mt-0.5 shrink-0"/>
                        <div>
                            <span className="font-bold text-gray-700">수동 추가 (반자동)</span>
                            <p className="text-gray-500 mt-1">번호 6개를 직접 골라 <strong>[수동 추가]</strong> 버튼을 누르면 내 게임 리스트에 쏙 들어갑니다.</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-2 bg-gray-50 p-2 rounded">
                        <Wand2 size={14} className="text-indigo-600 mt-0.5 shrink-0"/>
                        <div>
                            <span className="font-bold text-gray-700">자동 채우기</span>
                            <p className="text-gray-500 mt-1">수동으로 몇 게임 넣은 뒤 <strong>[나머지 자동채움]</strong>을 누르면, 빈 자리를 AI 추천 번호로 가득 채워줍니다.</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* 4. Stats Analysis */}
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

            {/* 5. Update */}
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
    );
};

export default UserGuide;
