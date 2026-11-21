import React from 'react';
import { Sparkles, LayoutDashboard, FilePlus, UploadCloud, Users, Briefcase } from 'lucide-react';
import { Job } from '../types';

interface NavbarProps {
  currentTab: 'dashboard' | 'create_job' | 'upload' | 'ranking';
  setCurrentTab: (tab: 'dashboard' | 'create_job' | 'upload' | 'ranking') => void;
  jobs: Job[];
  selectedJobId: string;
  setSelectedJobId: (id: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  jobs,
  selectedJobId,
  setSelectedJobId,
}) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-40 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentTab('dashboard')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-200 bg-clip-text text-transparent">
                  TalentMatch AI
                </span>
                <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  v1.0 Pro
                </span>
              </div>
              <p className="text-xs text-slate-400">Intelligent Resume Matching</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            <button
              onClick={() => setCurrentTab('dashboard')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                currentTab === 'dashboard'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </button>

            <button
              onClick={() => setCurrentTab('create_job')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                currentTab === 'create_job'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <FilePlus className="w-4 h-4" />
              Create Job
            </button>

            <button
              onClick={() => setCurrentTab('upload')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                currentTab === 'upload'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <UploadCloud className="w-4 h-4" />
              Upload Resumes
            </button>

            <button
              onClick={() => setCurrentTab('ranking')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                currentTab === 'ranking'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Users className="w-4 h-4" />
              Candidate Ranking
            </button>
          </nav>

          {/* Job Selector Dropdown */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
              <Briefcase className="w-4 h-4 text-indigo-400" />
              <select
                value={selectedJobId}
                onChange={(e) => setSelectedJobId(e.target.value)}
                className="bg-transparent text-sm text-slate-200 font-medium focus:outline-none cursor-pointer max-w-[200px] truncate"
              >
                {jobs.map((j) => (
                  <option key={j.id} value={j.id} className="bg-slate-800 text-white">
                    {j.title}
                  </option>
                ))}
                {jobs.length === 0 && <option value="">No Jobs Created</option>}
              </select>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
