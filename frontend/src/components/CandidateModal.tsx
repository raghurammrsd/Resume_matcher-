import React, { useEffect, useState } from 'react';
import { 
  X, 
  Award, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  GraduationCap, 
  Briefcase, 
  FileText, 
  ShieldCheck, 
  Sparkles,
  Quote,
  ChevronDown,
  Layers
} from 'lucide-react';
import { CandidateDetailAnalysis } from '../types';
import { api } from '../api';

interface CandidateModalProps {
  candidateId: string | null;
  jobId: string;
  onClose: () => void;
}

export const CandidateModal: React.FC<CandidateModalProps> = ({
  candidateId,
  jobId,
  onClose,
}) => {
  const [data, setData] = useState<CandidateDetailAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'evidence' | 'experience'>('overview');

  useEffect(() => {
    if (!candidateId || !jobId) return;
    setLoading(true);
    api
      .getCandidateExplanation(candidateId, jobId)
      .then((res) => setData(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [candidateId, jobId]);

  if (!candidateId) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 animate-in fade-in duration-150">
      <div 
        className="bg-white w-full max-w-4xl rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-slate-900 text-white p-6 flex items-start justify-between border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                Candidate Intelligence Report
              </span>
              <span className="text-xs text-slate-400">Resume: {data?.resume_filename}</span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight">
              {data ? data.candidate_name : 'Loading Profile...'}
            </h2>
            <div className="flex items-center gap-4 mt-1.5 text-xs text-slate-300">
              {data?.email && <span>{data.email}</span>}
              {data?.phone && <span>• {data.phone}</span>}
            </div>
          </div>

          <div className="flex items-center gap-4">
            {data && (
              <div className="text-right">
                <div className="flex items-center gap-2 justify-end">
                  <span className="text-3xl font-extrabold text-emerald-400">
                    {data.overall_score}%
                  </span>
                  <span className={`text-[11px] font-bold uppercase px-2.5 py-1 rounded-full ${
                    data.overall_score >= 80
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : data.overall_score >= 60
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      : 'bg-slate-500/20 text-slate-300 border border-slate-500/30'
                  }`}>
                    {data.status_label}
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Overall Match Score</span>
              </div>
            )}
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition ml-2"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Navigation Tabs inside Modal */}
        <div className="border-b border-slate-200 bg-slate-50 px-6 flex items-center space-x-6 text-xs font-semibold text-slate-600">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-3.5 border-b-2 transition ${
              activeTab === 'overview'
                ? 'border-indigo-600 text-indigo-600 font-bold'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            Overview & Score Breakdown
          </button>
          <button
            onClick={() => setActiveTab('skills')}
            className={`py-3.5 border-b-2 transition ${
              activeTab === 'skills'
                ? 'border-indigo-600 text-indigo-600 font-bold'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            Technical Skills Taxonomy ({data?.matched_skills.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('experience')}
            className={`py-3.5 border-b-2 transition ${
              activeTab === 'experience'
                ? 'border-indigo-600 text-indigo-600 font-bold'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            Timeline & Experience ({data?.experience_analysis.final_years || 0} yrs)
          </button>
          <button
            onClick={() => setActiveTab('evidence')}
            className={`py-3.5 border-b-2 transition ${
              activeTab === 'evidence'
                ? 'border-indigo-600 text-indigo-600 font-bold'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            Verifiable Excerpts ({data?.evidence_items.length || 0})
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-800 text-sm">
          {loading || !data ? (
            <div className="py-20 text-center text-slate-400">Loading intelligence data...</div>
          ) : (
            <>
              {/* TAB 1: OVERVIEW */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  {/* Why matched vs Areas of concern */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    {/* Why this candidate matched */}
                    <div className="p-5 rounded-2xl bg-emerald-50/70 border border-emerald-200">
                      <div className="flex items-center gap-2 mb-3">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-900">
                          Why This Candidate Matched
                        </h4>
                      </div>
                      <ul className="space-y-2 text-xs text-emerald-800">
                        {data.why_matched.map((item, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-emerald-500 font-bold">•</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Areas of concern */}
                    <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200">
                      <div className="flex items-center gap-2 mb-3">
                        <AlertCircle className="w-4 h-4 text-amber-600" />
                        <h4 className="text-xs font-bold uppercase tracking-wider text-amber-900">
                          Areas of Concern / Gaps
                        </h4>
                      </div>
                      {data.areas_of_concern.length === 0 ? (
                        <p className="text-xs text-amber-700 italic">No significant disqualifying gaps detected.</p>
                      ) : (
                        <ul className="space-y-2 text-xs text-amber-800">
                          {data.areas_of_concern.map((item, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="text-amber-500 font-bold">•</span>
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>

                  {/* 5-Dimension Score Breakdown */}
                  <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-4">
                      Component Score Analysis (0–100 Scale)
                    </h4>

                    <div className="space-y-3.5 text-xs">
                      {/* Technical Skills */}
                      <div>
                        <div className="flex justify-between font-semibold mb-1">
                          <span className="text-slate-800">1. Technical Skills Matching (35% weight)</span>
                          <span className="font-bold text-indigo-600">{data.component_scores.technical_skills}%</span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-2">
                          <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${data.component_scores.technical_skills}%` }} />
                        </div>
                      </div>

                      {/* Semantic Similarity */}
                      <div>
                        <div className="flex justify-between font-semibold mb-1">
                          <span className="text-slate-800">2. Semantic Requirement Similarity (25% weight)</span>
                          <span className="font-bold text-cyan-600">{data.component_scores.semantic_similarity}%</span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-2">
                          <div className="bg-cyan-500 h-2 rounded-full" style={{ width: `${data.component_scores.semantic_similarity}%` }} />
                        </div>
                      </div>

                      {/* Experience */}
                      <div>
                        <div className="flex justify-between font-semibold mb-1">
                          <span className="text-slate-800">3. Relevant Experience Duration (20% weight)</span>
                          <span className="font-bold text-emerald-600">{data.component_scores.relevant_experience}%</span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-2">
                          <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${data.component_scores.relevant_experience}%` }} />
                        </div>
                      </div>

                      {/* Education */}
                      <div>
                        <div className="flex justify-between font-semibold mb-1">
                          <span className="text-slate-800">4. Education & Academic Degree (10% weight)</span>
                          <span className="font-bold text-amber-600">{data.component_scores.education}%</span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-2">
                          <div className="bg-amber-500 h-2 rounded-full" style={{ width: `${data.component_scores.education}%` }} />
                        </div>
                      </div>

                      {/* Responsibility */}
                      <div>
                        <div className="flex justify-between font-semibold mb-1">
                          <span className="text-slate-800">5. Responsibility Alignment (10% weight)</span>
                          <span className="font-bold text-purple-600">{data.component_scores.responsibilities}%</span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-2">
                          <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${data.component_scores.responsibilities}%` }} />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Ethics and Non-Discrimination Banner */}
                  <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-xs text-slate-600 flex items-start gap-2.5">
                    <ShieldCheck className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-slate-800">Fairness & Explainability Assurance: </span>
                      {data.fairness_statement}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: SKILLS TAXONOMY */}
              {activeTab === 'skills' && (
                <div className="space-y-6">
                  {/* Explicit Matches */}
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-700 mb-3 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      Explicit & Verified Synonym Matches (1.0 Value)
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {data.matched_skills.map((m, i) => (
                        <div key={i} className="p-3.5 rounded-xl border border-emerald-200 bg-emerald-50/40">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-900 text-xs">{m.skill}</span>
                            <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                              {m.type}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-600 mt-2 line-clamp-2 italic bg-white/70 p-2 rounded border border-emerald-100">
                            "{m.evidence}"
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Related Skills */}
                  {data.related_skills.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-purple-700 mb-3 flex items-center gap-1.5">
                        <Sparkles className="w-4 h-4" />
                        Explicitly Mapped Related Skills (0.7 Value)
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {data.related_skills.map((m, i) => (
                          <div key={i} className="p-3.5 rounded-xl border border-purple-200 bg-purple-50/40">
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-slate-900 text-xs">
                                Found: {m.related_skill_found} (for {m.required_skill})
                              </span>
                              <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-purple-100 text-purple-800">
                                Related (70%)
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-600 mt-2 line-clamp-2 italic bg-white/70 p-2 rounded border border-purple-100">
                              "{m.evidence}"
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Missing Skills */}
                  {data.missing_skills.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-red-700 mb-3 flex items-center gap-1.5">
                        <AlertCircle className="w-4 h-4" />
                        Missing Required Skills (0.0 Value - No Evidence Found)
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {data.missing_skills.map((s) => (
                          <span key={s} className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-red-50 text-red-700 border border-red-200">
                            ✗ {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* TAB 3: TIMELINE & EXPERIENCE */}
              {activeTab === 'experience' && (
                <div className="space-y-6">
                  <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                    <div>
                      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Calculated Duration</span>
                      <div className="text-2xl font-extrabold text-slate-900 mt-0.5">
                        {data.experience_analysis.final_years} Years
                      </div>
                      <span className="text-xs text-slate-500">Non-overlapping employment periods</span>
                    </div>

                    <div className="text-right">
                      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Overlap Resolution</span>
                      <div className={`text-xs font-bold mt-1 px-3 py-1 rounded-full ${
                        data.experience_analysis.has_overlapping_intervals
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}>
                        {data.experience_analysis.has_overlapping_intervals
                          ? 'Simultaneous dates merged'
                          : 'Sequential employment'}
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3">
                      Detected Date Intervals in Resume
                    </h4>
                    <div className="space-y-2">
                      {data.experience_analysis.detected_date_ranges.map((range, idx) => (
                        <div key={idx} className="p-3 rounded-xl bg-white border border-slate-200 flex items-center gap-3 text-xs">
                          <Clock className="w-4 h-4 text-indigo-600" />
                          <span className="font-semibold text-slate-800">{range}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 4: VERIFIABLE EXCERPTS */}
              {activeTab === 'evidence' && (
                <div className="space-y-4">
                  <p className="text-xs text-slate-500">
                    Exact textual excerpts extracted by sentence-transformers from the candidate's resume that justify each requirement score:
                  </p>

                  <div className="space-y-3">
                    {data.evidence_items.map((ev, i) => (
                      <div key={i} className="p-4 rounded-xl border border-slate-200 bg-white space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-bold text-slate-900">{ev.requirement_text}</span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-100 text-slate-700">
                            {ev.dimension} • {ev.similarity_score}%
                          </span>
                        </div>
                        <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs italic text-slate-700 flex items-start gap-2">
                          <Quote className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                          <span>"{ev.resume_excerpt || 'No direct text excerpt'}"</span>
                        </div>
                        <div className="text-[11px] text-slate-500 font-medium">
                          Analysis: {ev.explanation}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="bg-slate-50 px-6 py-4 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition"
          >
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
};
