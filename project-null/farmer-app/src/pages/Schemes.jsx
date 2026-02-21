import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { useSchemes } from '../hooks/useSchemes';
import SchemeCard from '../components/schemes/SchemeCard';
import SchemeFilters from '../components/schemes/SchemeFilters';
import EmptyState from '../components/common/EmptyState';
import { PageLoader } from '../components/common/Loader';
import { FileText, AlertCircle, Filter } from 'lucide-react';

export default function Schemes() {
  const { t } = useTranslation();
  const { farmer } = useAuth();

  const [filters, setFilters] = useState({
    state: farmer?.state || '',
    district: farmer?.district || '',
  });

  const [showEligibleOnly, setShowEligibleOnly] = useState(true);

  const { data: schemes, isLoading, isError, refetch } = useSchemes(filters);

  // Filter to eligible only when toggle is on
  const displaySchemes = showEligibleOnly
    ? schemes?.filter((s) => s.eligibility_status === 'eligible' || s.eligibility_status === 'partial')
    : schemes;

  const eligibleCount = schemes?.filter((s) => s.eligibility_status === 'eligible')?.length || 0;
  const totalCount = schemes?.length || 0;

  return (
      <div className="max-w-5xl mx-auto px-4 py-6 space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">{t('schemes.title')}</h1>
          {!isLoading && totalCount > 0 && (
            <span className="text-sm text-gray-500">
              {eligibleCount} eligible of {totalCount}
            </span>
          )}
        </div>

        <SchemeFilters filters={filters} onFilterChange={setFilters} />

        {/* Eligible only toggle */}
        {!isLoading && totalCount > 0 && (
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowEligibleOnly(!showEligibleOnly)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-all cursor-pointer
                ${showEligibleOnly
                  ? 'bg-primary-600 text-white border-primary-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-primary-300'}`}
            >
              <Filter className="w-4 h-4" />
              {showEligibleOnly ? 'Showing eligible only' : 'Showing all schemes'}
            </button>
          </div>
        )}

        {isLoading && <PageLoader />}

        {isError && (
          <EmptyState
            icon={AlertCircle}
            title={t('common.error')}
            description="Failed to load schemes. Please try again."
            actionLabel={t('common.retry')}
            onAction={refetch}
          />
        )}

        {!isLoading && !isError && displaySchemes?.length === 0 && (
          <EmptyState
            icon={FileText}
            title={showEligibleOnly ? 'No eligible schemes found' : t('schemes.no_results')}
            description={showEligibleOnly
              ? 'Update your profile or tap "Showing eligible only" to see all schemes.'
              : 'Try changing your crop, season, or location filters.'}
            actionLabel={showEligibleOnly ? 'Show all schemes' : undefined}
            onAction={showEligibleOnly ? () => setShowEligibleOnly(false) : undefined}
          />
        )}

        {!isLoading && displaySchemes?.length > 0 && (
          <div className="space-y-4">
            {displaySchemes.map((scheme) => (
              <SchemeCard key={scheme.id} scheme={scheme} />
            ))}
          </div>
        )}

        {/* Service center note */}
        <div className="bg-primary-50 border border-primary-200 rounded-2xl p-4 flex items-start gap-3 mt-6">
          <AlertCircle className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-primary-800">{t('schemes.need_help')}: <span className="font-mono font-bold">{farmer?.farmer_id}</span></p>
        </div>
      </div>
  );
}
