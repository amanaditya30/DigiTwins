'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { FileText, Wand2, Sparkles, CheckSquare, AlertTriangle, FileCode } from 'lucide-react';
import { apiGet, apiPost, getToken } from '@/utils/api';
import Sidebar from '@/components/Sidebar';
import GlassCard from '@/components/GlassCard';

export default function ResumeReviewer() {
  const router = useRouter();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  // GenAI tool states
  const [activeTool, setActiveTool] = useState<'cover' | 'linkedin' | 'bullet'>('cover');
  const [jobRole, setJobRole] = useState('Software Engineer');
  const [company, setCompany] = useState('Google');
  const [linkedinTopic, setLinkedinTopic] = useState('FastAPI multi-agent frameworks');
  const [rawBullet, setRawBullet] = useState('I worked on the frontend dashboard and added charts.');
  
  // Output states
  const [output, setOutput] = useState('');
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      router.push('/');
      return;
    }
    fetchStats();
  }, [router]);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const data = await apiGet('/api/dashboard/stats');
      setStats(data);
      if (data.career_goals) {
        setJobRole(data.career_goals);
      }
    } catch (err) {
      console.error('Error fetching resume stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setOutput('');
    try {
      let payload = {};
      if (activeTool === 'cover') {
        payload = { type: 'cover_letter', role: jobRole, company };
      } else if (activeTool === 'linkedin') {
        payload = { type: 'linkedin_post', topic: linkedinTopic };
      } else {
        payload = { type: 'resume_bullet', bullet: rawBullet };
      }

      const res = await apiPost('/api/profile/generate', payload);
      setOutput(res.content);
    } catch (err) {
      setOutput('Generation failed. Ensure API keys are active in the backend.');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-[#090d1a] items-center justify-center">
        <div className="text-slate-400 animate-pulse text-lg flex items-center space-x-2">
          <FileText className="w-6 h-6 animate-pulse text-blue-500" />
          <span>Auditing active resume details...</span>
        </div>
      </div>
    );
  }

  const scoreInfo = stats?.readiness || {};
  const resumeScore = scoreInfo.resume_score || 0;

  return (
    <div className="min-h-screen pl-64 flex bg-[#090d1a] text-slate-100">
      <Sidebar />
      
      <div className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">
            Resume <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Auditor</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">Review ATS compliance scores and generate tailored applications.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: ATS Score & Audits */}
          <div className="lg:col-span-6 flex flex-col space-y-8">
            <GlassCard className="flex flex-col items-center py-8">
              <h3 className="text-slate-300 font-semibold text-base mb-4">ATS Compatibility Rating</h3>
              
              {resumeScore === 0 ? (
                <div className="text-center py-6">
                  <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-3" />
                  <p className="text-slate-300 font-medium">No resume uploaded.</p>
                  <p className="text-slate-500 text-xs mt-1">Go to the Dashboard page and upload your resume PDF to trigger ATS grading.</p>
                </div>
              ) : (
                <>
                  <div className={`text-6xl font-black ${
                    resumeScore >= 80 ? 'text-emerald-400' : resumeScore >= 65 ? 'text-amber-400' : 'text-red-400'
                  }`}>
                    {resumeScore}%
                  </div>
                  <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider mt-2">
                    {resumeScore >= 80 ? 'Excellent Layout & Wording' : resumeScore >= 65 ? 'Good Start, Needs Fine-Tuning' : 'Requires Re-formatting'}
                  </div>

                  <div className="border-t border-white/5 w-full mt-6 pt-6 space-y-4">
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Strengths Highlighted</h4>
                      <ul className="text-xs text-slate-300 space-y-1">
                        <li className="flex items-center space-x-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                          <span>Clean layout design & readable header spacing</span>
                        </li>
                        <li className="flex items-center space-x-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                          <span>Clear technical sections (Languages, Databases, Frameworks)</span>
                        </li>
                      </ul>
                    </div>

                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Actionable Improvements</h4>
                      <ul className="text-xs text-slate-300 space-y-1">
                        <li className="flex items-center space-x-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                          <span>Add action verbs to start project descriptions</span>
                        </li>
                        <li className="flex items-center space-x-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                          <span>Quantify business metrics (e.g. increase performance by 15%)</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </>
              )}
            </GlassCard>
          </div>

          {/* Right Column: GenAI Tools */}
          <div className="lg:col-span-6">
            <GlassCard className="h-full flex flex-col">
              <h3 className="text-slate-300 font-semibold text-base mb-4 flex items-center space-x-2">
                <Wand2 className="w-4 h-4 text-purple-400" />
                <span>🛠️ GenAI Application Copilot</span>
              </h3>

              {/* Tool selector tabs */}
              <div className="flex bg-slate-950/40 p-1 rounded-xl border border-white/5 mb-6">
                <button
                  onClick={() => { setActiveTool('cover'); setOutput(''); }}
                  className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                    activeTool === 'cover' ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Cover Letter
                </button>
                <button
                  onClick={() => { setActiveTool('linkedin'); setOutput(''); }}
                  className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                    activeTool === 'linkedin' ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  LinkedIn Post
                </button>
                <button
                  onClick={() => { setActiveTool('bullet'); setOutput(''); }}
                  className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                    activeTool === 'bullet' ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Optimize Bullet
                </button>
              </div>

              {/* Form Inputs */}
              <div className="space-y-4 flex-1">
                {activeTool === 'cover' && (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Target Role</label>
                      <input
                        type="text"
                        value={jobRole}
                        onChange={(e) => setJobRole(e.target.value)}
                        className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-2.5 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Target Company</label>
                      <input
                        type="text"
                        value={company}
                        onChange={(e) => setCompany(e.target.value)}
                        className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-2.5 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                      />
                    </div>
                  </div>
                )}

                {activeTool === 'linkedin' && (
                  <div>
                    <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Topic / Achievement</label>
                    <input
                      type="text"
                      value={linkedinTopic}
                      onChange={(e) => setLinkedinTopic(e.target.value)}
                      className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-2.5 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                    />
                  </div>
                )}

                {activeTool === 'bullet' && (
                  <div>
                    <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Raw Project Bullet</label>
                    <textarea
                      rows={3}
                      value={rawBullet}
                      onChange={(e) => setRawBullet(e.target.value)}
                      className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-2.5 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                    />
                  </div>
                )}

                <button
                  onClick={handleGenerate}
                  disabled={generating}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-50 text-white font-bold py-3 rounded-xl text-sm shadow-md transition-all flex items-center justify-center space-x-2"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>{generating ? 'Drafting content...' : 'Generate Material'}</span>
                </button>

                {/* Output Display */}
                {output && (
                  <div className="mt-4 border-t border-white/5 pt-4">
                    <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                      <FileCode className="w-3.5 h-3.5 text-blue-400" />
                      <span>Generated Text Output</span>
                    </h5>
                    <textarea
                      readOnly
                      rows={8}
                      value={output}
                      className="w-full bg-slate-950/80 border border-white/10 rounded-xl p-4 text-slate-200 text-sm focus:outline-none font-mono"
                    />
                  </div>
                )}
              </div>
            </GlassCard>
          </div>
        </div>
      </div>
    </div>
  );
}
