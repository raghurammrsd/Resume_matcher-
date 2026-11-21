import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardScreen } from './components/DashboardScreen';
import { CreateJobScreen } from './components/CreateJobScreen';
import { UploadScreen } from './components/UploadScreen';
import { RankingScreen } from './components/RankingScreen';
import { CandidateModal } from './components/CandidateModal';
import { Job } from './types';
import { api } from './api';

export function App() {
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'create_job' | 'upload' | 'ranking'>('dashboard');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string>('');
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);
  const [loadingJobs, setLoadingJobs] = useState(true);

  const fetchJobs = async () => {
    try {
      const data = await api.getJobs();
      setJobs(data);
      if (data.length > 0 && !selectedJobId) {
        setSelectedJobId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch jobs', err);
    } finally {
      setLoadingJobs(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const selectedJob = jobs.find((j) => j.id === selectedJobId) || (jobs.length > 0 ? jobs[0] : null);

  const handleJobCreated = (newJob: Job) => {
    setJobs([newJob, ...jobs]);
    setSelectedJobId(newJob.id);
    setCurrentTab('upload');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        jobs={jobs}
        selectedJobId={selectedJobId}
        setSelectedJobId={setSelectedJobId}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {loadingJobs ? (
          <div className="py-20 text-center text-slate-400">Loading system...</div>
        ) : (
          <>
            {currentTab === 'dashboard' && (
              <DashboardScreen
                job={selectedJob}
                onNavigate={setCurrentTab}
                onSelectCandidate={setSelectedCandidateId}
              />
            )}

            {currentTab === 'create_job' && (
              <CreateJobScreen onJobCreated={handleJobCreated} />
            )}

            {currentTab === 'upload' && (
              <UploadScreen job={selectedJob} onNavigate={setCurrentTab} />
            )}

            {currentTab === 'ranking' && (
              <RankingScreen
                job={selectedJob}
                onSelectCandidate={setSelectedCandidateId}
                onNavigate={setCurrentTab}
              />
            )}
          </>
        )}
      </main>

      {/* Detailed Candidate Analysis Modal */}
      {selectedCandidateId && selectedJob && (
        <CandidateModal
          candidateId={selectedCandidateId}
          jobId={selectedJob.id}
          onClose={() => setSelectedCandidateId(null)}
        />
      )}
    </div>
  );
}

export default App;
