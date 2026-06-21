import { useState, useMemo } from 'react';
import { DragDropContext, type DropResult } from '@hello-pangea/dnd';
import { Plus, Search, Filter, Download, Upload, Trash2 } from 'lucide-react';
import type { JobApplication, JobStatus } from './types';
import { COLUMNS } from './types';
import { useLocalStorage } from './hooks/useLocalStorage';
import { KanbanColumn } from './components/KanbanColumn';
import { JobModal } from './components/JobModal';
import { Statistics } from './components/Statistics';

function App() {
  const [jobs, setJobs] = useLocalStorage<JobApplication[]>('job-board-jobs', []);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingJob, setEditingJob] = useState<JobApplication | null>(null);
  const [initialStatus, setInitialStatus] = useState<JobStatus | undefined>(undefined);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<JobStatus | 'all'>('all');

  // Filter and search jobs
  const filteredJobs = useMemo(() => {
    return jobs.filter(job => {
      const matchesSearch = 
        job.companyName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        job.jobTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
        job.location?.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesFilter = filterStatus === 'all' || job.status === filterStatus;
      
      return matchesSearch && matchesFilter;
    });
  }, [jobs, searchQuery, filterStatus]);

  // Group jobs by status
  const jobsByStatus = useMemo(() => {
    const grouped: Record<string, JobApplication[]> = {};
    COLUMNS.forEach(col => {
      grouped[col.id] = filteredJobs.filter(job => job.status === col.id);
    });
    return grouped;
  }, [filteredJobs]);

  // Handle drag and drop
  const handleDragEnd = (result: DropResult) => {
    if (!result.destination) return;

    const { source, destination } = result;
    
    if (source.droppableId === destination.droppableId && 
        source.index === destination.index) {
      return;
    }

    const sourceStatus = source.droppableId as JobStatus;
    const destStatus = destination.droppableId as JobStatus;
    
    const sourceJobs = [...jobsByStatus[sourceStatus]];
    const [movedJob] = sourceJobs.splice(source.index, 1);
    
    const updatedJob = {
      ...movedJob,
      status: destStatus,
      updatedAt: new Date().toISOString(),
      // If moving to applied and no date set, set it to today
      dateApplied: destStatus === 'applied' && !movedJob.dateApplied 
        ? new Date().toISOString().split('T')[0] 
        : movedJob.dateApplied,
    };

    // Add update note when status changes
    if (sourceStatus !== destStatus) {
      const statusUpdate = {
        id: crypto.randomUUID(),
        date: new Date().toISOString(),
        note: `Moved from "${COLUMNS.find(c => c.id === sourceStatus)?.title}" to "${COLUMNS.find(c => c.id === destStatus)?.title}"`,
      };
      updatedJob.updates = [...updatedJob.updates, statusUpdate];
    }

    const newJobs = jobs.map(j => j.id === updatedJob.id ? updatedJob : j);
    setJobs(newJobs);
  };

  // Handle adding new job
  const handleAddJob = (status?: string) => {
    setEditingJob(null);
    setInitialStatus(status as JobStatus | undefined);
    setIsModalOpen(true);
  };

  // Handle editing job
  const handleEditJob = (job: JobApplication) => {
    setEditingJob(job);
    setInitialStatus(undefined);
    setIsModalOpen(true);
  };

  // Handle saving job
  const handleSaveJob = (job: JobApplication) => {
    if (editingJob) {
      setJobs(jobs.map(j => j.id === job.id ? job : j));
    } else {
      setJobs([...jobs, job]);
    }
  };

  // Handle deleting job
  const handleDeleteJob = (jobId: string) => {
    setJobs(jobs.filter(j => j.id !== jobId));
  };

  // Export data to JSON
  const handleExport = () => {
    const dataStr = JSON.stringify(jobs, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `job-applications-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Import data from JSON
  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const importedJobs = JSON.parse(event.target?.result as string);
        if (Array.isArray(importedJobs)) {
          if (confirm(`Import ${importedJobs.length} job applications? This will merge with your existing data.`)) {
            setJobs(prev => {
              const existingIds = new Set(prev.map(j => j.id));
              const newJobs = importedJobs.filter(j => !existingIds.has(j.id));
              return [...prev, ...newJobs];
            });
          }
        }
      } catch (error) {
        alert('Invalid JSON file');
      }
    };
    reader.readAsText(file);
    e.target.value = ''; // Reset input
  };

  // Clear all data
  const handleClearAll = () => {
    if (confirm('Are you sure you want to delete all job applications? This cannot be undone.')) {
      setJobs([]);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-[1600px] mx-auto px-4 py-4">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Job Board Assistant</h1>
              <p className="text-sm text-gray-500">Track your job applications and interview progress</p>
            </div>
            
            <div className="flex flex-wrap items-center gap-2">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                <input
                  type="text"
                  placeholder="Search jobs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none w-full sm:w-48"
                />
              </div>

              {/* Filter */}
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value as JobStatus | 'all')}
                  className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none appearance-none bg-white cursor-pointer w-full sm:w-40"
                >
                  <option value="all">All Status</option>
                  {COLUMNS.map(col => (
                    <option key={col.id} value={col.id}>{col.title}</option>
                  ))}
                </select>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2">
                <button
                  onClick={handleExport}
                  className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Export data"
                >
                  <Download size={18} />
                </button>
                <label className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors cursor-pointer" title="Import data">
                  <Upload size={18} />
                  <input
                    type="file"
                    accept=".json"
                    onChange={handleImport}
                    className="hidden"
                  />
                </label>
                <button
                  onClick={handleClearAll}
                  className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Clear all data"
                >
                  <Trash2 size={18} />
                </button>
              </div>

              {/* Add Job Button */}
              <button
                onClick={() => handleAddJob()}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                <Plus size={18} />
                Add Job
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1600px] mx-auto px-4 py-6">
        {/* Statistics */}
        <div className="mb-6">
          <Statistics jobs={jobs} />
        </div>

        {/* Kanban Board */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <DragDropContext onDragEnd={handleDragEnd}>
            <div className="flex gap-4 overflow-x-auto kanban-scroll pb-2">
              {COLUMNS.map(column => (
                <KanbanColumn
                  key={column.id}
                  column={column}
                  jobs={jobsByStatus[column.id] || []}
                  onAddJob={handleAddJob}
                  onEditJob={handleEditJob}
                />
              ))}
            </div>
          </DragDropContext>
        </div>
      </main>

      {/* Job Modal */}
      <JobModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveJob}
        onDelete={handleDeleteJob}
        job={editingJob}
        initialStatus={initialStatus}
      />
    </div>
  );
}

export default App;
