import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { useSubsidies, useSetSubsidyReminder } from '../hooks/useSubsidies';
import SubsidyCard from '../components/subsidies/SubsidyCard';
import DeadlineCalendar from '../components/subsidies/DeadlineCalendar';
import Card, { CardTitle } from '../components/common/Card';
import Modal from '../components/common/Modal';
import EmptyState from '../components/common/EmptyState';
import { PageLoader } from '../components/common/Loader';
import { SUBSIDY_CATEGORIES } from '../utils/constants';
import { Coins, List, CalendarDays, Filter } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Subsidies() {
  const { t } = useTranslation();
  const { farmer } = useAuth();
  const setReminder = useSetSubsidyReminder();

  const [activeTab, setActiveTab] = useState('list'); // 'list' | 'calendar'
  const [categoryFilter, setCategoryFilter] = useState('');
  const [showEligibleOnly, setShowEligibleOnly] = useState(true);
  const [selectedSubsidy, setSelectedSubsidy] = useState(null);

  const { data: subsidies, isLoading } = useSubsidies({
    state: farmer?.state,
    category: categoryFilter || undefined,
  });

  const handleSetReminder = (subsidyId) => {
    setReminder.mutate(
      { id: subsidyId, data: { channel: 'sms' } },
      {
        onSuccess: () => toast.success('Reminder set!'),
        onError: () => toast.error('Failed to set reminder'),
      }
    );
  };

  const tabs = [
    { id: 'list', label: t('subsidies.active'), icon: List },
    { id: 'calendar', label: t('subsidies.calendar_view'), icon: CalendarDays },
  ];

  return (
      <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">{t('subsidies.title')}</h1>

        {/* Tabs */}
        <div className="flex gap-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all cursor-pointer
                ${activeTab === tab.id
                  ? 'bg-primary-100 text-primary-700'
                  : 'bg-white text-gray-500 hover:bg-gray-50 border border-gray-200'
                }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === 'list' && (
          <>
            {/* Category filter chips */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setCategoryFilter('')}
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all cursor-pointer
                  ${!categoryFilter ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
              >
                All
              </button>
              {SUBSIDY_CATEGORIES.map((cat) => (
                <button
                  key={cat.value}
                  onClick={() => setCategoryFilter(cat.value)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all cursor-pointer
                    ${categoryFilter === cat.value ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                >
                  {cat.label_en}
                </button>
              ))}
            </div>

            {/* Eligible filter toggle */}
            {!isLoading && subsidies?.length > 0 && (
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-500">
                  {subsidies.filter((s) => s.eligible).length} eligible of {subsidies.length} subsidies
                </p>
                <button
                  onClick={() => setShowEligibleOnly(!showEligibleOnly)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer
                    ${showEligibleOnly ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                >
                  <Filter className="w-3.5 h-3.5" />
                  {showEligibleOnly ? 'Showing eligible' : 'Showing all'}
                </button>
              </div>
            )}

            {isLoading && <PageLoader />}

            {!isLoading && subsidies?.length === 0 && (
              <EmptyState
                icon={Coins}
                title="No subsidies found"
                description="Try changing your filters or check back later."
              />
            )}

            {!isLoading && subsidies?.length > 0 && (() => {
              const filtered = showEligibleOnly ? subsidies.filter((s) => s.eligible) : subsidies;
              return filtered.length > 0 ? (
                <div className="grid md:grid-cols-2 gap-4">
                  {filtered.map((subsidy) => (
                    <SubsidyCard
                      key={subsidy.id}
                      subsidy={subsidy}
                      onSetReminder={handleSetReminder}
                      onViewDetail={setSelectedSubsidy}
                    />
                  ))}
                </div>
              ) : (
                <EmptyState
                  icon={Coins}
                  title="No eligible subsidies"
                  description="Update your profile or tap 'Showing eligible' to see all subsidies."
                />
              );
            })()}
          </>
        )}

        {activeTab === 'calendar' && <DeadlineCalendar />}

        {/* Detail Modal */}
        <Modal isOpen={!!selectedSubsidy} onClose={() => setSelectedSubsidy(null)} title={selectedSubsidy?.name_en} size="lg">
          {selectedSubsidy && (
            <div className="space-y-4">
              {selectedSubsidy.description_en && (
                <p className="text-sm text-gray-700 leading-relaxed">{selectedSubsidy.description_en}</p>
              )}
              {selectedSubsidy.benefit_amount && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-1">Benefit</h4>
                  <p className="text-sm text-primary-700 font-bold">{selectedSubsidy.benefit_amount}</p>
                </div>
              )}
              {selectedSubsidy.description_hi && (
                <div className="pt-3 border-t border-gray-100">
                  <p className="text-sm text-gray-500">{selectedSubsidy.description_hi}</p>
                </div>
              )}
            </div>
          )}
        </Modal>
      </div>
  );
}
