import { Droppable, type DroppableProvided, type DroppableStateSnapshot } from '@hello-pangea/dnd';
import { Plus } from 'lucide-react';
import type { JobApplication, Column } from '../types';
import { JobCard } from './JobCard';

interface KanbanColumnProps {
  column: Column;
  jobs: JobApplication[];
  onAddJob: (status?: string) => void;
  onEditJob: (job: JobApplication) => void;
}

export function KanbanColumn({ column, jobs, onAddJob, onEditJob }: KanbanColumnProps) {
  const getColumnColor = (color: string) => {
    const opacity = '20';
    return {
      background: `${color}${opacity}`,
      border: color,
    };
  };

  const columnStyle = getColumnColor(column.color);

  return (
    <div className="flex flex-col min-w-[280px] w-[280px] max-w-[280px]">
      {/* Column Header */}
      <div 
        className="rounded-t-lg p-3 border-t-4"
        style={{ 
          backgroundColor: columnStyle.background,
          borderColor: columnStyle.border 
        }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2 className="font-semibold text-gray-800 text-sm">{column.title}</h2>
            <span className="bg-white text-gray-600 text-xs px-2 py-0.5 rounded-full font-medium">
              {jobs.length}
            </span>
          </div>
          <button
            onClick={() => onAddJob(column.id)}
            className="text-gray-500 hover:text-gray-700 hover:bg-white/50 rounded p-1 transition-colors"
            title="Add job to this column"
          >
            <Plus size={16} />
          </button>
        </div>
      </div>

      {/* Column Content */}
      <Droppable droppableId={column.id}>
        {(provided: DroppableProvided, snapshot: DroppableStateSnapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`
              flex-1 bg-gray-50 rounded-b-lg p-3 min-h-[200px]
              transition-colors duration-200
              ${snapshot.isDraggingOver ? 'bg-blue-50 ring-2 ring-blue-200 ring-inset' : ''}
            `}
          >
            {jobs.map((job, index) => (
              <JobCard
                key={job.id}
                job={job}
                index={index}
                onEdit={onEditJob}
              />
            ))}
            {provided.placeholder}
            
            {/* Empty state */}
            {jobs.length === 0 && !snapshot.isDraggingOver && (
              <div className="text-center py-8 text-gray-400 text-sm">
                <p>No jobs yet</p>
                <button
                  onClick={() => onAddJob(column.id)}
                  className="text-blue-500 hover:text-blue-600 mt-1 text-xs underline"
                >
                  Add your first job
                </button>
              </div>
            )}
          </div>
        )}
      </Droppable>
    </div>
  );
}
