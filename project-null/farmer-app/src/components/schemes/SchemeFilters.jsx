import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { CROPS, SEASONS } from '../../utils/constants';
import { SlidersHorizontal, X } from 'lucide-react';
import Button from '../common/Button';

export default function SchemeFilters({ filters, onFilterChange }) {
  const { t } = useTranslation();
  const { farmer } = useAuth();
  const [showMobile, setShowMobile] = useState(false);

  const handleChange = (key, value) => {
    onFilterChange({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    onFilterChange({});
  };

  const hasActiveFilters = Object.values(filters).some((v) => v);

  const filterContent = (
    <div className="flex flex-col md:flex-row items-start md:items-end gap-3 flex-wrap">
      {/* Crop */}
      <div className="w-full md:w-auto">
        <label className="block text-xs font-medium text-gray-500 mb-1">{t('common.crop')}</label>
        <select
          value={filters.crop || ''}
          onChange={(e) => handleChange('crop', e.target.value)}
          className="w-full md:w-40 px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 outline-none cursor-pointer"
        >
          <option value="">All Crops</option>
          {CROPS.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Season */}
      <div className="w-full md:w-auto">
        <label className="block text-xs font-medium text-gray-500 mb-1">{t('common.season')}</label>
        <select
          value={filters.season || ''}
          onChange={(e) => handleChange('season', e.target.value)}
          className="w-full md:w-36 px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 outline-none cursor-pointer"
        >
          <option value="">All Seasons</option>
          {SEASONS.map((s) => (
            <option key={s.value} value={s.value}>{s.label_en}</option>
          ))}
        </select>
      </div>

      {/* Sort */}
      <div className="w-full md:w-auto">
        <label className="block text-xs font-medium text-gray-500 mb-1">Sort By</label>
        <select
          value={filters.sort || 'relevance'}
          onChange={(e) => handleChange('sort', e.target.value)}
          className="w-full md:w-36 px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 outline-none cursor-pointer"
        >
          <option value="relevance">{t('schemes.sort_relevance')}</option>
          <option value="deadline">{t('schemes.sort_deadline')}</option>
          <option value="benefit">{t('schemes.sort_benefit')}</option>
        </select>
      </div>

      {hasActiveFilters && (
        <Button variant="ghost" size="sm" onClick={clearFilters} icon={X}>
          Clear
        </Button>
      )}
    </div>
  );

  return (
    <>
      {/* Desktop filters */}
      <div className="hidden md:block bg-white rounded-2xl border border-gray-100 shadow-sm p-4 sticky top-16 z-10">
        {filterContent}
      </div>

      {/* Mobile filter toggle */}
      <div className="md:hidden">
        <Button variant="secondary" size="sm" icon={SlidersHorizontal} onClick={() => setShowMobile(!showMobile)}>
          {t('schemes.filter')} {hasActiveFilters && `(${Object.values(filters).filter(Boolean).length})`}
        </Button>

        {showMobile && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 mt-2">
            {filterContent}
          </div>
        )}
      </div>
    </>
  );
}
