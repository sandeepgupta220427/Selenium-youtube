import { useState, useEffect } from 'react';
import { X, Plus, Trash2, Save, Calendar, Link2, Building, Briefcase, FileText, DollarSign, MapPin, Globe, MessageSquare } from 'lucide-react';
import type { JobApplication, JobStatus, JobUpdate } from '../types';
import { COLUMNS } from '../types';

interface JobModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (job: JobApplication) => void;
  onDelete?: (jobId: string) => void;
  job?: JobApplication | null;
  initialStatus?: JobStatus;
}

const emptyJob: Omit<JobApplication, 'id' | 'createdAt' | 'updatedAt'> = {
  companyName: '',
  jobTitle: '',
  jobUrl: '',
  source: '',
  resumeUsed: '',
  coverLetterUsed: '',
  status: 'wishlist',
  dateApplied: '',
  salary: '',
  location: '',
  remoteType: undefined,
  notes: '',
  updates: [],
};

export function JobModal({ isOpen, onClose, onSave, onDelete, job, initialStatus }: JobModalProps) {
  const [formData, setFormData] = useState<Omit<JobApplication, 'id' | 'createdAt' | 'updatedAt'>>(emptyJob);
  const [newUpdate, setNewUpdate] = useState('');
  const [activeTab, setActiveTab] = useState<'details' | 'updates'>('details');

  useEffect(() => {
    if (isOpen) {
      if (job) {
        setFormData({
          companyName: job.companyName,
          jobTitle: job.jobTitle,
          jobUrl: job.jobUrl || '',
          source: job.source,
          resumeUsed: job.resumeUsed,
          coverLetterUsed: job.coverLetterUsed || '',
          status: job.status,
          dateApplied: job.dateApplied || '',
          salary: job.salary || '',
          location: job.location || '',
          remoteType: job.remoteType,
          notes: job.notes,
          updates: job.updates,
        });
      } else {
        setFormData({
          ...emptyJob,
          status: initialStatus || 'wishlist',
          dateApplied: new Date().toISOString().split('T')[0],
        });
      }
      setNewUpdate('');
      setActiveTab('details');
    }
  }, [isOpen, job, initialStatus]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const now = new Date().toISOString();
    const jobData: JobApplication = {
      ...formData,
      id: job?.id || crypto.randomUUID(),
      createdAt: job?.createdAt || now,
      updatedAt: now,
    };
    onSave(jobData);
    onClose();
  };

  const handleAddUpdate = () => {
    if (!newUpdate.trim()) return;
    const update: JobUpdate = {
      id: crypto.randomUUID(),
      date: new Date().toISOString(),
      note: newUpdate.trim(),
    };
    setFormData({
      ...formData,
      updates: [...formData.updates, update],
    });
    setNewUpdate('');
  };

  const handleDeleteUpdate = (updateId: string) => {
    setFormData({
      ...formData,
      updates: formData.updates.filter(u => u.id !== updateId),
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">
            {job ? 'Edit Job Application' : 'Add New Job Application'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 p-1 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('details')}
            className={`
              px-4 py-2 text-sm font-medium transition-colors
              ${activeTab === 'details' 
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50/50' 
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'}
            `}
          >
            Details
          </button>
          <button
            onClick={() => setActiveTab('updates')}
            className={`
              px-4 py-2 text-sm font-medium transition-colors flex items-center gap-2
              ${activeTab === 'updates' 
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50/50' 
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'}
            `}
          >
            Updates
            {formData.updates.length > 0 && (
              <span className="bg-gray-200 text-gray-700 text-xs px-1.5 py-0.5 rounded-full">
                {formData.updates.length}
              </span>
            )}
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === 'details' ? (
            <form id="jobForm" onSubmit={handleSubmit} className="space-y-4">
              {/* Company & Position */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <span className="flex items-center gap-1.5">
                      <Building size={14} />
                      Company Name *
                    </span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.companyName}
                    onChange={(e) => setFormData({ ...formData, companyName: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    placeholder="e.g., Google"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <span className="flex items-center gap-1.5">
                      <Briefcase size={14} />
                      Job Title *
                    </span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.jobTitle}
                    onChange={(e) => setFormData({ ...formData, jobTitle: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    placeholder="e.g., Senior Software Engineer"
                  />
                </div>
              </div>

              {/* Job URL & Source */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <span className="flex items-center gap-1.5">
                      <Link2 size={14} />
                      Job URL
                    </span>
                  </label>
                  <input
                    type="url"
                    value={formData.jobUrl}
                    onChange={(e) => setFormData({ ...formData, jobUrl: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    placeholder="https://..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <span className="flex items-center gap-1.5">
                      <Globe size={14} />
                      Source *
                    </span>
                  </label>
                  <select
                    required
                    value={formData.source}
                    onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                  >
                    <option value="">Select source...</option>
                    <option value="LinkedIn">LinkedIn</option>
                    <option value="Indeed">Indeed</option>
                    <option value="Company Website">Company Website</option>
                    <option value="Referral">Referral</option>
                    <option value="Recruiter">Recruiter</option>
                    <option value="Glassdoor">Glassdoor</option>
                    <option value="AngelList">AngelList / Wellfound</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>

              {/* Status & Date Applied */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status *
                  </label>
                  <select
                    required
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as JobStatus })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                  >
                    {COLUMNS.map(col => (
                      <option key={col.id} value={col.id}>{col.title}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <span className="flex items-center gap-1.5">
                      <Calendar size={14} />
                      Date Applied
                    </span>
                  </label>
                  <input
                    type="date"
                    value={formData.dateApplied}
                    onChange={(e) => setFormData({ ...formData, dateApplied: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                  />
                </div>
              </div>

              {/* Resume & Cover Letter */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <span className="flex items-center gap-1.5">
                      <FileText size={14} />
                      Resume Used *
                    </span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.resumeUsed}
                    onChange={(e) => setFormData({ ...formData, resumeUsed: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    placeholder="e.g., Resume_Software_Engineer_v2.pdf"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Cover Letter Used
                  </label>
                  <input
                    type="text"
                    value={formData.coverLetterUsed}
                    onChange={(e) => setFormData({ ...formData, coverLetterUsed: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    placeholder="e.g., Cover_Letter_Google.pdf"
                  />
                </div>
              </div>

              {/* Location & Remote Type */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <span className="flex items-center gap-1.5">
                      <MapPin size={14} />
                      Location
                    </span>
                  </label>
                  <input
                    type="text"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    placeholder="e.g., San Francisco, CA"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Work Type
                  </label>
                  <select
                    value={formData.remoteType || ''}
                    onChange={(e) => setFormData({ ...formData, remoteType: (e.target.value as 'remote' | 'hybrid' | 'onsite') || undefined })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                  >
                    <option value="">Select...</option>
                    <option value="remote">Remote</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="onsite">On-site</option>
                  </select>
                </div>
              </div>

              {/* Salary */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <span className="flex items-center gap-1.5">
                    <DollarSign size={14} />
                    Salary Range
                  </span>
                </label>
                <input
                  type="text"
                  value={formData.salary}
                  onChange={(e) => setFormData({ ...formData, salary: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                  placeholder="e.g., $120k - $160k"
                />
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <span className="flex items-center gap-1.5">
                    <MessageSquare size={14} />
                    Notes
                  </span>
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none"
                  placeholder="Add any additional notes about this application..."
                />
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              {/* Add Update */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Add New Update
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newUpdate}
                    onChange={(e) => setNewUpdate(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddUpdate()}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    placeholder="e.g., Phone screen scheduled for next week"
                  />
                  <button
                    type="button"
                    onClick={handleAddUpdate}
                    disabled={!newUpdate.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
                  >
                    <Plus size={16} />
                    Add
                  </button>
                </div>
              </div>

              {/* Updates List */}
              <div className="space-y-2">
                {formData.updates.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <p>No updates yet.</p>
                    <p className="text-sm">Add updates to track your progress!</p>
                  </div>
                ) : (
                  [...formData.updates].reverse().map((update) => (
                    <div
                      key={update.id}
                      className="bg-white border border-gray-200 rounded-lg p-3 flex items-start justify-between gap-3"
                    >
                      <div className="flex-1">
                        <p className="text-gray-800 text-sm">{update.note}</p>
                        <p className="text-gray-400 text-xs mt-1">{formatDate(update.date)}</p>
                      </div>
                      <button
                        onClick={() => handleDeleteUpdate(update.id)}
                        className="text-gray-400 hover:text-red-500 p-1 rounded hover:bg-red-50 transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
          <div>
            {job && onDelete && (
              <button
                type="button"
                onClick={() => {
                  if (confirm('Are you sure you want to delete this job application?')) {
                    onDelete(job.id);
                    onClose();
                  }
                }}
                className="text-red-600 hover:text-red-700 text-sm font-medium flex items-center gap-1.5 px-3 py-2 rounded-lg hover:bg-red-50 transition-colors"
              >
                <Trash2 size={16} />
                Delete
              </button>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Cancel
            </button>
            {activeTab === 'details' && (
              <button
                type="submit"
                form="jobForm"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1.5"
              >
                <Save size={16} />
                {job ? 'Save Changes' : 'Add Job'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
