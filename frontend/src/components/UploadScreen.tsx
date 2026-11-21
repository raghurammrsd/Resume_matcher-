import React, { useState, useEffect, useRef } from 'react';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  Trash2, 
  Sparkles, 
  ArrowRight,
  AlertTriangle
} from 'lucide-react';
import { Job, ProcessingStatus } from '../types';
import { api } from '../api';

interface UploadScreenProps {
  job: Job | null;
  onNavigate: (tab: 'dashboard' | 'create_job' | 'upload' | 'ranking') => void;
}

export const UploadScreen: React.FC<UploadScreenProps> = ({ job, onNavigate }) => {
  const [statusData, setStatusData] = useState<ProcessingStatus | null>(null);
  const [uploading, setUploading] = useState(false);
  const [loadingSamples, setLoadingSamples] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchStatus = async () => {
    if (!job) return;
    try {
      const data = await api.getProcessingStatus(job.id);
      setStatusData(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchStatus();
    // Auto-poll status every 1.5 seconds if processing
    const interval = setInterval(() => {
      if (statusData && !statusData.is_complete && statusData.pending_resumes > 0) {
        fetchStatus();
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [job?.id, statusData?.pending_resumes]);

  const handleFiles = async (files: FileList | File[]) => {
    if (!job) return;
    const validFiles: File[] = [];
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const ext = file.name.split('.').pop()?.toLowerCase();
      if (ext === 'pdf' || ext === 'docx') {
        validFiles.push(file);
      }
    }

    if (validFiles.length === 0) {
      alert('Please upload .pdf or .docx resumes only.');
      return;
    }

    setUploading(true);
    try {
      await api.uploadResumes(job.id, validFiles);
      await fetchStatus();
    } catch (err: any) {
      alert(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleLoadSamples = async () => {
    if (!job) return;
    setLoadingSamples(true);
    try {
      await api.loadSampleResumes(job.id);
      await fetchStatus();
    } catch (err: any) {
      alert(err.message || 'Failed to load samples');
    } finally {
      setLoadingSamples(false);
    }
  };

  const handleDelete = async (resumeId: string) => {
    try {
      await api.deleteResume(resumeId);
      await fetchStatus();
    } catch (err: any) {
      alert(err.message || 'Failed to delete resume');
    }
  };

  if (!job) {
    return (
      <div className="text-center py-20">
        <h2 className="text-xl font-bold text-slate-800">Select or Create a Job Position First</h2>
        <button
          onClick={() => onNavigate('create_job')}
          className="mt-4 px-5 py-2.5 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-700"
        >
          Create Job Position
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Bulk Resume Upload & Parsing
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Upload candidate resumes (PDF or DOCX) to run AI extraction and semantic scoring.
          </p>
        </div>

        {/* Quick Benchmark Button */}
        <button
          onClick={handleLoadSamples}
          disabled={loadingSamples || uploading}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 text-white text-xs font-semibold hover:from-indigo-700 hover:to-indigo-800 transition shadow-sm disabled:opacity-50"
        >
          {loadingSamples ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Loading 15 Benchmark Resumes...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 text-cyan-300" />
              1-Click Load 15 Benchmark Resumes
            </>
          )}
        </button>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragActive(false);
          if (e.dataTransfer.files) handleFiles(e.dataTransfer.files);
        }}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center cursor-pointer transition-all ${
          dragActive
            ? 'border-indigo-600 bg-indigo-50/70 scale-[0.99]'
            : 'border-slate-300 bg-white hover:border-indigo-400 hover:bg-slate-50/50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => {
            if (e.target.files) handleFiles(e.target.files);
          }}
        />

        <div className="w-16 h-16 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto mb-4">
          <UploadCloud className="w-8 h-8" />
        </div>

        <h3 className="text-base font-bold text-slate-800">
          Drag & drop resumes here, or <span className="text-indigo-600 underline">browse files</span>
        </h3>
        <p className="text-xs text-slate-400 mt-1.5">
          Supports PDF and DOCX formats (up to 15MB each, 10–50 resumes in batch)
        </p>
        <div className="mt-4 flex items-center justify-center gap-2 text-xs text-slate-500 font-medium">
          <span className="bg-slate-100 px-2.5 py-1 rounded-md">Automatic SHA-256 Deduplication</span>
          <span className="bg-slate-100 px-2.5 py-1 rounded-md">Fault-Tolerant Processing</span>
        </div>
      </div>

      {/* Processing Status Summary */}
      {statusData && statusData.total_resumes > 0 && (
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">
                Uploaded Resumes ({statusData.total_resumes})
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Completed: {statusData.completed_resumes} | Failed / Handled: {statusData.failed_resumes} | In Progress: {statusData.pending_resumes}
              </p>
            </div>

            {statusData.completed_resumes > 0 && (
              <button
                onClick={() => onNavigate('ranking')}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-700 transition"
              >
                View Candidate Rankings ({statusData.completed_resumes})
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider">
                  <th className="py-3 px-3">File Name</th>
                  <th className="py-3 px-3">Size</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3">Details / Validation</th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {statusData.resumes.map((r) => {
                  const isSuccess = r.status === 'completed';
                  const isFailed = r.status === 'failed';
                  const isPending = !isSuccess && !isFailed;

                  return (
                    <tr key={r.id} className="hover:bg-slate-50/70 transition">
                      <td className="py-3.5 px-3 flex items-center gap-2 text-slate-900 font-semibold">
                        <FileText className="w-4 h-4 text-slate-400 shrink-0" />
                        <span className="truncate max-w-xs">{r.filename}</span>
                      </td>
                      <td className="py-3.5 px-3 text-slate-500">
                        {(r.file_size / 1024).toFixed(1)} KB
                      </td>
                      <td className="py-3.5 px-3">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold ${
                            isSuccess
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : isFailed
                              ? 'bg-red-50 text-red-700 border border-red-200'
                              : 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                          }`}
                        >
                          {isSuccess && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />}
                          {isFailed && <XCircle className="w-3.5 h-3.5 text-red-600" />}
                          {isPending && <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-600" />}
                          {r.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-3.5 px-3 text-slate-600 max-w-sm">
                        {isFailed ? (
                          <div className="flex items-center gap-1.5 text-red-600">
                            <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                            <span className="truncate">{r.error_message || 'Validation error'}</span>
                          </div>
                        ) : isSuccess ? (
                          <span className="text-emerald-700">Parsed & matched against JD</span>
                        ) : (
                          <span className="text-slate-400">Processing background task...</span>
                        )}
                      </td>
                      <td className="py-3.5 px-3 text-right">
                        <button
                          onClick={() => handleDelete(r.id)}
                          className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                          title="Delete resume"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
