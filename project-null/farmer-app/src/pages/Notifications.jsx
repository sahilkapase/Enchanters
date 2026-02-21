import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import {
  Bell, BellOff, CheckCheck, ChevronLeft, ChevronRight,
  FileText, Coins, Clock, Info, AlertTriangle,
} from 'lucide-react';
import { useNotifications, useMarkRead, useMarkAllRead } from '../hooks/useNotifications';

/* ── tiny helpers ── */
const typeIcon = {
  new_scheme: FileText,
  new_subsidy: Coins,
  deadline_approaching: Clock,
  scheme_update: Info,
  general: Bell,
};

const priorityColor = {
  critical: 'bg-red-100 text-red-700 border-red-200',
  high: 'bg-amber-100 text-amber-700 border-amber-200',
  normal: 'bg-primary-50 text-primary-700 border-primary-200',
  low: 'bg-gray-50 text-gray-500 border-gray-200',
};

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(dateStr).toLocaleDateString();
}

export default function Notifications() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const isHi = i18n.language === 'hi';

  const [page, setPage] = useState(1);
  const [unreadOnly, setUnreadOnly] = useState(false);

  const { data, isLoading } = useNotifications({ page, perPage: 15, unreadOnly });
  const markRead = useMarkRead();
  const markAllRead = useMarkAllRead();

  const items = data?.items ?? [];
  const unreadCount = data?.unread_count ?? 0;
  const total = data?.total ?? 0;
  const perPage = data?.per_page ?? 15;
  const totalPages = Math.ceil(total / perPage) || 1;

  const handleClick = (n) => {
    if (!n.read) markRead.mutate(n.id);
    // navigate to the referenced item if applicable
    if (n.reference_type === 'scheme' && n.reference_id) {
      navigate(`/schemes/${n.reference_id}`);
    } else if (n.reference_type === 'subsidy' && n.reference_id) {
      navigate('/subsidies');
    }
  };

  /* ── Skeleton rows ── */
  const Skeleton = () => (
    <div className="space-y-3">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="animate-pulse flex gap-3 p-4 rounded-xl bg-gray-50">
          <div className="w-10 h-10 rounded-full bg-gray-200 shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-3/4" />
            <div className="h-3 bg-gray-200 rounded w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto px-4 py-6 space-y-5">
      {/* ── Header ── */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bell className="w-6 h-6 text-primary-600" />
          <h1 className="text-xl font-bold text-gray-900">
            {t('nav.notifications', 'Notifications')}
          </h1>
          {unreadCount > 0 && (
            <span className="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
              {unreadCount}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Toggle unread only */}
          <button
            onClick={() => { setUnreadOnly(!unreadOnly); setPage(1); }}
            className={`text-xs px-3 py-1.5 rounded-full border transition-colors cursor-pointer
              ${unreadOnly
                ? 'bg-primary-50 border-primary-300 text-primary-700'
                : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
          >
            {unreadOnly ? 'Unread' : 'All'}
          </button>

          {/* Mark all read */}
          {unreadCount > 0 && (
            <button
              onClick={() => markAllRead.mutate()}
              className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-800 cursor-pointer"
              title="Mark all as read"
            >
              <CheckCheck className="w-4 h-4" />
              <span className="hidden sm:inline">Read all</span>
            </button>
          )}
        </div>
      </div>

      {/* ── List ── */}
      {isLoading ? (
        <Skeleton />
      ) : items.length === 0 ? (
        <div className="flex flex-col items-center py-16 text-gray-400 space-y-3">
          <BellOff className="w-12 h-12" />
          <p className="text-sm">
            {unreadOnly ? 'No unread notifications' : 'No notifications yet'}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((n) => {
            const Icon = typeIcon[n.type] || Bell;
            const colors = priorityColor[n.priority] || priorityColor.normal;

            return (
              <button
                key={n.id}
                onClick={() => handleClick(n)}
                className={`w-full text-left flex gap-3 p-4 rounded-xl border transition-all cursor-pointer
                  ${n.read
                    ? 'bg-white border-gray-100 hover:bg-gray-50'
                    : `${colors} hover:shadow-sm`
                  }`}
              >
                {/* Icon */}
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0
                    ${n.read ? 'bg-gray-100' : 'bg-white/60'}`}
                >
                  <Icon className={`w-5 h-5 ${n.read ? 'text-gray-400' : ''}`} />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <p className={`text-sm leading-snug ${n.read ? 'text-gray-700' : 'font-semibold text-gray-900'}`}>
                    {isHi ? (n.title_hi || n.title_en) : n.title_en}
                  </p>
                  <p className={`text-xs mt-0.5 line-clamp-2 ${n.read ? 'text-gray-400' : 'text-gray-600'}`}>
                    {isHi ? (n.body_hi || n.body_en) : n.body_en}
                  </p>
                  <p className="text-[10px] text-gray-400 mt-1">{timeAgo(n.created_at)}</p>
                </div>

                {/* Unread dot */}
                {!n.read && (
                  <div className="w-2.5 h-2.5 rounded-full bg-primary-500 shrink-0 mt-1.5" />
                )}
              </button>
            );
          })}
        </div>
      )}

      {/* ── Pagination ── */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="p-2 rounded-lg border border-gray-200 disabled:opacity-30 hover:bg-gray-50 cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-sm text-gray-600">
            {page} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="p-2 rounded-lg border border-gray-200 disabled:opacity-30 hover:bg-gray-50 cursor-pointer"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
