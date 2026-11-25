'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Mic, 
  Send, 
  Play, 
  CheckCircle, 
  MessageSquare, 
  Loader2, 
  Award, 
  Sparkles, 
  History, 
  CheckCircle2, 
  AlertCircle,
  HelpCircle,
  ThumbsUp,
  ThumbsDown,
  User,
  ArrowRight,
  TrendingUp,
  Activity
} from 'lucide-react';
import { apiGet, apiPost, getToken } from '@/utils/api';
import Sidebar from '@/components/Sidebar';
import GlassCard from '@/components/GlassCard';

interface Interview {
  id: number;
  job_role: string;
  interview_type: string;
  score: number;
  feedback: {
    strengths?: string[];
    weaknesses?: string[];
    suggestions?: string[];
  };
  transcript: { speaker: string; text: string }[];
  created_at: string;
}

export default function MockInterviewPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [activeInterview, setActiveInterview] = useState<Interview | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [studentAnswer, setStudentAnswer] = useState('');
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState(false);
  const [isStartingInterview, setIsStartingInterview] = useState(false);
  const [isFinishing, setIsFinishing] = useState(false);
  
  // Setup Form States
  const [jobRole, setJobRole] = useState('Software Engineer');
  const [interviewType, setInterviewType] = useState('Technical');
  
  // Feedback states for current turn
  const [lastFeedback, setLastFeedback] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  // Active view: 'list' | 'session' | 'report'
  const [viewMode, setViewMode] = useState<'list' | 'session' | 'report'>('list');
  const [reportedInterview, setReportedInterview] = useState<Interview | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push('/');
      return;
    }
    fetchInterviews();
  }, [router]);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [activeInterview?.transcript]);

  const fetchInterviews = async () => {
    setLoading(true);
    try {
      const data = await apiGet('/api/interview');
      // Sort interviews by date (latest first)
      const sorted = data.sort((a: Interview, b: Interview) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setInterviews(sorted);
    } catch (err) {
      console.error('Error fetching interviews:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartInterview = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsStartingInterview(true);
    try {
      const res = await apiPost('/api/interview/start', {
        job_role: jobRole,
        interview_type: interviewType
      });
      
      // The start endpoint returns {"interview_id": number, "question": string}
      // Let's fetch the new interview object to populate transcript and details
      const allData = await apiGet('/api/interview');
      const newlyCreated = allData.find((inv: Interview) => inv.id === res.interview_id);
      
      if (newlyCreated) {
        setActiveInterview(newlyCreated);
        setCurrentQuestion(res.question);
        setLastFeedback('');
        setIsComplete(false);
        setViewMode('session');
      } else {
        alert('Failed to initialize active interview object.');
      }
    } catch (err) {
      console.error('Failed to start interview:', err);
      alert('Error initializing interview. Please configure your profile first.');
    } finally {
      setIsStartingInterview(false);
    }
  };

  const handleSubmitAnswer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!studentAnswer.trim() || !activeInterview) return;

    setIsSubmittingAnswer(true);
    try {
      const res = await apiPost(`/api/interview/${activeInterview.id}/answer`, {
        answer: studentAnswer
      });

      // Response contains: {"feedback": string, "next_question": string, "is_complete": boolean}
      setLastFeedback(res.feedback);
      setCurrentQuestion(res.next_question);
      setIsComplete(res.is_complete);

      // Add student answer and interviewer's next turn to local transcript state
      const updatedTranscript = [
        ...activeInterview.transcript,
        { speaker: 'Student', text: studentAnswer },
        { speaker: 'Interviewer', text: res.next_question }
      ];

      setActiveInterview(prev => prev ? {
        ...prev,
        transcript: updatedTranscript
      } : null);

      setStudentAnswer('');
    } catch (err) {
      console.error('Failed to submit answer:', err);
      alert('Error submitting answer.');
    } finally {
      setIsSubmittingAnswer(false);
    }
  };

  const handleFinishInterview = async () => {
    if (!activeInterview) return;
    setIsFinishing(true);
    try {
      const finishedInterview = await apiPost(`/api/interview/${activeInterview.id}/finish`);
      setReportedInterview(finishedInterview);
      setViewMode('report');
      await fetchInterviews();
    } catch (err) {
      console.error('Failed to finish interview:', err);
      alert('Error generating feedback report.');
    } finally {
      setIsFinishing(false);
    }
  };

  const viewReport = (interview: Interview) => {
    setReportedInterview(interview);
    setViewMode('report');
  };

  if (loading && interviews.length === 0) {
    return (
      <div className="flex min-h-screen bg-[#090d1a] items-center justify-center">
        <div className="text-slate-400 animate-pulse text-lg flex items-center space-x-2">
          <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
          <span>Synchronizing Mock Recruiter Agents...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pl-64 flex bg-[#090d1a] text-slate-100">
      <Sidebar />

      <div className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Header */}
        <div className="flex justify-between items-center border-b border-white/5 pb-6">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">
              Mock <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Interview Coach</span>
            </h1>
            <p className="text-slate-400 text-sm mt-1">Practice realistic behavioral and technical mock trials run by Autonomous HR Agents.</p>
          </div>
          {viewMode !== 'list' && (
            <button
              onClick={() => {
                setViewMode('list');
                setActiveInterview(null);
                setReportedInterview(null);
              }}
              className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-2 rounded-xl text-xs font-semibold tracking-wider transition-all"
            >
              Back to Overview
            </button>
          )}
        </div>

        {/* VIEW 1: Overview and Start Interview */}
        {viewMode === 'list' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Start Panel */}
            <div className="lg:col-span-5">
              <GlassCard className="h-full border border-blue-500/10 flex flex-col justify-between">
                <div>
                  <div className="flex items-center space-x-2 text-blue-400 mb-4">
                    <Sparkles className="w-5 h-5" />
                    <h3 className="font-bold text-lg text-slate-200">Start New Mock Round</h3>
                  </div>
                  <p className="text-slate-400 text-xs leading-relaxed mb-6">
                    Our AI Recruiter checks your profile, skills, and target companies to frame custom questions. The RAG engine injects actual concepts from company-specific study materials.
                  </p>
                  
                  <form onSubmit={handleStartInterview} className="space-y-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Target Job Role</label>
                      <input
                        type="text"
                        value={jobRole}
                        onChange={(e) => setJobRole(e.target.value)}
                        className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                        placeholder="e.g. Software Engineer, Data Scientist"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Interview Domain</label>
                      <select
                        value={interviewType}
                        onChange={(e) => setInterviewType(e.target.value)}
                        className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                      >
                        <option value="Technical">Technical (Coding & CS Fundamentals)</option>
                        <option value="Behavioral">Behavioral (HR & Leadership principles)</option>
                        <option value="System Design">System Design (Scalability & Architecture)</option>
                        <option value="General Placement">General Placement (Aptitude & Project QA)</option>
                      </select>
                    </div>
                    <button
                      type="submit"
                      disabled={isStartingInterview}
                      className="w-full mt-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-blue-600/10 flex items-center justify-center space-x-2 transition-all hover:-translate-y-0.5"
                    >
                      {isStartingInterview ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>Generating Questions...</span>
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4 fill-white" />
                          <span>Begin Live Simulation</span>
                        </>
                      )}
                    </button>
                  </form>
                </div>

                <div className="mt-8 pt-6 border-t border-white/5 flex items-center space-x-3 text-slate-500 text-xs">
                  <Activity className="w-4 h-4 text-emerald-500" />
                  <span>AI evaluator checks answers in real time</span>
                </div>
              </GlassCard>
            </div>

            {/* Previous History List */}
            <div className="lg:col-span-7 space-y-4">
              <div className="flex items-center space-x-2 text-slate-300 font-semibold mb-2">
                <History className="w-4 h-4 text-purple-400" />
                <span>Interview History & Analytics</span>
              </div>

              {interviews.length === 0 ? (
                <GlassCard className="text-center py-12 text-slate-500 text-sm border border-dashed border-white/5">
                  No mock interviews found. Start your first session on the left panel!
                </GlassCard>
              ) : (
                <div className="space-y-4 max-h-[550px] overflow-y-auto pr-2">
                  {interviews.map((interview) => (
                    <GlassCard 
                      key={interview.id} 
                      className="flex items-center justify-between border border-white/5 hover:border-blue-500/20 hover:bg-slate-900/50 transition-all cursor-pointer p-4"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-bold text-slate-200">{interview.job_role}</span>
                          <span className="text-xs bg-slate-800 text-blue-400 px-2 py-0.5 rounded-md font-medium">
                            {interview.interview_type}
                          </span>
                        </div>
                        <p className="text-slate-500 text-xs">
                          {new Date(interview.created_at).toLocaleDateString(undefined, { 
                            year: 'numeric', 
                            month: 'short', 
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>

                      <div className="flex items-center space-x-6">
                        <div className="text-right">
                          <span className="text-xs text-slate-400 font-medium uppercase tracking-wider block">Score</span>
                          <span className={`text-xl font-extrabold ${
                            interview.score >= 80 ? 'text-emerald-400' : interview.score >= 60 ? 'text-amber-400' : 'text-red-400'
                          }`}>
                            {interview.score}%
                          </span>
                        </div>
                        <button
                          onClick={() => viewReport(interview)}
                          className="bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 border border-blue-500/20 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all"
                        >
                          View Analytics
                        </button>
                      </div>
                    </GlassCard>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* VIEW 2: Active Chat Simulation */}
        {viewMode === 'session' && activeInterview && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left Session Info Panel */}
            <div className="lg:col-span-4">
              <GlassCard className="border border-blue-500/10 space-y-6">
                <div>
                  <h3 className="font-bold text-slate-200 text-lg">Interview Progress</h3>
                  <p className="text-slate-400 text-xs mt-1">Evaluation in progress. Read recruiter prompts carefully.</p>
                </div>

                <div className="space-y-4">
                  <div>
                    <span className="text-xs text-slate-400 font-medium block">Job Role</span>
                    <span className="text-sm font-semibold text-slate-200">{activeInterview.job_role}</span>
                  </div>
                  <div>
                    <span className="text-xs text-slate-400 font-medium block">Evaluation Format</span>
                    <span className="text-xs bg-slate-800 text-blue-400 px-2 py-0.5 rounded-md font-medium inline-block mt-1">
                      {activeInterview.interview_type}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs text-slate-400 font-medium block">Completion Condition</span>
                    <span className="text-xs text-slate-300 block mt-1">Limit 3 turns for instant feedback.</span>
                  </div>
                </div>

                {isComplete && (
                  <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 space-y-3">
                    <div className="flex items-center space-x-2 text-emerald-400 text-sm font-semibold">
                      <CheckCircle className="w-4 h-4" />
                      <span>Round Complete!</span>
                    </div>
                    <p className="text-slate-300 text-xs leading-relaxed">
                      You have completed the mock trial questions. Click the button below to analyze your transcripts and fetch the performance report.
                    </p>
                    <button
                      onClick={handleFinishInterview}
                      disabled={isFinishing}
                      className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold py-2 rounded-xl text-xs transition-all shadow-md flex items-center justify-center space-x-2"
                    >
                      {isFinishing ? (
                        <>
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          <span>Generating Report...</span>
                        </>
                      ) : (
                        <span>Generate Performance Report</span>
                      )}
                    </button>
                  </div>
                )}
              </GlassCard>
            </div>

            {/* Central Chat Interface */}
            <div className="lg:col-span-8 flex flex-col h-[600px]">
              {/* Messages Body */}
              <div className="flex-1 bg-slate-950/40 border border-white/5 rounded-2xl p-6 overflow-y-auto space-y-6 min-h-[400px]">
                {activeInterview.transcript.map((turn, index) => {
                  const isInterviewer = turn.speaker === 'Interviewer';
                  return (
                    <div 
                      key={index}
                      className={`flex ${isInterviewer ? 'justify-start' : 'justify-end'}`}
                    >
                      <div className={`flex items-start space-x-3 max-w-[80%] ${isInterviewer ? '' : 'flex-row-reverse space-x-reverse'}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border ${
                          isInterviewer ? 'bg-blue-600/20 border-blue-500/30 text-blue-400' : 'bg-purple-600/20 border-purple-500/30 text-purple-400'
                        }`}>
                          {isInterviewer ? <Sparkles className="w-4 h-4" /> : <User className="w-4 h-4" />}
                        </div>
                        <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                          isInterviewer 
                            ? 'bg-slate-900/80 text-slate-200 rounded-tl-none border border-white/5 shadow-md' 
                            : 'bg-gradient-to-r from-blue-600 to-purple-600 text-slate-100 rounded-tr-none shadow-md shadow-blue-500/5'
                        }`}>
                          <p>{turn.text}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}

                {/* Show thinking state while waiting for agent answer */}
                {isSubmittingAnswer && (
                  <div className="flex justify-start">
                    <div className="flex items-start space-x-3 max-w-[80%]">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 bg-blue-600/20 border border-blue-500/30 text-blue-400">
                        <Loader2 className="w-4 h-4 animate-spin" />
                      </div>
                      <div className="p-4 rounded-2xl bg-slate-900/80 border border-white/5 text-slate-400 text-sm rounded-tl-none flex items-center space-x-2">
                        <span>AI Recruiter evaluating response...</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Local alert with feedback from last question */}
                {lastFeedback && !isSubmittingAnswer && (
                  <div className="bg-blue-500/5 border border-blue-500/10 rounded-xl p-4 flex items-start space-x-3">
                    <AlertCircle className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="text-xs text-blue-400 font-bold uppercase tracking-wider block">Live Feedback</span>
                      <p className="text-xs text-slate-300 mt-1 leading-relaxed">{lastFeedback}</p>
                    </div>
                  </div>
                )}

                <div ref={chatEndRef} />
              </div>

              {/* Chat Input */}
              {!isComplete && (
                <form onSubmit={handleSubmitAnswer} className="mt-4 flex items-center space-x-3">
                  <input
                    type="text"
                    disabled={isSubmittingAnswer}
                    value={studentAnswer}
                    onChange={(e) => setStudentAnswer(e.target.value)}
                    className="flex-1 bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3.5 text-slate-200 text-sm focus:outline-none focus:border-blue-500 disabled:opacity-50"
                    placeholder="Type your structured professional answer..."
                    required
                  />
                  <button
                    type="submit"
                    disabled={isSubmittingAnswer || !studentAnswer.trim()}
                    className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600 text-white p-3.5 rounded-xl transition-all shadow-md shadow-blue-500/10 flex items-center justify-center"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </form>
              )}
            </div>
          </div>
        )}

        {/* VIEW 3: Final Analytics Report */}
        {viewMode === 'report' && reportedInterview && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left Overview Stats */}
            <div className="lg:col-span-4 space-y-6">
              <GlassCard className="border border-blue-500/10 flex flex-col items-center py-8">
                <Award className="w-12 h-12 text-yellow-400 mb-3 animate-pulse" />
                <h3 className="text-slate-300 font-semibold text-base">Round Overall Rating</h3>
                <div className={`text-6xl font-black mt-2 ${
                  reportedInterview.score >= 80 ? 'text-emerald-400' : reportedInterview.score >= 60 ? 'text-amber-400' : 'text-red-400'
                }`}>
                  {reportedInterview.score}%
                </div>
                <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider mt-2">
                  {reportedInterview.score >= 80 ? 'Placement Quality' : reportedInterview.score >= 60 ? 'Competitive Standard' : 'Requires Training'}
                </div>
              </GlassCard>

              <GlassCard className="space-y-4">
                <h4 className="font-bold text-slate-200 text-sm">Session Meta</h4>
                <div className="space-y-2.5 text-xs text-slate-400">
                  <div className="flex justify-between">
                    <span>Target Role:</span>
                    <span className="font-semibold text-slate-300">{reportedInterview.job_role}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Interview Format:</span>
                    <span className="font-semibold text-slate-300">{reportedInterview.interview_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Completed On:</span>
                    <span className="font-semibold text-slate-300">
                      {new Date(reportedInterview.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </GlassCard>
            </div>

            {/* Right Detailed Analysis */}
            <div className="lg:col-span-8 space-y-6">
              <GlassCard className="space-y-6">
                <div>
                  <h3 className="text-xl font-bold text-slate-200">Autonomous HR Evaluation</h3>
                  <p className="text-slate-400 text-xs mt-1">Detailed review compiled by the Placement Twin Analysis Agents.</p>
                </div>

                {/* Strengths */}
                <div className="space-y-3">
                  <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center space-x-2">
                    <ThumbsUp className="w-3.5 h-3.5" />
                    <span>Key Strengths Identified</span>
                  </h4>
                  <ul className="space-y-2">
                    {reportedInterview.feedback?.strengths?.map((str, idx) => (
                      <li key={idx} className="text-slate-300 text-sm flex items-start space-x-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                        <span>{str}</span>
                      </li>
                    )) || <li className="text-slate-500 text-xs">No feedback structured.</li>}
                  </ul>
                </div>

                {/* Weaknesses */}
                <div className="space-y-3">
                  <h4 className="text-xs font-semibold text-rose-400 uppercase tracking-wider flex items-center space-x-2">
                    <ThumbsDown className="w-3.5 h-3.5" />
                    <span>Areas of Improvement</span>
                  </h4>
                  <ul className="space-y-2">
                    {reportedInterview.feedback?.weaknesses?.map((weak, idx) => (
                      <li key={idx} className="text-slate-300 text-sm flex items-start space-x-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-1.5 shrink-0" />
                        <span>{weak}</span>
                      </li>
                    )) || <li className="text-slate-500 text-xs">No improvements listed.</li>}
                  </ul>
                </div>

                {/* Suggestions */}
                <div className="space-y-3 pt-4 border-t border-white/5">
                  <h4 className="text-xs font-semibold text-blue-400 uppercase tracking-wider flex items-center space-x-2">
                    <HelpCircle className="w-3.5 h-3.5" />
                    <span>Concrete Preparation Guidance</span>
                  </h4>
                  <ul className="space-y-2">
                    {reportedInterview.feedback?.suggestions?.map((sug, idx) => (
                      <li key={idx} className="text-slate-300 text-sm flex items-start space-x-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 shrink-0" />
                        <span>{sug}</span>
                      </li>
                    )) || <li className="text-slate-500 text-xs">No preparation guidance specified.</li>}
                  </ul>
                </div>
              </GlassCard>

              {/* View Conversation transcript */}
              <GlassCard className="space-y-4">
                <h4 className="font-bold text-slate-200 text-sm flex items-center space-x-2">
                  <MessageSquare className="w-4 h-4 text-purple-400" />
                  <span>Full Session Transcript Review</span>
                </h4>
                <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2">
                  {reportedInterview.transcript.map((turn, index) => {
                    const isInterviewer = turn.speaker === 'Interviewer';
                    return (
                      <div key={index} className="space-y-1">
                        <span className={`text-xs font-semibold uppercase tracking-wider ${
                          isInterviewer ? 'text-blue-400' : 'text-purple-400'
                        }`}>
                          {turn.speaker}
                        </span>
                        <p className="text-slate-300 text-sm leading-relaxed bg-slate-950/20 border border-white/5 rounded-xl p-3.5">
                          {turn.text}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </GlassCard>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
