'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Code, 
  Plus, 
  Loader2, 
  Award, 
  HelpCircle, 
  Lightbulb, 
  ArrowUpRight,
  BookOpen,
  Terminal,
  Activity,
  Layers,
  Sparkles
} from 'lucide-react';
import { apiGet, apiPost, getToken } from '@/utils/api';
import Sidebar from '@/components/Sidebar';
import GlassCard from '@/components/GlassCard';

const GithubIcon = ({ className = "w-4 h-4" }: { className?: string }) => (
  <svg 
    className={className} 
    fill="currentColor" 
    viewBox="0 0 24 24" 
    aria-hidden="true"
  >
    <path 
      fillRule="evenodd" 
      d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.137 20.162 22 16.418 22 12c0-5.523-4.477-10-10-10z" 
      clipRule="evenodd" 
    />
  </svg>
);

interface Project {
  id: number;
  title: string;
  description: string;
  repo_url?: string;
  score: number;
  suggestions: string[];
  interview_questions: string[];
}

export default function ProjectsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  
  // Create Form States
  const [showAddForm, setShowAddForm] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [repoUrl, setRepoUrl] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      router.push('/');
      return;
    }
    fetchProjects();
  }, [router]);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const data = await apiGet('/api/projects');
      setProjects(data);
      if (data.length > 0) {
        setSelectedProject(data[0]);
      }
    } catch (err) {
      console.error('Error fetching projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) return;

    setIsSubmitting(true);
    try {
      const newProj = await apiPost('/api/projects', {
        title,
        description,
        repo_url: repoUrl || undefined
      });
      
      setProjects(prev => [...prev, newProj]);
      setSelectedProject(newProj);
      setShowAddForm(false);
      setTitle('');
      setDescription('');
      setRepoUrl('');
    } catch (err) {
      console.error('Error auditing project:', err);
      alert('Failed to audit project. Please check if your profile has been configured.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading && projects.length === 0) {
    return (
      <div className="flex min-h-screen bg-[#090d1a] items-center justify-center">
        <div className="text-slate-400 animate-pulse text-lg flex items-center space-x-2">
          <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
          <span>Synchronizing Project Audit Agents...</span>
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
              Project <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Auditor</span>
            </h1>
            <p className="text-slate-400 text-sm mt-1">Submit project details and repositories to audit tech stacks, architectures, and prepare defense questions.</p>
          </div>
          <button
            onClick={() => setShowAddForm(true)}
            className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 px-5 py-2.5 rounded-xl font-semibold text-sm shadow-lg shadow-blue-600/10 hover:-translate-y-0.5 transition-all duration-200"
          >
            <Plus className="w-4 h-4" />
            <span>Audit New Project</span>
          </button>
        </div>

        {/* Dashboard Content Split */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Column: Projects List */}
          <div className="lg:col-span-4 space-y-4">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-2">
              <Layers className="w-3.5 h-3.5 text-blue-400" />
              <span>Audited Projects List</span>
            </h3>

            {projects.length === 0 ? (
              <GlassCard className="text-center py-12 text-slate-500 text-sm border border-dashed border-white/5">
                No projects audited yet. Tap the button above to begin!
              </GlassCard>
            ) : (
              <div className="space-y-3">
                {projects.map((proj) => (
                  <div
                    key={proj.id}
                    onClick={() => setSelectedProject(proj)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all duration-200 ${
                      selectedProject?.id === proj.id
                        ? 'bg-gradient-to-r from-blue-600/20 to-purple-600/20 text-blue-400 border-blue-500/30'
                        : 'bg-slate-900/40 border-white/5 text-slate-300 hover:bg-slate-900/60'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <span className="font-bold text-sm block truncate max-w-[70%]">{proj.title}</span>
                      <span className={`text-xs px-2 py-0.5 rounded font-bold ${
                        proj.score >= 80 ? 'bg-emerald-500/10 text-emerald-400' : proj.score >= 60 ? 'bg-amber-500/10 text-amber-400' : 'bg-rose-500/10 text-rose-400'
                      }`}>
                        {proj.score}%
                      </span>
                    </div>
                    {proj.repo_url && (
                      <div className="flex items-center space-x-1.5 text-slate-500 text-xs mt-2">
                        <GithubIcon className="w-3 h-3" />
                        <span className="truncate max-w-[80%]">{proj.repo_url}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right Column: Detailed Audit Report */}
          <div className="lg:col-span-8">
            {selectedProject ? (
              <div className="space-y-6">
                
                {/* Score & Info Card */}
                <GlassCard className="border border-blue-500/10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                  <div>
                    <h2 className="text-2xl font-bold text-slate-100 flex items-center space-x-2">
                      <span>{selectedProject.title}</span>
                      {selectedProject.repo_url && (
                        <a 
                          href={selectedProject.repo_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-slate-400 hover:text-slate-200 inline-block p-1"
                        >
                          <ArrowUpRight className="w-4 h-4" />
                        </a>
                      )}
                    </h2>
                    <p className="text-slate-400 text-xs mt-2 max-w-xl leading-relaxed">
                      {selectedProject.description}
                    </p>
                  </div>

                  <div className="bg-slate-950/40 p-4 rounded-2xl border border-white/5 flex flex-col items-center shrink-0 w-full md:w-32 py-6">
                    <span className="text-xs text-slate-400 font-medium">Twin Score</span>
                    <span className={`text-3xl font-black mt-1 ${
                      selectedProject.score >= 80 ? 'text-emerald-400' : selectedProject.score >= 60 ? 'text-amber-400' : 'text-rose-400'
                    }`}>
                      {selectedProject.score}%
                    </span>
                    <span className="text-[10px] text-slate-500 uppercase tracking-widest mt-1.5 font-bold">
                      {selectedProject.score >= 80 ? 'Production' : selectedProject.score >= 60 ? 'Competitive' : 'Basic'}
                    </span>
                  </div>
                </GlassCard>

                {/* Audit Suggestions */}
                <GlassCard className="space-y-4">
                  <h3 className="text-xs font-semibold text-blue-400 uppercase tracking-wider flex items-center space-x-2">
                    <Lightbulb className="w-4 h-4" />
                    <span>Architectural suggestions & optimization tips</span>
                  </h3>
                  <ul className="space-y-3">
                    {selectedProject.suggestions.map((sug, idx) => (
                      <li key={idx} className="text-slate-300 text-sm flex items-start space-x-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />
                        <span>{sug}</span>
                      </li>
                    ))}
                  </ul>
                </GlassCard>

                {/* Interview Prep Questions */}
                <GlassCard className="space-y-4">
                  <h3 className="text-xs font-semibold text-purple-400 uppercase tracking-wider flex items-center space-x-2">
                    <HelpCircle className="w-4 h-4" />
                    <span>Project defense interview questions (Agentic QA)</span>
                  </h3>
                  <div className="space-y-4">
                    {selectedProject.interview_questions.map((quest, idx) => (
                      <div key={idx} className="bg-slate-950/20 border border-white/5 rounded-xl p-4 space-y-1.5">
                        <span className="text-xs text-purple-400 font-bold uppercase tracking-wider">Question {idx + 1}</span>
                        <p className="text-slate-200 text-sm leading-relaxed">{quest}</p>
                      </div>
                    ))}
                  </div>
                </GlassCard>

              </div>
            ) : (
              <GlassCard className="h-64 flex flex-col items-center justify-center text-slate-500 text-sm border border-dashed border-white/5">
                <Terminal className="w-8 h-8 text-slate-600 mb-3" />
                <span>Select a project from the left panel or audit a new one to view report details.</span>
              </GlassCard>
            )}
          </div>
        </div>

        {/* Modal form */}
        {showAddForm && (
          <div className="fixed inset-0 bg-slate-950/70 backdrop-blur-md flex items-center justify-center p-4 z-50">
            <div className="max-w-xl w-full bg-slate-900 border border-white/10 rounded-2xl p-6 md:p-8 space-y-6 shadow-2xl relative">
              <button
                onClick={() => setShowAddForm(false)}
                className="absolute top-4 right-4 text-slate-400 hover:text-slate-200 text-lg font-bold"
              >
                ✕
              </button>
              <h3 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-blue-400" />
                <span>Audit Project Parameters</span>
              </h3>
              
              <form onSubmit={handleEvaluateProject} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Project Title</label>
                  <input
                    type="text"
                    required
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                    placeholder="e.g. Placement Twin AI Portal"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">GitHub Repository URL (Optional)</label>
                  <input
                    type="url"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                    placeholder="e.g. https://github.com/username/project"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Tech Stack & System Description</label>
                  <textarea
                    required
                    rows={4}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-slate-200 text-sm focus:outline-none focus:border-blue-500"
                    placeholder="Describe your tech stack, system architecture, challenges solved, database design, etc."
                  />
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-3.5 rounded-xl shadow-lg transition-all flex items-center justify-center space-x-2"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Auditing Code & Architecture...</span>
                    </>
                  ) : (
                    <span>Audit Project</span>
                  )}
                </button>
              </form>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
