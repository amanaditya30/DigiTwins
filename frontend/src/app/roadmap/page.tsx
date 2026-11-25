'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Map, Target, CheckSquare, Plus, Loader, BookOpen } from 'lucide-react';
import { apiGet, apiPost, getToken } from '@/utils/api';
import Sidebar from '@/components/Sidebar';
import GlassCard from '@/components/GlassCard';

export default function RoadmapPage() {
  const router = useRouter();
  const [roadmap, setRoadmap] = useState<any>(null);
  const [dsaHistory, setDsaHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Logger form states
  const [topic, setTopic] = useState('Arrays');
  const [qName, setQName] = useState('Two Sum');
  const [difficulty, setDifficulty] = useState('Easy');
  const [status, setStatus] = useState('Solved');
  const [logging, setLogging] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      router.push('/');
      return;
    }
    fetchData();
  }, [router]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const roadData = await apiGet('/api/roadmap');
      setRoadmap(roadData);
      
      const histData = await apiGet('/api/roadmap/dsa/progress');
      setDsaHistory(histData);
    } catch (err) {
      console.error('Error fetching roadmap details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogProgress = async (e: React.FormEvent) => {
    e.preventDefault();
    setLogging(true);
    try {
      const payload = {
        topic,
        question_name: qName,
        difficulty,
        status
      };
      await apiPost('/api/roadmap/dsa/progress', payload);
      setQName('');
      
      // Re-fetch progress list
      const histData = await apiGet('/api/roadmap/dsa/progress');
      setDsaHistory(histData);
    } catch (err) {
      alert('Failed to log DSA progress.');
    } finally {
      setLogging(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-[#090d1a] items-center justify-center">
        <div className="text-slate-400 animate-pulse text-lg flex items-center space-x-2">
          <Map className="w-6 h-6 animate-spin text-blue-500" />
          <span>Formulating learning syllabus roadmaps...</span>
        </div>
      </div>
    );
  }

  // Fallback defaults if empty
  const weekly = (roadmap?.weekly_tasks && Object.keys(roadmap.weekly_tasks).length > 0) 
    ? roadmap.weekly_tasks 
    : {
        'Week 1': ['Study Arrays & Two-pointer logic details', 'Conduct initial resume formatting audits'],
        'Week 2': ['Study Stack, Queues, and Sliding window algorithms', 'Build basic FastAPI CRUD API routing'],
        'Week 3': ['Study Binary Search & Heap data structures', 'Implement database relationships in SQLModel'],
        'Week 4': ['Study Graph BFS/DFS implementations', 'Conduct 1 complete Technical mock interview']
      };

  const monthly = (roadmap?.monthly_tasks && Object.keys(roadmap.monthly_tasks).length > 0)
    ? roadmap.monthly_tasks
    : {
        'Month 1': ['Consolidate intermediate algorithms and finish 1 full-stack project service'],
        'Month 2': ['Focus on databases tuning, system designs, and complete mock assessments']
      };

  const recommendedDsa = [
    { name: 'Two Sum', topic: 'Arrays', difficulty: 'Easy', platform: 'LeetCode' },
    { name: 'Valid Parentheses', topic: 'Stacks', difficulty: 'Easy', platform: 'LeetCode' },
    { name: 'Longest Substring Without Repeating Characters', topic: 'Sliding Window', difficulty: 'Medium', platform: 'LeetCode' },
    { name: 'Number of Islands', topic: 'Graphs', difficulty: 'Medium', platform: 'LeetCode' }
  ];

  return (
    <div className="min-h-screen pl-64 flex bg-[#090d1a] text-slate-100">
      <Sidebar />
      
      <div className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">
            Roadmap & <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">DSA Advisor</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">Review weekly study guides and track your competitive coding progress.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Weekly Roadmap */}
          <div className="lg:col-span-6 flex flex-col space-y-8">
            <GlassCard>
              <h3 className="text-slate-300 font-semibold text-base mb-6 flex items-center space-x-2">
                <BookOpen className="w-4 h-4 text-blue-400" />
                <span>🗺️ Weekly Preparation Roadmaps</span>
              </h3>
              
              <div className="space-y-6">
                {Object.entries(weekly).map(([week, tasks]: [string, any]) => (
                  <div key={week} className="border-l-2 border-blue-500/20 pl-4 space-y-2">
                    <h4 className="text-sm font-bold text-slate-200">{week}</h4>
                    <ul className="space-y-1.5">
                      {tasks.map((task: string, i: number) => (
                        <li key={i} className="text-slate-400 text-xs flex items-start space-x-2 leading-relaxed">
                          <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1" />
                          <span>{task}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>

              <div className="border-t border-white/5 mt-6 pt-6 space-y-3">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">High-Level Milestones</h4>
                {Object.entries(monthly).map(([month, goals]: [string, any]) => (
                  <p key={month} className="text-slate-300 text-xs">
                    <strong>{month}:</strong> {goals.join(', ')}
                  </p>
                ))}
              </div>
            </GlassCard>
          </div>

          {/* Right Column: Recommended & Logging */}
          <div className="lg:col-span-6 flex flex-col space-y-8">
            {/* Recommendations */}
            <GlassCard>
              <h3 className="text-slate-300 font-semibold text-base mb-4 flex items-center space-x-2">
                <Target className="w-4 h-4 text-purple-400" />
                <span>🎯 Recommended DSA Questions</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {recommendedDsa.map((item, idx) => (
                  <div key={idx} className="bg-slate-950/40 border border-white/5 p-3 rounded-xl flex flex-col justify-between">
                    <div>
                      <h5 className="font-bold text-slate-200 text-xs">{item.name}</h5>
                      <span className="text-[10px] text-slate-400 mt-0.5 block">{item.topic} • {item.platform}</span>
                    </div>
                    <span className={`text-[10px] font-semibold tracking-wide w-fit px-2 py-0.5 rounded-full mt-2 ${
                      item.difficulty === 'Easy' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                    }`}>
                      {item.difficulty}
                    </span>
                  </div>
                ))}
              </div>
            </GlassCard>

            {/* Log form */}
            <GlassCard>
              <h3 className="text-slate-300 font-semibold text-base mb-4 flex items-center space-x-2">
                <Plus className="w-4 h-4 text-pink-400" />
                <span>📥 Log Practiced Question</span>
              </h3>

              <form onSubmit={handleLogProgress} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Topic</label>
                    <input
                      type="text"
                      required
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-2 text-slate-200 text-xs focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Question Name</label>
                    <input
                      type="text"
                      required
                      value={qName}
                      onChange={(e) => setQName(e.target.value)}
                      className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-2 text-slate-200 text-xs focus:outline-none focus:border-blue-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Difficulty</label>
                    <select
                      value={difficulty}
                      onChange={(e) => setDifficulty(e.target.value)}
                      className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-2 text-slate-200 text-xs focus:outline-none focus:border-blue-500"
                    >
                      <option value="Easy">Easy</option>
                      <option value="Medium">Medium</option>
                      <option value="Hard">Hard</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Status</label>
                    <select
                      value={status}
                      onChange={(e) => setStatus(e.target.value)}
                      className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-2 text-slate-200 text-xs focus:outline-none focus:border-blue-500"
                    >
                      <option value="Solved">Solved</option>
                      <option value="In Progress">In Progress</option>
                    </select>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={logging}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-2.5 rounded-xl text-xs shadow-md transition-all flex items-center justify-center space-x-1"
                >
                  {logging ? <Loader className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
                  <span>Log Practice Question</span>
                </button>
              </form>
            </GlassCard>

            {/* Solved Question History List */}
            <GlassCard className="flex-1">
              <h3 className="text-slate-300 font-semibold text-base mb-4 flex items-center space-x-2">
                <CheckSquare className="w-4 h-4 text-emerald-400" />
                <span>📋 Practice History Log</span>
              </h3>
              <div className="space-y-3 overflow-y-auto max-h-48">
                {dsaHistory.length === 0 ? (
                  <p className="text-slate-500 text-xs">No logged questions found. Start practicing and submit your questions!</p>
                ) : (
                  dsaHistory.map((item) => (
                    <div key={item.id} className="flex justify-between items-center p-3 bg-slate-950/40 rounded-xl border border-white/5">
                      <div>
                        <h5 className="font-bold text-slate-200 text-xs">{item.question_name}</h5>
                        <span className="text-[10px] text-slate-400 mt-0.5 block">{item.topic} • {item.difficulty}</span>
                      </div>
                      <span className={`text-[10px] font-semibold tracking-wider ${
                        item.status.toLowerCase() === 'solved' ? 'text-emerald-400' : 'text-amber-400'
                      }`}>
                        {item.status.toLowerCase() === 'solved' ? '✅ Solved' : '⏳ Active'}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </GlassCard>
          </div>
        </div>
      </div>
    </div>
  );
}
