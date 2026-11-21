import React, { useEffect, useState } from 'react';
import { 
  Users, 
  Award, 
  CheckCircle2, 
  Clock, 
  TrendingUp, 
  ArrowRight, 
  UploadCloud, 
  FileText, 
  RotateCw,
  Sliders,
  ShieldCheck
} from 'lucide-react';
import { Job, JobSummary, MatchResultItem } from '../types';
import { api } from '../api';

interface DashboardScreenProps {
  job: Job | null;
  onNavigate: (tab: 'dashboard' | 'create_job' | 'upload' | 'ranking') => void;
  onSelectCandidate: (candidateId: string) => void;
}

export const DashboardScreen: React.FC<DashboardScreenProps> = ({
  job,
  onNavigate,
  onSelectCandidate,
}) => {
  const [summary, setSummary] = useState<JobSummary | null>(null);
  const [topCandidates, setTopCandidates] = useState<MatchResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [reprocessing, setReprocessing] = useState(false);

  const fetchDashboardData = async () => {
    if (!job) return;
    setLoading(true);
    try {
      const [sumData, candidates] = await Promise.all([
        api.getJobSummary(job.id),
        api.getRankedCandidates(job.id),
      ]);
      setSummary(sumData);
      setTopCandidates(candidates.slice(0, 5));
    } catch (err) {
      console.error('Error fetching dashboard summary:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [job?.id]);

  const handleReprocess = async () => {
    if (!job) return;
    setReprocessing(true);
    try {
      await api.reprocessJob(job.id);
      setTimeout(fetchDashboardData, 1000);
    } catch (err) {
      console.error(err);
    } finally {
      setReprocessing(false);
    }
  };

  if (!job) {
    return (
      <div className="text-center py-20">
        <div className="w-16 h-16 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center mx-auto mb-4">
          <FileText className="w-8 h-8 text-indigo-600" />
        </div>
        <h2 className="text-xl font-bold text-slate-800">No Job Selected</h2>
        <p className="text-slate-500 mt-1 mb-6">Create a job description to begin uploading resumes and ranking candidates.</p>
        <button
          onClick={() => onNavigate('create_job')}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition"
        >
          Create New Job
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header Banner */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              Live Analysis
            </span>
            <span className="text-xs text-slate-400 font-medium">Job ID: {job.id.slice(0, 8)}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {job.title}
          </h1>
          <p className="text-slate-500 mt-1 text-sm max-w-2xl line-clamp-2">
            {job.description}
          </p>
          <div className="flex flex-wrap items-center gap-3 mt-4 text-xs text-slate-600 font-medium">
            <span className="bg-slate-100 px-3 py-1 rounded-md">Dept: {job.department}</span>
            <span className="bg-slate-100 px-3 py-1 rounded-md">Location: {job.location}</span>
            <span className="bg-slate-100 px-3 py-1 rounded-md">Min Experience: {job.required_experience_years} years</span>
          </div>
        </div>

        {/* Quick Action Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => onNavigate('upload')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition shadow-sm shadow-indigo-200"
          >
            <UploadCloud className="w-4 h-4" />
            Upload Resumes
          </button>
          <button
            onClick={handleReprocess}
            disabled={reprocessing}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white text-slate-700 border border-slate-300 text-sm font-semibold hover:bg-slate-50 transition"
          >
            <RotateCw className={`w-4 h-4 text-slate-500 ${reprocessing ? 'animate-spin' : ''}`} />
            {reprocessing ? 'Reprocessing...' : 'Re-match'}
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Resumes */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Resumes</span>
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900">{summary?.total_resumes_uploaded || 0}</span>
            <span className="text-xs text-slate-500">processed: {summary?.total_candidates_processed || 0}</span>
          </div>
          <div className="mt-3 text-xs text-emerald-600 font-medium flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Ready for recruiter review</span>
          </div>
        </div>

        {/* Average Match */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Average Match</span>
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900">{summary?.average_match_score || 0}%</span>
            <span className="text-xs text-slate-500">across cohort</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-1.5 mt-3 overflow-hidden">
            <div
              className="bg-emerald-500 h-1.5 rounded-full"
              style={{ width: `${summary?.average_match_score || 0}%` }}
            />
          </div>
        </div>

        {/* Strong Matches */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Strong Matches</span>
            <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <Award className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900">{summary?.strong_matches_count || 0}</span>
            <span className="text-xs text-indigo-600 font-semibold bg-indigo-50 px-2 py-0.5 rounded-full">
              Score ≥ 80%
            </span>
          </div>
          <p className="mt-3 text-xs text-slate-500">High priority shortlist recommendations</p>
        </div>

        {/* Moderate / Pipeline */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Moderate & Other</span>
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900">
              {(summary?.moderate_matches_count || 0) + (summary?.low_matches_count || 0)}
            </span>
            <span className="text-xs text-slate-500">
              ({summary?.moderate_matches_count || 0} mod, {summary?.low_matches_count || 0} low)
            </span>
          </div>
          <p className="mt-3 text-xs text-slate-500">Potential candidates with skill overlaps</p>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Top Candidates Ranking Preview */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Top Matching Candidates</h2>
              <p className="text-xs text-slate-500 mt-0.5">Ranked by explainable multi-dimensional AI scoring</p>
            </div>
            <button
              onClick={() => onNavigate('ranking')}
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 group"
            >
              View Full Table ({topCandidates.length})
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition" />
            </button>
          </div>

          {topCandidates.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-xl">
              <UploadCloud className="w-10 h-10 text-slate-300 mx-auto mb-2" />
              <p className="text-sm font-medium text-slate-600">No candidate results calculated yet</p>
              <p className="text-xs text-slate-400 mt-1">Upload resumes to see automatic AI matching rankings</p>
              <button
                onClick={() => onNavigate('upload')}
                className="mt-4 inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-50 text-indigo-600 text-xs font-semibold hover:bg-indigo-100 transition"
              >
                Upload Candidate Resumes
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {topCandidates.map((c, index) => {
                const isStrong = c.overall_score >= 80;
                const isMod = c.overall_score >= 60 && c.overall_score < 80;
                return (
                  <div
                    key={c.id}
                    onClick={() => onSelectCandidate(c.candidate_id)}
                    className="p-4 rounded-xl border border-slate-200 hover:border-indigo-300 hover:bg-slate-50/70 transition cursor-pointer flex items-center justify-between gap-4 group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-slate-100 text-slate-600 font-bold text-xs flex items-center justify-center">
                        #{index + 1}
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-slate-900 group-hover:text-indigo-600 transition">
                          {c.candidate_name}
                        </h4>
                        <div className="flex flex-wrap items-center gap-1.5 mt-1">
                          {c.matched_skills.slice(0, 3).map((s) => (
                            <span key={s} className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                              {s}
                            </span>
                          ))}
                          {c.missing_skills.length > 0 && (
                            <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-600">
                              Missing: {c.missing_skills[0]}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className="flex items-center gap-1.5 justify-end">
                          <span className={`text-base font-extrabold ${isStrong ? 'text-emerald-600' : isMod ? 'text-amber-600' : 'text-slate-600'}`}>
                            {c.overall_score}%
                          </span>
                          <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                            isStrong ? 'bg-emerald-100 text-emerald-800' : isMod ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-600'
                          }`}>
                            {c.status_label}
                          </span>
                        </div>
                        <span className="text-[11px] text-slate-400">Click for evidence</span>
                      </div>
                      <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600 group-hover:translate-x-0.5 transition" />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right: Scoring Model & Transparency */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Sliders className="w-4 h-4 text-indigo-600" />
              <h3 className="text-sm font-bold text-slate-900">Current Scoring Formula</h3>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Configured weights applied across 5 dimensions:
            </p>

            <div className="space-y-3 text-xs">
              <div>
                <div className="flex justify-between font-medium text-slate-700 mb-1">
                  <span>Technical Skills</span>
                  <span className="font-bold text-slate-900">{Math.round((job.scoring_weights?.weight_skills || 0.35) * 100)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-1.5">
                  <div className="bg-indigo-600 h-1.5 rounded-full" style={{ width: `${(job.scoring_weights?.weight_skills || 0.35) * 100}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-medium text-slate-700 mb-1">
                  <span>Semantic Similarity</span>
                  <span className="font-bold text-slate-900">{Math.round((job.scoring_weights?.weight_semantic || 0.25) * 100)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-1.5">
                  <div className="bg-cyan-500 h-1.5 rounded-full" style={{ width: `${(job.scoring_weights?.weight_semantic || 0.25) * 100}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-medium text-slate-700 mb-1">
                  <span>Relevant Experience</span>
                  <span className="font-bold text-slate-900">{Math.round((job.scoring_weights?.weight_experience || 0.20) * 100)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-1.5">
                  <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${(job.scoring_weights?.weight_experience || 0.20) * 100}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-medium text-slate-700 mb-1">
                  <span>Education & Qualifications</span>
                  <span className="font-bold text-slate-900">{Math.round((job.scoring_weights?.weight_education || 0.10) * 100)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-1.5">
                  <div className="bg-amber-500 h-1.5 rounded-full" style={{ width: `${(job.scoring_weights?.weight_education || 0.10) * 100}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-medium text-slate-700 mb-1">
                  <span>Responsibility Alignment</span>
                  <span className="font-bold text-slate-900">{Math.round((job.scoring_weights?.weight_responsibility || 0.10) * 100)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-1.5">
                  <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: `${(job.scoring_weights?.weight_responsibility || 0.10) * 100}%` }} />
                </div>
              </div>
            </div>
          </div>

          {/* Fairness Notice */}
          <div className="bg-emerald-50/60 rounded-2xl p-5 border border-emerald-200/80">
            <div className="flex items-center gap-2 mb-2">
              <ShieldCheck className="w-4 h-4 text-emerald-700" />
              <h4 className="text-xs font-bold text-emerald-900 uppercase tracking-wider">AI Ethics & Non-Discrimination</h4>
            </div>
            <p className="text-xs text-emerald-800 leading-relaxed">
              TalentMatch AI uses strict non-discriminatory algorithmic scoring. Protected personal characteristics (age, gender, religion, caste, nationality, photos) are excluded from scoring calculations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
