'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  CheckSquare, 
  Loader2, 
  Award, 
  HelpCircle, 
  Search,
  CheckCircle,
  XCircle,
  ArrowRight,
  Sparkles,
  Bookmark,
  BookOpen
} from 'lucide-react';
import { apiPost, getToken } from '@/utils/api';
import Sidebar from '@/components/Sidebar';
import GlassCard from '@/components/GlassCard';

interface MatchResult {
  compatibility_score: number;
  matching_skills: string[];
  missing_skills: string[];
  recommendations: string[];
}

export default function JobMatcherPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [jobDescription, setJobDescription] = useState('');
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push('/');
      return;
    }
  }, [router]);

  const handleAnalyzeMatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobDescription.trim()) return;

    setLoading(true);
    try {
      const res = await apiPost('/api/profile/match', {
        job_description: jobDescription
      });
      setMatchResult(res);
    } catch (err) {
      console.error('Error matching job description:', err);
      alert('Failed to analyze job match. Ensure your digital twin profile is configured first!');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/5';
    if (score >= 60) return 'text-amber-400 border-amber-500/30 bg-amber-500/5';
    return 'text-rose-400 border-rose-500/30 bg-rose-500/5';
  };

  return (
    <div className="min-h-screen pl-64 flex bg-[#090d1a] text-slate-100">
      <Sidebar />

      <div className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Header */}
        <div className="flex justify-between items-center border-b border-white/5 pb-6">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">
              Job <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Matcher</span>
            </h1>
            <p className="text-slate-400 text-sm mt-1">Audit job descriptions against your Placement Twin profile to identify gaps and target specific hiring mandates.</p>
          </div>
        </div>

        {/* Content split grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Column: Job Description Submission */}
          <div className="lg:col-span-6">
            <GlassCard className="border border-blue-500/10 space-y-4">
              <div className="flex items-center space-x-2 text-slate-200">
                <Bookmark className="w-5 h-5 text-blue-400" />
                <h3 className="font-bold text-lg">Input Job Mandate</h3>
              </div>
              <p className="text-slate-400 text-xs leading-relaxed">
                Paste the target job description or candidate requirement outline below. The Matching Agent evaluates matching keyword percentages and missing hiring mandates.
              </p>

              <form onSubmit={handleAnalyzeMatch} className="space-y-4 pt-2">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Job Description Text</label>
                  <textarea
                    required
                    rows={12}
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3.5 text-slate-200 text-sm focus:outline-none focus:border-blue-500 leading-relaxed"
                    placeholder="Paste skills requirements, responsibilities, guidelines, target tech stack, etc. from LinkedIn or hiring portals..."
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading || !jobDescription.trim()}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-3.5 rounded-xl shadow-lg transition-all flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Auditing Fit Ratios...</span>
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4" />
                      <span>Evaluate Compatibility Fit</span>
                    </>
                  )}
                </button>
              </form>
            </GlassCard>
          </div>

          {/* Right Column: Match Analysis Results */}
          <div className="lg:col-span-6">
            {matchResult ? (
              <div className="space-y-6">
                
                {/* Score panel */}
                <GlassCard className={`border flex items-center justify-between p-6 ${getScoreColor(matchResult.compatibility_score)}`}>
                  <div className="space-y-1">
                    <h4 className="text-sm font-bold uppercase tracking-wider">Overall Match Rating</h4>
                    <p className="text-xs text-slate-400">
                      {matchResult.compatibility_score >= 85 
                        ? 'Strong compatibility! You have high probability of passing ATS.' 
                        : matchResult.compatibility_score >= 60 
                        ? 'Moderate overlap. Bridge missing requirements to secure interviews.' 
                        : 'Skill gaps detected. Follow agent suggestions before applying.'}
                    </p>
                  </div>
                  <div className="text-4xl font-black shrink-0 px-4 py-2 border rounded-xl border-current font-mono">
                    {matchResult.compatibility_score}%
                  </div>
                </GlassCard>

                {/* Skills tags grid */}
                <GlassCard className="space-y-4">
                  <div>
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Skills Breakdown Analysis</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      
                      {/* Matching Skills */}
                      <div className="space-y-2">
                        <span className="text-xs font-bold text-emerald-400 flex items-center space-x-1">
                          <CheckCircle className="w-3.5 h-3.5" />
                          <span>Matching Core Skills</span>
                        </span>
                        {matchResult.matching_skills.length === 0 ? (
                          <span className="text-xs text-slate-500 block">No matching skills identified.</span>
                        ) : (
                          <div className="flex flex-wrap gap-1.5 pt-1">
                            {matchResult.matching_skills.map((skill, idx) => (
                              <span 
                                key={idx} 
                                className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-xs font-medium"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Missing Skills */}
                      <div className="space-y-2">
                        <span className="text-xs font-bold text-rose-400 flex items-center space-x-1">
                          <XCircle className="w-3.5 h-3.5" />
                          <span>Missing Core Skills</span>
                        </span>
                        {matchResult.missing_skills.length === 0 ? (
                          <span className="text-xs text-emerald-400 block">No critical skill gaps!</span>
                        ) : (
                          <div className="flex flex-wrap gap-1.5 pt-1">
                            {matchResult.missing_skills.map((skill, idx) => (
                              <span 
                                key={idx} 
                                className="bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded text-xs font-medium"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                    </div>
                  </div>
                </GlassCard>

                {/* Recommendations */}
                <GlassCard className="space-y-4">
                  <h4 className="text-xs font-semibold text-blue-400 uppercase tracking-wider flex items-center space-x-2">
                    <BookOpen className="w-4 h-4" />
                    <span>How to bridge gaps & optimize applications</span>
                  </h4>
                  <ul className="space-y-3">
                    {matchResult.recommendations.map((rec, idx) => (
                      <li key={idx} className="text-slate-300 text-sm flex items-start space-x-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </GlassCard>

              </div>
            ) : (
              <GlassCard className="h-64 flex flex-col items-center justify-center text-slate-500 text-sm border border-dashed border-white/5">
                <Sparkles className="w-8 h-8 text-slate-600 mb-3 animate-pulse" />
                <span>Submit job details on the left. AI will analyze compatibility stats and recommendations here.</span>
              </GlassCard>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
