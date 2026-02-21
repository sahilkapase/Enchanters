import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAgent } from '../context/AgentAuthContext';
import {
  getStagedItems,
  approveStagedItem,
  rejectStagedItem,
  createStagedItem,
} from '../services/api';
import {
  Inbox, Check, X, Bot, PenTool, Filter,
  ChevronLeft, ChevronRight, Eye, Plus,
} from 'lucide-react';
import toast from 'react-hot-toast';
import ReviewDetail from './ReviewDetail';
import AddItemModal from './AddItemModal';

const STATUS_TABS = [
  { value: '', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
];

const SOURCE_ICONS = {
  myscheme: Bot,
  data_gov: Bot,
  rss_feed: Bot,
  manual: PenTool,
};

function StatusBadge({ status }) {
  const styles = {
    pending: 'bg-amber-100 text-amber-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
  };
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${styles[status] || 'bg-gray-100 text-gray-600'}`}>
      {status}
    </span>
  );
}

function TypeBadge({ type }) {
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
      type === 'scheme' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
    }`}>
      {type}
    </span>
  );
}

export default function ReviewQueue() {
  const { agent } = useAgent();
  const queryClient = useQueryClient();

  const [statusFilter, setStatusFilter] = useState('pending');
  const [page, setPage] = useState(1);
  const [selectedItem, setSelectedItem] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['staged-items', { status: statusFilter, page }],
    queryFn: () => getStagedItems({ status: statusFilter || undefined, page, per_page: 15 }),
  });

  const approveMutation = useMutation({
    mutationFn: ({ id }) =>
      approveStagedItem(id, {
        reviewed_by: agent?.name || 'Agent',
        review_notes: '',
      }),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['staged-items'] });
      const stats = result.matching_stats || {};
      toast.success(
        `Approved! ${stats.notified || 0} farmers notified.`,
        { duration: 4000 },
      );
      setSelectedItem(null);
    },
    onError: () => toast.error('Failed to approve item'),
  });

  const rejectMutation = useMutation({
    mutationFn: ({ id, notes }) =>
      rejectStagedItem(id, {
        reviewed_by: agent?.name || 'Agent',
        review_notes: notes || '',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staged-items'] });
      toast.success('Item rejected');
      setSelectedItem(null);
    },
    onError: () => toast.error('Failed to reject item'),
  });

  const createMutation = useMutation({
    mutationFn: (data) => createStagedItem(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staged-items'] });
      toast.success('Item added to review queue');
      setShowAddModal(false);
    },
    onError: (err) => toast.error(err?.response?.data?.detail || 'Failed to create item'),
  });

  const items = data?.items || [];
  const totalPages = data?.pages || 1;

  if (selectedItem) {
    return (
      <ReviewDetail
        item={selectedItem}
        onBack={() => setSelectedItem(null)}
        onApprove={(id) => approveMutation.mutate({ id })}
        onReject={(id, notes) => rejectMutation.mutate({ id, notes })}
        isApproving={approveMutation.isPending}
        isRejecting={rejectMutation.isPending}
        agentName={agent?.name || 'Agent'}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Review Queue</h1>
          <p className="text-sm text-gray-500 mt-1">
            Review scraped and manually entered schemes before publishing to farmers
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          Add Entry
        </button>
      </div>

      {/* Status Tabs */}
      <div className="flex gap-2">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.value}
            onClick={() => { setStatusFilter(tab.value); setPage(1); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer
              ${statusFilter === tab.value
                ? 'bg-primary-100 text-primary-700'
                : 'bg-white text-gray-500 hover:bg-gray-50 border border-gray-200'
              }`}
          >
            {tab.label}
            {tab.value === 'pending' && data?.total > 0 && statusFilter === 'pending' && (
              <span className="ml-1.5 bg-amber-500 text-white text-xs px-1.5 py-0.5 rounded-full">
                {data.total}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Items Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-gray-400">Loading...</div>
        ) : items.length === 0 ? (
          <div className="p-12 text-center">
            <Inbox className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No items in this queue</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Source</th>
                <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="text-right py-3 px-4 text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => {
                const SourceIcon = SOURCE_ICONS[item.source] || Bot;
                return (
                  <tr key={item.id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <SourceIcon className="w-4 h-4 text-gray-400" />
                        <span className="text-xs text-gray-500">{item.source}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <p className="text-sm font-medium text-gray-900 truncate max-w-xs">
                        {item.name_en}
                      </p>
                      {item.ministry && (
                        <p className="text-xs text-gray-400 truncate">{item.ministry}</p>
                      )}
                    </td>
                    <td className="py-3 px-4"><TypeBadge type={item.item_type} /></td>
                    <td className="py-3 px-4"><StatusBadge status={item.status} /></td>
                    <td className="py-3 px-4 text-xs text-gray-500">
                      {item.created_at
                        ? new Date(item.created_at).toLocaleDateString('en-IN', {
                            day: '2-digit', month: 'short',
                          })
                        : '—'}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => setSelectedItem(item)}
                          className="p-1.5 text-gray-400 hover:text-primary-600 rounded-lg hover:bg-primary-50 cursor-pointer"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {item.status === 'pending' && (
                          <>
                            <button
                              onClick={() => approveMutation.mutate({ id: item.id })}
                              disabled={approveMutation.isPending}
                              className="p-1.5 text-gray-400 hover:text-green-600 rounded-lg hover:bg-green-50 cursor-pointer"
                              title="Approve"
                            >
                              <Check className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => rejectMutation.mutate({ id: item.id, notes: '' })}
                              disabled={rejectMutation.isPending}
                              className="p-1.5 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 cursor-pointer"
                              title="Reject"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Page {page} of {totalPages} ({data?.total || 0} items)
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-2 rounded-lg border border-gray-200 disabled:opacity-30 hover:bg-gray-50 cursor-pointer"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-2 rounded-lg border border-gray-200 disabled:opacity-30 hover:bg-gray-50 cursor-pointer"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Add Item Modal */}
      {showAddModal && (
        <AddItemModal
          onClose={() => setShowAddModal(false)}
          onSubmit={(data) => createMutation.mutate(data)}
          isSubmitting={createMutation.isPending}
        />
      )}
    </div>
  );
}
