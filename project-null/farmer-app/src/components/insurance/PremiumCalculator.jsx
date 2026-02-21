import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { useCalculatePremium } from '../../hooks/useInsurance';
import Card, { CardTitle } from '../common/Card';
import Button from '../common/Button';
import { CROPS, SEASONS } from '../../utils/constants';
import { Calculator, IndianRupee, Shield, Building2 } from 'lucide-react';
import { formatCurrency } from '../../utils/formatters';

export default function PremiumCalculator() {
  const { t } = useTranslation();
  const { farmer } = useAuth();
  const calculatePremium = useCalculatePremium();

  const [form, setForm] = useState({
    crop: '',
    season: 'kharif',
    district: farmer?.district || '',
    land_area: farmer?.land_area || '',
  });

  const handleCalculate = () => {
    calculatePremium.mutate({
      crop: form.crop,
      season: form.season,
      district: form.district,
      land_area: parseFloat(form.land_area),
    });
  };

  const result = calculatePremium.data;

  return (
    <Card>
      <CardTitle className="flex items-center gap-2 mb-4">
        <Calculator className="w-5 h-5 text-primary-600" />
        {t('insurance.premium_calculator')}
      </CardTitle>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">{t('common.crop')}</label>
          <select
            value={form.crop}
            onChange={(e) => setForm({ ...form, crop: e.target.value })}
            className="w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm bg-white focus:ring-2 focus:ring-primary-500 outline-none cursor-pointer"
          >
            <option value="">Select crop</option>
            {CROPS.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">{t('common.season')}</label>
          <select
            value={form.season}
            onChange={(e) => setForm({ ...form, season: e.target.value })}
            className="w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm bg-white focus:ring-2 focus:ring-primary-500 outline-none cursor-pointer"
          >
            {SEASONS.map((s) => (
              <option key={s.value} value={s.value}>{s.label_en}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">{t('common.district')}</label>
          <input
            type="text"
            value={form.district}
            onChange={(e) => setForm({ ...form, district: e.target.value })}
            placeholder="Enter district"
            className="w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 outline-none"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">{t('auth.land_area')} (acres)</label>
          <input
            type="number"
            value={form.land_area}
            onChange={(e) => setForm({ ...form, land_area: e.target.value })}
            placeholder="e.g., 5"
            min="0"
            step="0.1"
            className="w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 outline-none"
          />
        </div>
      </div>

      <Button
        onClick={handleCalculate}
        loading={calculatePremium.isPending}
        disabled={!form.crop || !form.district || !form.land_area}
        className="w-full"
      >
        {t('insurance.calculate')}
      </Button>

      {/* Result */}
      {result && (
        <div className="mt-6 bg-gradient-to-br from-primary-50 to-green-50 rounded-2xl p-5 space-y-4 border border-primary-100">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-white rounded-xl shadow-sm">
              <Shield className="w-5 h-5 text-blue-600 mx-auto mb-1" />
              <p className="text-xs text-gray-500">{t('insurance.sum_insured')}</p>
              <p className="text-lg font-bold text-gray-900">{formatCurrency(result.sum_insured)}</p>
            </div>
            <div className="text-center p-3 bg-white rounded-xl shadow-sm">
              <IndianRupee className="w-5 h-5 text-green-600 mx-auto mb-1" />
              <p className="text-xs text-gray-500">{t('insurance.farmer_premium')}</p>
              <p className="text-lg font-bold text-primary-700">{formatCurrency(result.farmer_premium)}</p>
            </div>
            <div className="text-center p-3 bg-white rounded-xl shadow-sm">
              <IndianRupee className="w-5 h-5 text-amber-600 mx-auto mb-1" />
              <p className="text-xs text-gray-500">{t('insurance.govt_subsidy')}</p>
              <p className="text-lg font-bold text-gray-900">{formatCurrency(result.govt_subsidy)}</p>
            </div>
            <div className="text-center p-3 bg-white rounded-xl shadow-sm">
              <Building2 className="w-5 h-5 text-gray-600 mx-auto mb-1" />
              <p className="text-xs text-gray-500">{t('insurance.insurance_company')}</p>
              <p className="text-sm font-bold text-gray-900">{result.insurance_company || 'N/A'}</p>
            </div>
          </div>
        </div>
      )}

      {calculatePremium.isError && (
        <p className="mt-3 text-sm text-red-500 text-center">
          Failed to calculate premium. Please try again.
        </p>
      )}
    </Card>
  );
}
