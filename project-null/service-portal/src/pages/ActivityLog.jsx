import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getAgentActivity } from '../services/api';
import { Clock, Search, ChevronLeft, ChevronRight, User } from 'lucide-react';

export default function ActivityLog() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const limit = 20;

  const { data, isLoading } = useQuery({
    queryKey: ['agent-activity', { page, limit, search }],
    queryFn: () => getAgentActivity({ page, limit, q: search || undefined }),
    keepPreviousData: true,
  });

  const items = data?.items || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Activity Log</h1>
        <p className="text-sm text-gray-500 mt-1">
          All farmer access sessions are recorded here
        </p>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          className="w-full rounded-lg border border-gray-300 pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
          placeholder="Search by farmer ID or purpose"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Clock className="w-6 h-6 text-primary-600 animate-spin" />
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-20">
            <User className="w-10 h-10 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No activity records found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Farmer ID</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Farmer Name</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Purpose</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Start</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">End</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Duration</th>
                  <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody>
                {items.map((s) => {
                  const start = new Date(s.session_start);
                  const end = s.session_end ? new Date(s.session_end) : null;
                  const dur = end
                    ? `${Math.round((end - start) / 60000)} min`
                    : '—';

                  return (
                    <tr key={s.id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="py-3 px-4 font-mono text-primary-700">{s.farmer_id}</td>
                      <td className="py-3 px-4 text-gray-700">{s.farmer_name || '—'}</td>
                      <td className="py-3 px-4 text-gray-600">{s.purpose}</td>
                      <td className="py-3 px-4 text-gray-500 whitespace-nowrap">
                        {start.toLocaleDateString('en-IN')} {start.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                      </td>
                      <td className="py-3 px-4 text-gray-500 whitespace-nowrap">
                        {end ? `${end.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}` : '—'}
                      </td>
                      <td className="py-3 px-4 text-gray-500">{dur}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                            s.status === 'active'
                              ? 'bg-green-100 text-green-700'
                              : s.status === 'ended'
                              ? 'bg-gray-100 text-gray-600'
                              : 'bg-red-100 text-red-600'
                          }`}
                        >
                          {s.status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100">
            <p className="text-sm text-gray-500">
              Showing {(page - 1) * limit + 1}–{Math.min(page * limit, total)} of {total}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-30"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="flex items-center text-sm text-gray-600 px-2">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-30"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
