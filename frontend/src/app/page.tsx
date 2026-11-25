'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Sparkles, Brain, CheckSquare, FileText, Mic, Map, ArrowRight } from 'lucide-react';
import { apiLogin, apiPost, setToken, getToken } from '@/utils/api';
import GlassCard from '@/components/GlassCard';

export default function AuthPage() {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Redirect to dashboard if token exists
  useEffect(() => {
    if (getToken()) {
      router.push('/dashboard');
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        const res = await apiLogin(username, password);
        setToken(res.access_token);
        router.push('/dashboard');
      } else {
        const payload = { username, email, password };
        const res = await apiPost('/api/auth/register', payload);
        setToken(res.access_token);
        router.push('/dashboard');
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check inputs.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 md:p-8 bg-[#090d1a]">
      <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Left Side: Pitch Banner */}
        <div className="lg:col-span-7 flex flex-col space-y-6">
          <div className="flex items-center space-x-2 w-fit bg-blue-500/10 border border-blue-500/20 px-3 py-1 rounded-full text-blue-400 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 animate-pulse" />
            <span>Autonomous Career Twin System</span>
          </div>

          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight">
            Meet Your <br />
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Placement Twin
            </span>
          </h1>

          <p className="text-slate-400 text-lg max-w-lg">
            Build a digital replica of your skills, resume, and code repos to receive automated, agentic career guidance and mock assessments.
          </p>

          {/* Features Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4">
            <div className="flex items-start space-x-3">
              <div className="p-2 bg-blue-500/10 border border-blue-500/20 rounded-lg text-blue-400">
                <Brain className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-200 text-sm">LangGraph Multi-Agent Flow</h4>
                <p className="text-slate-400 text-xs mt-0.5">Specialized agents audit roadmaps, projects, and skills in a unified workflow.</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="p-2 bg-purple-500/10 border border-purple-500/20 rounded-lg text-purple-400">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-200 text-sm">ATS Resume Review</h4>
                <p className="text-slate-400 text-xs mt-0.5">Automated scoring audits layout formats, bullet metrics, and flags key gaps.</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="p-2 bg-pink-500/10 border border-pink-500/20 rounded-lg text-pink-400">
                <Mic className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-200 text-sm">Interactive Mock Recruiter</h4>
                <p className="text-slate-400 text-xs mt-0.5">Conduct technical or HR rounds with dynamic turn-based evaluations.</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400">
                <Map className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-200 text-sm">CS Theory RAG System</h4>
                <p className="text-slate-400 text-xs mt-0.5">Embeds your PDF notes in ChromaDB to advice interview practice rounds.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Auth Card */}
        <div className="lg:col-span-5">
          <GlassCard className="border border-white/10 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-32 h-32 bg-blue-500/10 rounded-full blur-2xl pointer-events-none" />

            {/* Selector */}
            <div className="flex bg-slate-950/50 p-1.5 rounded-xl border border-white/5 mb-6">
              <button
                type="button"
                onClick={() => { setIsLogin(true); setError(''); }}
                className={`flex-1 text-center py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${
                  isLogin ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => { setIsLogin(false); setError(''); }}
                className={`flex-1 text-center py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${
                  !isLogin ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Register
              </button>
            </div>

            <h3 className="text-2xl font-bold mb-6 text-slate-100">
              {isLogin ? 'Access Dashboard' : 'Join Placement Twin'}
            </h3>

            {error && (
              <div className="mb-4 p-3 bg-red-500/15 border border-red-500/30 rounded-xl text-red-400 text-xs font-medium">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">Username</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. johndoe"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-sm"
                />
              </div>

              {!isLogin && (
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">Email Address</label>
                  <input
                    type="email"
                    required
                    placeholder="name@domain.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-sm"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">Password</label>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-sm"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-50 text-white py-3.5 rounded-xl font-bold text-sm shadow-lg hover:shadow-blue-500/10 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <span>{loading ? 'Authenticating...' : isLogin ? 'Access Portal' : 'Register Twin'}</span>
                {!loading && <ArrowRight className="w-4 h-4" />}
              </button>
            </form>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
