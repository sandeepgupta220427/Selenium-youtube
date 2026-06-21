import { Draggable, type DraggableProvided, type DraggableStateSnapshot } from '@hello-pangea/dnd';
import { Building2, MapPin, ExternalLink, FileText, Clock, MoreHorizontal, Calendar } from 'lucide-react';
import type { JobApplication } from '../types';
import { COLUMNS } from '../types';

interface JobCardProps {
  job: JobApplication;
  index: number;
  onEdit: (job: JobApplication) => void;
}

export function JobCard({ job, index, onEdit }: JobCardProps) {
  const column = COLUMNS.find(col => col.id === job.status);
  
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      wishlist: 'bg-slate-100 text-slate-700',
      applied: 'bg-blue-100 text-blue-700',
      interview: 'bg-amber-100 text-amber-700',
      offer: 'bg-green-100 text-green-700',
      rejected: 'bg-red-100 text-red-700',
      accepted: 'bg-purple-100 text-purple-700',
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getDaysSince = (dateString?: string) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysSince = getDaysSince(job.dateApplied);

  return (
    <Draggable draggableId={job.id} index={index}>
      {(provided: DraggableProvided, snapshot: DraggableStateSnapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={`
            bg-white rounded-lg p-4 mb-3 shadow-sm border border-gray-200
            cursor-pointer transition-all duration-200
            hover:shadow-md hover:border-gray-300
            ${snapshot.isDragging ? 'shadow-lg ring-2 ring-blue-400 rotate-2' : ''}
          `}
          onClick={() => onEdit(job)}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-gray-900 text-sm truncate pr-2">
                {job.jobTitle}
              </h3>
              <div className="flex items-center gap-1 text-gray-600 text-xs mt-0.5">
                <Building2 size={12} />
                <span className="truncate">{job.companyName}</span>
              </div>
            </div>
            <span className={`
              text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap
              ${getStatusColor(job.status)}
            `}>
              {column?.title}
            </span>
          </div>

          {/* Details */}
          <div className="space-y-1.5 mb-3">
            {job.location && (
              <div className="flex items-center gap-1.5 text-gray-500 text-xs">
                <MapPin size={12} />
                <span>{job.location}</span>
                {job.remoteType && (
                  <span className="text-gray-400">
                    • {job.remoteType.charAt(0).toUpperCase() + job.remoteType.slice(1)}
                  </span>
                )}
              </div>
            )}
            
            {job.resumeUsed && (
              <div className="flex items-center gap-1.5 text-gray-500 text-xs">
                <FileText size={12} />
                <span className="truncate" title={job.resumeUsed}>
                  {job.resumeUsed.length > 25 ? job.resumeUsed.substring(0, 25) + '...' : job.resumeUsed}
                </span>
              </div>
            )}

            <div className="flex items-center gap-1.5 text-gray-500 text-xs">
              <Clock size={12} />
              <span>Via {job.source}</span>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between pt-2 border-t border-gray-100">
            <div className="flex items-center gap-1.5 text-gray-400 text-xs">
              <Calendar size={12} />
              {job.dateApplied ? (
                <span>
                  {formatDate(job.dateApplied)}
                  {daysSince !== null && (
                    <span className="text-gray-400 ml-1">
                      ({daysSince === 0 ? 'Today' : daysSince === 1 ? '1 day ago' : `${daysSince} days ago`})
                    </span>
                  )}
                </span>
              ) : (
                <span>No date</span>
              )}
            </div>
            
            {job.jobUrl && (
              <a
                href={job.jobUrl}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="text-blue-500 hover:text-blue-600 transition-colors"
                title="Open job posting"
              >
                <ExternalLink size={14} />
              </a>
            )}
          </div>

          {/* Updates indicator */}
          {job.updates.length > 0 && (
            <div className="mt-2 pt-2 border-t border-gray-100">
              <div className="flex items-center gap-1.5 text-xs text-amber-600">
                <MoreHorizontal size={12} />
                <span>{job.updates.length} update{job.updates.length > 1 ? 's' : ''}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </Draggable>
  );
}
