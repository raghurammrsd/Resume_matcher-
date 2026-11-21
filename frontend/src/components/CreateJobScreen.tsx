import React, { useState } from 'react';
import { Sparkles, Sliders, CheckCircle2, Plus, X, ArrowRight, RefreshCw, FileText } from 'lucide-react';
import { api } from '../api';
import { Job } from '../types';

interface CreateJobScreenProps {
  onJobCreated: (job: Job) => void;
}

const DEFAULT_AI_ENGINEER_JD = `Role: Senior AI Engineer
Department: Engineering
Location: Remote / Hybrid

We are looking for a Senior AI & Backend Engineer with at least 4 years of experience to design, build, and deploy production machine learning pipelines and scalable backend microservices.

Core Responsibilities:
- Build and maintain scalable REST APIs and high-throughput backend services using FastAPI and Python.
- Develop, evaluate, and deploy machine learning models and predictive pipelines into production.
- Architect containerized services using Docker and manage deployments across cloud environments.
- Optimize relational database schemas, indexes, and queries using PostgreSQL.

Required Qualifications & Skills:
- Minimum 4+ years of relevant software engineering and machine learning experience.
- Strong proficiency in Python, FastAPI, PostgreSQL, Docker, and Machine Learning (PyTorch or Scikit-learn).
- Proven track record of deploying containerized microservices and automated CI/CD pipelines.
- Bachelor's degree in Computer Science, Software Engineering, or equivalent practical experience.`;

export const CreateJobScreen: React.FC<CreateJobScreenProps> = ({ onJobCreated }) => {
  const [title, setTitle] = useState('Senior AI Engineer');
  const [department, setDepartment] = useState('Engineering');
  const [location, setLocation] = useState('Remote / Hybrid');
  const [description, setDescription] = useState(DEFAULT_AI_ENGINEER_JD);
  
  // Weights state (in percentages 0-100)
  const [weightSkills, setWeightSkills] = useState(35);
  const [weightSemantic, setWeightSemantic] = useState(25);
  const [weightExperience, setWeightExperience] = useState(20);
  const [weightEducation, setWeightEducation] = useState(10);
  const [weightResponsibility, setWeightResponsibility] = useState(10);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const totalWeight = weightSkills + weightSemantic + weightExperience + weightEducation + weightResponsibility;

  const handlePreloadTemplate = () => {
    setTitle('Senior AI Engineer');
    setDepartment('Engineering');
    setLocation('Remote / Hybrid');
    setDescription(DEFAULT_AI_ENGINEER_JD);
    setWeightSkills(35);
    setWeightSemantic(25);
    setWeightExperience(20);
    setWeightEducation(10);
    setWeightResponsibility(10);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) {
      setError('Job title and description are required.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const createdJob = await api.createJob({
        title,
        department,
        location,
        description,
        scoring_weights: {
          weight_skills: weightSkills / 100.0,
          weight_semantic: weightSemantic / 100.0,
          weight_experience: weightExperience / 100.0,
          weight_education: weightEducation / 100.0,
          weight_responsibility: weightResponsibility / 100.0,
        },
      });
      onJobCreated(createdJob);
    } catch (err: any) {
      setError(err.message || 'Failed to create job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Create Job Position
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Define requirements and customize 5-dimensional AI scoring weights.
          </p>
        </div>
        <button
          type="button"
          onClick={handlePreloadTemplate}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-50 text-indigo-700 text-xs font-semibold hover:bg-indigo-100 transition border border-indigo-200"
        >
          <Sparkles className="w-4 h-4 text-indigo-600" />
          Load Benchmark Scenario JD
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 text-red-700 border border-red-200 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic Job Details */}
        <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-sm space-y-6">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-600" />
            Position Details
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div className="sm:col-span-2">
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Job Title *
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Senior AI Engineer"
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Department
              </label>
              <input
                type="text"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                placeholder="Engineering"
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Job Description & Core Requirements *
            </label>
            <textarea
              required
              rows={12}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Paste the full job description here..."
              className="w-full p-4 rounded-xl border border-slate-300 text-sm font-mono leading-relaxed focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
            <p className="text-xs text-slate-400 mt-2">
              The AI NLP engine automatically extracts technical skills, minimum required experience years, education qualifications, and core responsibilities from this text.
            </p>
          </div>
        </div>

        {/* Scoring Weights Configurator */}
        <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Sliders className="w-5 h-5 text-indigo-600" />
              Evaluation Dimension Weights
            </h2>
            <div className={`px-3 py-1 rounded-full text-xs font-bold ${
              totalWeight === 100 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              Total Weight: {totalWeight}% {totalWeight === 100 ? '✓ (Balanced)' : '⚠️ (Must equal 100%)'}
            </div>
          </div>

          <p className="text-xs text-slate-500">
            Customize how much each dimension contributes to the candidate's final 0–100 score.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Technical Skills */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-bold text-slate-800">Technical Skills Matching</span>
                <span className="text-sm font-extrabold text-indigo-600">{weightSkills}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={weightSkills}
                onChange={(e) => setWeightSkills(Number(e.target.value))}
                className="w-full accent-indigo-600"
              />
              <span className="text-[11px] text-slate-400">Exact taxonomy & synonym verification</span>
            </div>

            {/* Semantic Similarity */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-bold text-slate-800">Semantic Requirement Alignment</span>
                <span className="text-sm font-extrabold text-cyan-600">{weightSemantic}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={weightSemantic}
                onChange={(e) => setWeightSemantic(Number(e.target.value))}
                className="w-full accent-cyan-600"
              />
              <span className="text-[11px] text-slate-400">Sentence transformer vector similarity</span>
            </div>

            {/* Experience */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-bold text-slate-800">Relevant Experience</span>
                <span className="text-sm font-extrabold text-emerald-600">{weightExperience}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={weightExperience}
                onChange={(e) => setWeightExperience(Number(e.target.value))}
                className="w-full accent-emerald-600"
              />
              <span className="text-[11px] text-slate-400">Non-overlapping employment duration</span>
            </div>

            {/* Education */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-bold text-slate-800">Education & Qualifications</span>
                <span className="text-sm font-extrabold text-amber-600">{weightEducation}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={weightEducation}
                onChange={(e) => setWeightEducation(Number(e.target.value))}
                className="w-full accent-amber-600"
              />
              <span className="text-[11px] text-slate-400">Degree level & academic field match</span>
            </div>

            {/* Responsibilities */}
            <div className="sm:col-span-2 p-4 rounded-xl bg-slate-50 border border-slate-200">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-bold text-slate-800">Job Responsibility Alignment</span>
                <span className="text-sm font-extrabold text-purple-600">{weightResponsibility}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={weightResponsibility}
                onChange={(e) => setWeightResponsibility(Number(e.target.value))}
                className="w-full accent-purple-600"
              />
              <span className="text-[11px] text-slate-400">Direct project accomplishment comparison against duties</span>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex items-center justify-end gap-4">
          <button
            type="submit"
            disabled={loading || totalWeight !== 100}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition shadow-md shadow-indigo-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Analyzing & Creating Position...
              </>
            ) : (
              <>
                Create Position & Extract Requirements
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
