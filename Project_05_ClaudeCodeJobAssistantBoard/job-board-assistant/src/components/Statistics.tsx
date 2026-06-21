import { Briefcase, CheckCircle2, Clock, TrendingUp, Target } from 'lucide-react';
import type { JobApplication } from '../types';
import { COLUMNS } from '../types';

interface StatisticsProps {
  jobs: JobApplication[];
}

export function Statistics({ jobs }: StatisticsProps) {
  const totalJobs = jobs.length;
  const appliedJobs = jobs.filter(j => j.status !== 'wishlist').length;
  const interviewJobs = jobs.filter(j => ['interview', 'offer', 'accepted'].includes(j.status)).length;
  const offerJobs = jobs.filter(j => ['offer', 'accepted'].includes(j.status)).length;

  // Calculate response rate
  const responseRate = appliedJobs > 0 
    ? Math.round(((interviewJobs + jobs.filter(j => j.status === 'rejected').length) / appliedJobs) * 100) 
    : 0;

  // Calculate conversion rate
  const conversionRate = interviewJobs > 0 
    ? Math.round((offerJobs / interviewJobs) * 100) 
    : 0;

  // Get jobs applied this week
  const oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
  const jobsThisWeek = jobs.filter(j => 
    j.dateApplied && new Date(j.dateApplied) >= oneWeekAgo
  ).length;

  // Get jobs applied this month
  const oneMonthAgo = new Date();
  oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
  const jobsThisMonth = jobs.filter(j => 
    j.dateApplied && new Date(j.dateApplied) >= oneMonthAgo
  ).length;

  const stats = [
    { 
      label: 'Total Jobs', 
      value: totalJobs, 
      icon: Briefcase, 
      color: 'bg-blue-500',
      description: 'In your pipeline'
    },
    { 
      label: 'Applied', 
      value: appliedJobs, 
      icon: CheckCircle2, 
      color: 'bg-green-500',
      description: 'Applications sent'
    },
    { 
      label: 'Interviews', 
      value: interviewJobs, 
      icon: Clock, 
      color: 'bg-amber-500',
      description: 'In interview stage'
    },
    { 
      label: 'Offers', 
      value: offerJobs, 
      icon: Target, 
      color: 'bg-purple-500',
      description: 'Offers received'
    },
  ];

  const secondaryStats = [
    { label: 'Response Rate', value: `${responseRate}%`, description: 'Heard back from companies' },
    { label: 'Conversion Rate', value: `${conversionRate}%`, description: 'Interviews to offers' },
    { label: 'This Week', value: jobsThisWeek, description: 'Applications sent' },
    { label: 'This Month', value: jobsThisMonth, description: 'Applications sent' },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <TrendingUp className="text-blue-600" size={24} />
        <h2 className="text-xl font-semibold text-gray-800">Dashboard Overview</h2>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="bg-gray-50 rounded-xl p-4 border border-gray-100 hover:border-gray-200 transition-colors"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className={`${stat.color} text-white p-2 rounded-lg`}>
                <stat.icon size={18} />
              </div>
              <span className="text-2xl font-bold text-gray-800">{stat.value}</span>
            </div>
            <p className="font-medium text-gray-700 text-sm">{stat.label}</p>
            <p className="text-gray-500 text-xs">{stat.description}</p>
          </div>
        ))}
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t border-gray-200">
        {secondaryStats.map((stat) => (
          <div key={stat.label} className="text-center">
            <p className="text-2xl font-bold text-gray-800">{stat.value}</p>
            <p className="text-sm font-medium text-gray-600">{stat.label}</p>
            <p className="text-xs text-gray-400">{stat.description}</p>
          </div>
        ))}
      </div>

      {/* Status Breakdown */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Status Breakdown</h3>
        <div className="flex flex-wrap gap-2">
          {COLUMNS.map(col => {
            const count = jobs.filter(j => j.status === col.id).length;
            return (
              <div
                key={col.id}
                className="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm"
                style={{ backgroundColor: `${col.color}20` }}
              >
                <div
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: col.color }}
                />
                <span className="font-medium text-gray-700">{col.title}</span>
                <span className="text-gray-500">({count})</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
