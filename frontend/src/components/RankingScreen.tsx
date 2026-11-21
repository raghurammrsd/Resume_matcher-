import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Search, 
  Filter, 
  ChevronRight, 
  Award, 
  CheckCircle2, 
  AlertCircle, 
  Sliders, 
  Download,
  Eye,
  ArrowUpDown
} from 'lucide-react';
import { Job, MatchResultItem } from '../types';
import { api } from '../api';

interface RankingScreenProps {
  job: Job | null;
  onSelectCandidate: (candidateId: string) => void;
  onNavigate: (tab: 'dashboard' | 'create_job' | 'upload' | 'ranking') => void;
}

export const RankingScreen: React.FC<RankingScreenProps> = ({
  job,
  onSelectCandidate,
  onNavigate,
}) => {
  const [candidates, setCandidates] = useState<MatchResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<'All' | 'Strong' | 'Moderate' | 'Low'>('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<'overall' | 'skills' | 'experience' | 'semantic'>('overall');
  const [sortAsc, setSortAsc] = useState(false);

  const fetchCandidates = async () => {
    if (!job) return;
    setLoading(true);
    try {
      const data = await api.getRankedCandidates(job.id, statusFilter);
      setCandidates(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, [job?.id, statusFilter]);

  if (!job) {
    return (
      <div className="text-center py-20">
        <h2 className="text-xl font-bold text-slate-800">Select a Job Position First</h2>
        <button
          onClick={() => onNavigate('create_job')}
          className="mt-4 px-5 py-2.5 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-700"
        >
          Create Job
        </button>
      </div>
    );
  }

  // Filter by search term
  const filtered = candidates.filter((c) => {
    const term = searchTerm.toLowerCase();
    const nameMatch = c.candidate_name.toLowerCase().includes(term);
    const skillMatch = c.matched_skills.some((s) => s.toLowerCase().includes(term));
    return nameMatch || skillMatch;
  });

  // Sort
  const sorted = [...filtered].sort((a, b) => {
    let valA = a.overall_score;
    let valB = b.overall_score;
    if (sortField === 'skills') { valA = a.skill_score; valB = b.skill_score; }
    if (sortField === 'experience') { valA = a.experience_score; valB = b.experience_score; }
    if (sortField === 'semantic') { valA = a.semantic_score; valB = b.semantic_score; }

    return sortAsc ? valA - valB : valB - valA;
  });

  const toggleSort = (field: 'overall' | 'skills' | 'experience' | 'semantic') => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Candidate Ranking & Intelligence
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Sortable multi-dimensional assessment for <span className="font-semibold text-slate-800">{job.title}</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('upload')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white text-slate-700 border border-slate-300 text-xs font-semibold hover:bg-slate-50 transition"
          >
            Upload More Resumes
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200/80 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search */}
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search candidate name or skill..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-xs rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
          />
        </div>

        {/* Status Filters */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          <span className="text-xs font-semibold text-slate-500 flex items-center gap-1 mr-1">
            <Filter className="w-3.5 h-3.5" /> Tier:
          </span>
          {(['All', 'Strong', 'Moderate', 'Low'] as const).map((tier) => (
            <button
              key={tier}
              onClick={() => setStatusFilter(tier)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                statusFilter === tier
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {tier} {tier === 'Strong' ? '(≥80%)' : tier === 'Moderate' ? '(60-79%)' : tier === 'Low' ? '(<60%)' : ''}
            </button>
          ))}
        </div>
      </div>

      {/* Ranking Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        {sorted.length === 0 ? (
          <div className="text-center py-16">
            <Users className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-sm font-bold text-slate-700">No Candidates Found</h3>
            <p className="text-xs text-slate-400 mt-1">Upload resumes or adjust search filters to view ranked candidates.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider">
                  <th className="py-3.5 px-4 w-12 text-center">Rank</th>
                  <th className="py-3.5 px-4">Candidate Profile</th>
                  <th className="py-3.5 px-4 cursor-pointer select-none" onClick={() => toggleSort('overall')}>
                    <div className="flex items-center gap-1 hover:text-indigo-600">
                      <span>Overall Match</span>
                      <ArrowUpDown className="w-3.5 h-3.5" />
                    </div>
                  </th>
                  <th className="py-3.5 px-4 cursor-pointer select-none" onClick={() => toggleSort('skills')}>
                    <div className="flex items-center gap-1 hover:text-indigo-600">
                      <span>Skills (35%)</span>
                      <ArrowUpDown className="w-3.5 h-3.5" />
                    </div>
                  </th>
                  <th className="py-3.5 px-4 cursor-pointer select-none" onClick={() => toggleSort('semantic')}>
                    <div className="flex items-center gap-1 hover:text-indigo-600">
                      <span>Semantic (25%)</span>
                      <ArrowUpDown className="w-3.5 h-3.5" />
                    </div>
                  </th>
                  <th className="py-3.5 px-4 cursor-pointer select-none" onClick={() => toggleSort('experience')}>
                    <div className="flex items-center gap-1 hover:text-indigo-600">
                      <span>Experience (20%)</span>
                      <ArrowUpDown className="w-3.5 h-3.5" />
                    </div>
                  </th>
                  <th className="py-3.5 px-4">Skill Alignment</th>
                  <th className="py-3.5 px-4 text-right">Evidence Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {sorted.map((c, index) => {
                  const isStrong = c.overall_score >= 80;
                  const isMod = c.overall_score >= 60 && c.overall_score < 80;

                  return (
                    <tr
                      key={c.id}
                      onClick={() => onSelectCandidate(c.candidate_id)}
                      className="hover:bg-slate-50/80 transition cursor-pointer group"
                    >
                      {/* Rank */}
                      <td className="py-4 px-4 text-center">
                        <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full font-bold text-xs ${
                          index === 0
                            ? 'bg-amber-100 text-amber-900 border border-amber-300'
                            : index === 1
                            ? 'bg-slate-200 text-slate-800'
                            : index === 2
                            ? 'bg-orange-100 text-orange-800'
                            : 'bg-slate-100 text-slate-600'
                        }`}>
                          #{index + 1}
                        </span>
                      </td>

                      {/* Name */}
                      <td className="py-4 px-4">
                        <div className="font-bold text-sm text-slate-900 group-hover:text-indigo-600 transition">
                          {c.candidate_name}
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">
                          ID: {c.candidate_id.slice(0, 8)}
                        </div>
                      </td>

                      {/* Overall Score */}
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <span className={`text-base font-extrabold ${
                            isStrong ? 'text-emerald-600' : isMod ? 'text-amber-600' : 'text-slate-600'
                          }`}>
                            {c.overall_score}%
                          </span>
                          <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                            isStrong
                              ? 'bg-emerald-100 text-emerald-800'
                              : isMod
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-slate-100 text-slate-600'
                          }`}>
                            {c.status_label}
                          </span>
                        </div>
                      </td>

                      {/* Technical Skills Score */}
                      <td className="py-4 px-4">
                        <div className="font-semibold text-slate-800">{c.skill_score}%</div>
                        <div className="w-16 bg-slate-100 rounded-full h-1 mt-1">
                          <div className="bg-indigo-600 h-1 rounded-full" style={{ width: `${c.skill_score}%` }} />
                        </div>
                      </td>

                      {/* Semantic Score */}
                      <td className="py-4 px-4">
                        <div className="font-semibold text-slate-800">{c.semantic_score}%</div>
                        <div className="w-16 bg-slate-100 rounded-full h-1 mt-1">
                          <div className="bg-cyan-500 h-1 rounded-full" style={{ width: `${c.semantic_score}%` }} />
                        </div>
                      </td>

                      {/* Experience Score */}
                      <td className="py-4 px-4">
                        <div className="font-semibold text-slate-800">{c.experience_score}%</div>
                        <div className="w-16 bg-slate-100 rounded-full h-1 mt-1">
                          <div className="bg-emerald-500 h-1 rounded-full" style={{ width: `${c.experience_score}%` }} />
                        </div>
                      </td>

                      {/* Skill Tags */}
                      <td className="py-4 px-4 max-w-xs">
                        <div className="flex flex-wrap items-center gap-1">
                          {c.matched_skills.slice(0, 3).map((s) => (
                            <span key={s} className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                              ✓ {s}
                            </span>
                          ))}
                          {c.missing_skills.slice(0, 1).map((s) => (
                            <span key={s} className="px-2 py-0.5 rounded text-[10px] font-semibold bg-red-50 text-red-600 border border-red-200">
                              ✗ {s}
                            </span>
                          ))}
                          {c.matched_skills.length > 3 && (
                            <span className="text-[10px] text-slate-400">+{c.matched_skills.length - 3}</span>
                          )}
                        </div>
                      </td>

                      {/* Action */}
                      <td className="py-4 px-4 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectCandidate(c.candidate_id);
                          }}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-700 text-xs font-semibold hover:bg-indigo-100 transition"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          Inspect Evidence
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
