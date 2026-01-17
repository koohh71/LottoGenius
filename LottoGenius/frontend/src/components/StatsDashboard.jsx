import React from 'react';
import { Loader2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from 'recharts';

const COLORS = ['#FACC15', '#60A5FA', '#F87171', '#9CA3AF', '#4ADE80'];

const StatsDashboard = ({ statsData, statsLimit, setStatsLimit }) => {
    return (
        <div className="space-y-6 animate-fade-in">
             <div className="flex bg-gray-100 p-1 rounded-lg">
                <button onClick={() => setStatsLimit(30)} className={`flex-1 py-2 text-xs font-medium rounded-md transition ${statsLimit === 30 ? 'bg-white shadow text-indigo-600' : 'text-gray-500'}`}>최근 30회</button>
                <button onClick={() => setStatsLimit(10000)} className={`flex-1 py-2 text-xs font-medium rounded-md transition ${statsLimit === 10000 ? 'bg-white shadow text-indigo-600' : 'text-gray-500'}`}>전체</button>
            </div>
            
            {!statsData ? (
                <div className="flex justify-center py-10"><Loader2 className="animate-spin text-gray-400"/></div>
            ) : (
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

                    {/* 2. Bar Chart: Least Frequent Numbers */}
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
    );
};

export default StatsDashboard;
