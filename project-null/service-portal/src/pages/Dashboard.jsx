import { useQuery } from '@tanstack/react-query';
import { useAgent } from '../context/AgentAuthContext';
import { getAgentActivity, getPendingCount } from '../services/api';
import { LayoutDashboard, Users, FileCheck, Clock, Inbox } from 'lucide-react';

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-500">{label}</p>
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { agent } = useAgent();
  const { data: activity } = useQuery({
    queryKey: ['agent-activity', { limit: 5 }],
    queryFn: () => getAgentActivity({ limit: 5 }),
  });

  const { data: pendingData } = useQuery({
    queryKey: ['pending-count'],
    queryFn: getPendingCount,
    refetchInterval: 60000,
  });

  const pendingCount = pendingData?.pending_count || 0;

  const today = new Date().toLocaleDateString('en-IN', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const sessions = activity?.items || [];
  const todayCount = sessions.filter(
    (s) => new Date(s.session_start).toDateString() === new Date().toDateString()
  ).length;

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {agent?.name || 'Agent'}
        </h1>
        <p className="text-sm text-gray-500 mt-1">{today}</p>
        <p className="text-sm text-gray-500">{agent?.center_name || 'Jan Suvidha Kendra'}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Users} label="Farmers Today" value={todayCount} color="bg-primary-600" />
        <StatCard icon={FileCheck} label="Forms Generated" value={sessions.length} color="bg-green-600" />
        <StatCard icon={Inbox} label="Pending Review" value={pendingCount} color="bg-amber-500" />
        <StatCard icon={LayoutDashboard} label="Total Sessions" value={activity?.total || 0} color="bg-purple-600" />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <a
            href="/lookup"
            className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
          >
            <Users className="w-5 h-5 text-primary-600" />
            <div>
              <p className="text-sm font-medium text-gray-900">Look Up Farmer</p>
              <p className="text-xs text-gray-500">Search by ID or phone</p>
            </div>
          </a>
          <a
            href="/activity"
            className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
          >
            <Clock className="w-5 h-5 text-primary-600" />
            <div>
              <p className="text-sm font-medium text-gray-900">View Activity</p>
              <p className="text-xs text-gray-500">Session history</p>
            </div>
          </a>
          <a
            href="/lookup"
            className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
          >
            <FileCheck className="w-5 h-5 text-primary-600" />
            <div>
              <p className="text-sm font-medium text-gray-900">Generate Form</p>
              <p className="text-xs text-gray-500">Pre-fill application</p>
            </div>
          </a>
        </div>
      </div>

      {/* Recent Sessions */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Sessions</h2>
        {sessions.length === 0 ? (
          <p className="text-sm text-gray-500">No recent sessions.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500">Farmer ID</th>
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500">Purpose</th>
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500">Time</th>
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((s) => (
                  <tr key={s.id} className="border-b border-gray-50">
                    <td className="py-2 px-3 font-mono text-primary-700">{s.farmer_id}</td>
                    <td className="py-2 px-3 text-gray-700">{s.purpose}</td>
                    <td className="py-2 px-3 text-gray-500">
                      {new Date(s.session_start).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-2 px-3">
                      <span
                        className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                          s.status === 'active'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {s.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
