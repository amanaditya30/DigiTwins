'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  User, 
  Settings, 
  FileText, 
  MapPin, 
  Calendar, 
  Award,
  Zap,
  TrendingUp,
  BrainCircuit,
  Upload,
  CheckCircle2
} from 'lucide-react';
import { apiGet, apiPost, apiPostFile, getToken } from '@/utils/api';
import Sidebar from '@/components/Sidebar';
import GlassCard from '@/components/GlassCard';
import { 
  Radar, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  ResponsiveContainer 
} from 'recharts';

interface Task {
  id: number;
  text: string;
  category: string;
  completed: boolean;
}

export default function Dashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<any>(null);
  const [motivation, setMotivation] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  
  // Profile Form States
  const [showConfig, setShowConfig] = useState(false);
  const [fullName, setFullName] = useState('');
  const [careerGoals, setCareerGoals] = useState('');
  const [targetCompanies, setTargetCompanies] = useState('');
  const [skills, setSkills] = useState('');
  const [interests, setInterests] = useState('');
  const [academicHistory, setAcademicHistory] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [configSaving, setConfigSaving] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (!getToken()) {
      router.push('/');
      return;
    }
    fetchData();
  }, [router]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const statsData = await apiGet('/api/dashboard/stats');
      setStats(statsData);
      
      if (statsData.profile_exists) {
        // Pre-fill config form
        setFullName(statsData.skills ? statsData.skills.full_name || '' : '');
        setCareerGoals(statsData.career_goals || '');
        setTargetCompanies(statsData.target_companies ? statsData.target_companies.join(', ') : '');
        setSkills(statsData.skills ? statsData.skills.join(', ') : '');
        // Fetch full profile to get interests and academics
        const profile = await apiGet('/api/profile');
        setFullName(profile.full_name);
        setSkills(profile.skills.join(', '));
        setInterests(profile.interests.join(', '));
        setTargetCompanies(profile.target_companies.join(', '));
        setCareerGoals(profile.career_goals);
        setAcademicHistory(profile.academic_history);
      }
      
      const motivationData = await apiGet('/api/planner/motivation');
      setMotivation(motivationData);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTask = async (taskId: number) => {
    try {
      const res = await apiPost(`/api/planner/tasks/${taskId}/toggle`);
      setStats((prev: any) => ({
        ...prev,
        daily_tasks: res.tasks
      }));
    } catch (err) {
      console.error('Error toggling task:', err);
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setConfigSaving(true);
    try {
      const payload = {
        full_name: fullName,
        skills: skills.split(',').map(s => s.trim()).filter(Boolean),
        interests: interests.split(',').map(i => i.trim()).filter(Boolean),
        target_companies: targetCompanies.split(',').map(t => t.trim()).filter(Boolean),
        career_goals: careerGoals,
        academic_history: academicHistory,
        resume_text: ''
      };
      
      await apiPost('/api/profile', payload);
      
      if (resumeFile) {
        await apiPostFile('/api/profile/resume', resumeFile);
      }
      
      setShowConfig(false);
      await fetchData();
    } catch (err) {
      alert('Failed to update twin parameters.');
    } finally {
      setConfigSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-[#090d1a] items-center justify-center">
        <div className="text-slate-400 animate-pulse text-lg flex items-center space-x-2">
          <BrainCircuit className="w-6 h-6 animate-spin text-blue-500" />
          <span>Synchronizing career twin configurations...</span>
        </div>
      </div>
    );
  }

  // Pre-load data variables
  const profileExists = stats?.profile_exists;
  const scoreInfo = stats?.readiness || {};
  const dsaStats = stats?.dsa_stats || {};
  const interviewStats = stats?.interview_stats || {};
  const dailyTasks = stats?.daily_tasks || [];

  // Structure radar chart data
  const chartData = [
    { subject: 'Resume', score: scoreInfo.resume_score || 0 },
    { subject: 'DSA', score: scoreInfo.dsa_score || 0 },
    { subject: 'Interview', score: scoreInfo.interview_score || 0 },
    { subject: 'Skill Match', score: scoreInfo.skill_score || 0 },
    { subject: 'Project', score: scoreInfo.project_score || 0 },
  ];

  return (
    <div className="min-h-screen pl-64 flex bg-[#090d1a] text-slate-100">
      <Sidebar />
      
      <div className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Top welcome banner */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">
              Twin <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Dashboard</span>
            </h1>
            <p className="text-slate-400 text-sm mt-1">Autonomous evaluation, roadmaps, and mock recruiters metrics.</p>
          </div>
          <button
            onClick={() => setShowConfig(true)}
            className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 px-5 py-2.5 rounded-xl font-semibold text-sm shadow-lg shadow-blue-600/10 hover:-translate-y-0.5 transition-all duration-200"
          >
            <Settings className="w-4 h-4" />
            <span>Configure Twin Details</span>
          </button>
        </div>

        {!profileExists ? (
          /* Onboarding Setup View */
          <GlassCard className="text-center py-12 px-6 border border-blue-500/10 max-w-2xl mx-auto">
            <User className="w-12 h-12 text-blue-400 mx-auto mb-4 animate-bounce" />
            <h2 className="text-2xl font-bold text-slate-200">Welcome to Placement Twin AI!</h2>
            <p className="text-slate-400 text-sm mt-3 max-w-md mx-auto leading-relaxed">
              Your career replica model has not been initialized. Let's configure your skills, target companies, and goals to build your Placement Twin.
            </p>
            <button
              onClick={() => setShowConfig(true)}
              className="mt-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 px-6 py-3 rounded-xl font-bold text-sm shadow-md transition-all"
            >
              Configure Digital Twin Profile
            </button>
          </GlassCard>
        ) : (
          /* Full Dashboard Grid */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Left Column: Scores & Radar Charts */}
            <div className="lg:col-span-5 flex flex-col space-y-8">
              {/* Readiness Score Card */}
              <GlassCard className="relative overflow-hidden flex flex-col items-center py-8">
                <h3 className="text-slate-300 font-semibold text-base mb-4">Placement Readiness Score</h3>
                <div className={`text-6xl font-black ${
                  scoreInfo.overall_score >= 80 ? 'text-emerald-400' : scoreInfo.overall_score >= 60 ? 'text-amber-400' : 'text-red-400'
                }`}>
                  {scoreInfo.overall_score}%
                </div>
                <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider mt-2">
                  {scoreInfo.overall_score >= 80 ? '✓ Ready for Placements' : scoreInfo.overall_score >= 60 ? '⏳ Needs Practice' : '⚠️ Critical Skill Gap'}
                </div>
                <div className="border-t border-white/5 w-full mt-6 pt-4 text-xs text-slate-400 leading-relaxed text-center px-4">
                  <strong>Assessment:</strong> {scoreInfo.reasoning}
                </div>
              </GlassCard>

              {/* Recharts Radar Chart */}
              <GlassCard className="flex flex-col items-center">
                <h3 className="text-slate-300 font-semibold text-base mb-6 w-full text-left">Twin Balance Analysis</h3>
                <div className="w-full h-64 flex items-center justify-center">
                  {mounted ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
                        <PolarGrid stroke="rgba(255,255,255,0.06)" />
                        <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={11} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" fontSize={9} />
                        <Radar
                          name="Student"
                          dataKey="score"
                          stroke="#8b5cf6"
                          fill="#8b5cf6"
                          fillOpacity={0.25}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="text-slate-500 text-xs animate-pulse">Initializing balance chart...</div>
                  )}
                </div>
              </GlassCard>
            </div>

            {/* Right Column: Checklists, Motivation & Analytics */}
            <div className="lg:col-span-7 flex flex-col space-y-8">
              {/* Daily Action Plan Checklist */}
              <GlassCard>
                <h3 className="text-slate-300 font-semibold text-base mb-4 flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-blue-400" />
                  <span>🗓️ Today's Action Plan</span>
                </h3>
                <div className="space-y-3">
                  {dailyTasks.length === 0 ? (
                    <p className="text-slate-500 text-sm">Save your details to trigger the daily planner agent.</p>
                  ) : (
                    dailyTasks.map((task: Task) => (
                      <div 
                        key={task.id}
                        onClick={() => handleToggleTask(task.id)}
                        className={`flex items-center space-x-3 p-3.5 rounded-xl border border-white/5 cursor-pointer hover:bg-white/5 transition-all ${
                          task.completed ? 'bg-slate-900/30 opacity-60' : 'bg-slate-900/10'
                        }`}
                      >
                        <div className={`w-4 h-4 rounded border flex items-center justify-center transition-all ${
                          task.completed ? 'bg-blue-600 border-blue-500 text-white' : 'border-white/20'
                        }`}>
                          {task.completed && <CheckCircle2 className="w-3 h-3 fill-white stroke-blue-600" />}
                        </div>
                        <div className="flex-1 text-sm">
                          <span className="text-xs text-blue-400 font-semibold uppercase mr-2 tracking-wider">
                            [{task.category}]
                          </span>
                          <span className={task.completed ? 'line-through text-slate-500' : 'text-slate-200'}>
                            {task.text}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </GlassCard>

              {/* Remarks and Motivation quote panel */}
              <GlassCard>
                <h3 className="text-slate-300 font-semibold text-base mb-3 flex items-center space-x-2">
                  <Award className="w-4 h-4 text-purple-400" />
                  <span>💡 Mentor Remarks & Motivation</span>
                </h3>
                {motivation ? (
                  <div className="space-y-4">
                    <p className="italic text-slate-300 border-l-4 border-purple-500 pl-4 py-1 text-sm">
                      "{motivation.quote}"
                    </p>
                    <div>
                      <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Reminders Checklist</h5>
                      <ul className="space-y-1.5">
                        {motivation.reminders?.map((r: string, idx: number) => (
                          <li key={idx} className="text-slate-300 text-sm flex items-center space-x-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-purple-500" />
                            <span>{r}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <p className="text-slate-500 text-sm">Loading remarks...</p>
                )}
              </GlassCard>

              {/* Prep Metrics Grid */}
              <GlassCard>
                <h3 className="text-slate-300 font-semibold text-base mb-4 flex items-center space-x-2">
                  <TrendingUp className="w-4 h-4 text-pink-400" />
                  <span>📈 Preparation Metrics</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-slate-950/40 p-4 rounded-xl border border-white/5">
                    <span className="text-xs text-slate-400 font-medium">DSA Completed</span>
                    <h4 className="text-xl font-bold text-slate-100 mt-1">{dsaStats.solved} / {dsaStats.total}</h4>
                    <span className="text-xs text-emerald-400 font-semibold">{dsaStats.percentage}% progress</span>
                  </div>
                  <div className="bg-slate-950/40 p-4 rounded-xl border border-white/5">
                    <span className="text-xs text-slate-400 font-medium">Mock Audits</span>
                    <h4 className="text-xl font-bold text-slate-100 mt-1">{interviewStats.count} Rounds</h4>
                    <span className="text-xs text-purple-400 font-semibold">Avg Score: {interviewStats.average_score}%</span>
                  </div>
                  <div className="bg-slate-950/40 p-4 rounded-xl border border-white/5">
                    <span className="text-xs text-slate-400 font-medium">Prep Consistency</span>
                    {(() => {
                      const completed = dailyTasks.filter((t: Task) => t.completed).length;
                      const total = dailyTasks.length;
                      const consistency = total > 0 ? Math.round((completed / total) * 100) : 0;
                      return (
                        <>
                          <h4 className="text-xl font-bold text-slate-100 mt-1">{consistency}%</h4>
                          <span className="text-xs text-pink-400 font-semibold">Today's checklist</span>
                        </>
                      );
                    })()}
                  </div>
                </div>
              </GlassCard>
            </div>
          </div>
        )}
      </div>

      {/* Config Panel Modal */}
      {showConfig && (
        <div className="fixed inset-0 bg-slate-950/70 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <div className="max-w-3xl w-full max-h-[90vh] overflow-y-auto bg-slate-900 border border-white/10 rounded-2xl p-6 md:p-8 space-y-6 shadow-2xl relative">
            <button
              onClick={() => setShowConfig(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-200 text-lg font-bold"
            >
              ✕
            </button>
            <h3 className="text-2xl font-bold text-slate-100 flex items-center space-x-2">
              <Zap className="w-5 h-5 text-blue-400" />
              <span>Twin Configuration Panel</span>
            </h3>
            
            <form onSubmit={handleSaveProfile} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Full Name</label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                    placeholder="e.g. John Doe"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Career Goals / Job Role</label>
                  <input
                    type="text"
                    required
                    value={careerGoals}
                    onChange={(e) => setCareerGoals(e.target.value)}
                    className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                    placeholder="e.g. Software Engineer"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Target Companies (comma-separated)</label>
                <input
                  type="text"
                  value={targetCompanies}
                  onChange={(e) => setTargetCompanies(e.target.value)}
                  className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                  placeholder="e.g. Google, Amazon, Microsoft"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Core Skills (comma-separated)</label>
                <textarea
                  required
                  rows={2}
                  value={skills}
                  onChange={(e) => setSkills(e.target.value)}
                  className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                  placeholder="e.g. Python, Javascript, React, FastAPI, SQL"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Interests / Tech Domains (comma-separated)</label>
                <textarea
                  rows={2}
                  value={interests}
                  onChange={(e) => setInterests(e.target.value)}
                  className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                  placeholder="e.g. Artificial Intelligence, RAG, Web Dev"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Academics & Scores</label>
                <textarea
                  rows={2}
                  value={academicHistory}
                  onChange={(e) => setAcademicHistory(e.target.value)}
                  className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                  placeholder="e.g. CS Major GPA: 3.8/4.0"
                />
              </div>

              <div className="p-4 bg-slate-950/40 rounded-xl border border-white/5 flex items-center justify-between">
                <div>
                  <h5 className="text-sm font-semibold text-slate-200">Upload PDF Resume</h5>
                  <p className="text-slate-400 text-xs mt-0.5">Let Profile Agents audit formatting layout.</p>
                </div>
                <label className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-xl cursor-pointer text-xs font-semibold tracking-wider transition-all">
                  <Upload className="w-3.5 h-3.5" />
                  <span>Choose PDF</span>
                  <input
                    type="file"
                    accept=".pdf"
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setResumeFile(e.target.files[0]);
                      }
                    }}
                  />
                </label>
              </div>

              {resumeFile && (
                <div className="text-xs text-emerald-400 font-semibold">
                  Selected resume: {resumeFile.name}
                </div>
              )}

              <button
                type="submit"
                disabled={configSaving}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-3.5 rounded-xl shadow-lg transition-all"
              >
                {configSaving ? 'Re-compiling Twin Model...' : 'Save & Trigger Agent Audit'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
