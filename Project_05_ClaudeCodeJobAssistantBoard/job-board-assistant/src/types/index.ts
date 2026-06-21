export type JobStatus = 'wishlist' | 'applied' | 'interview' | 'offer' | 'rejected' | 'accepted';

export interface JobUpdate {
  id: string;
  date: string;
  note: string;
}

export interface JobApplication {
  id: string;
  companyName: string;
  jobTitle: string;
  jobUrl?: string;
  source: string; // LinkedIn, Indeed, Company Website, Referral, etc.
  resumeUsed: string; // Resume version/filename
  coverLetterUsed?: string;
  status: JobStatus;
  dateApplied?: string;
  salary?: string;
  location?: string;
  remoteType?: 'remote' | 'hybrid' | 'onsite';
  notes: string;
  updates: JobUpdate[];
  createdAt: string;
  updatedAt: string;
}

export interface Column {
  id: JobStatus;
  title: string;
  color: string;
}

export const COLUMNS: Column[] = [
  { id: 'wishlist', title: 'Wishlist', color: '#94a3b8' },
  { id: 'applied', title: 'Applied', color: '#3b82f6' },
  { id: 'interview', title: 'Interview', color: '#f59e0b' },
  { id: 'offer', title: 'Offer', color: '#10b981' },
  { id: 'rejected', title: 'Rejected', color: '#ef4444' },
  { id: 'accepted', title: 'Accepted', color: '#8b5cf6' },
];
