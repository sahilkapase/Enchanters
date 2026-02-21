import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { useSchemes } from '../hooks/useSchemes';
import { useSubsidies } from '../hooks/useSubsidies';
import Card, { CardTitle } from '../components/common/Card';
import Button from '../components/common/Button';
import CountdownTimer from '../components/common/CountdownTimer';
import { PageLoader } from '../components/common/Loader';
import {
  FileText, Shield, Download, ArrowRight, Copy, Share2,
  AlertCircle, Calendar, TrendingUp, Sprout,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function Home() {
  const { t } = useTranslation();
  const { farmer } = useAuth();

  const { data: schemes, isLoading: schemesLoading } = useSchemes({
    state: farmer?.state,
    district: farmer?.district,
  });

  const { data: subsidies, isLoading: subsidiesLoading } = useSubsidies({
    state: farmer?.state,
    status: 'open',
  });

  if (!farmer) return <PageLoader />;

  const eligibleSchemes = schemes?.filter?.((s) => s.eligibility_status === 'eligible') || [];
  const upcomingDeadlines = [
    ...(schemes?.filter?.((s) => s.deadline)?.slice(0, 3) || []),
    ...(subsidies?.filter?.((s) => s.close_date)?.slice(0, 2) || []),
  ].sort((a, b) => new Date(a.deadline || a.close_date) - new Date(b.deadline || b.close_date)).slice(0, 5);

  // Profile completion
  const profileFields = [farmer.name, farmer.phone, farmer.pin_code, farmer.land_area, farmer.district];
  const completedFields = profileFields.filter(Boolean).length;
  const profilePercent = Math.round((completedFields / 7) * 100); // 7 key fields total

  const copyFarmerId = () => {
    navigator.clipboard.writeText(farmer.farmer_id);
    toast.success('Farmer ID copied!');
  };

  const shareOnWhatsApp = () => {
    const text = `My KisaanSeva Farmer ID: ${farmer.farmer_id}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
  };

  return (
      <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        {/* Welcome Card */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <p className="text-primary-100 text-sm">{t('home.welcome')},</p>
              <h1 className="text-2xl font-bold">{farmer.name}</h1>
              <p className="text-primary-200 text-sm mt-1 font-mono">{farmer.farmer_id}</p>
              {farmer.district && (
                <p className="text-primary-200 text-sm">{farmer.district}, {farmer.state}</p>
              )}
            </div>
            <div className="flex gap-2">
              <button onClick={copyFarmerId} className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors cursor-pointer">
                <Copy className="w-4 h-4" />
              </button>
              <button onClick={shareOnWhatsApp} className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors cursor-pointer">
                <Share2 className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Profile completion bar */}
          <div className="mt-4">
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-primary-200">{t('home.profile_completion', { percent: profilePercent })}</span>
              <Link to="/profile" className="text-primary-100 hover:text-white text-xs underline">
                {t('home.complete_profile_cta')}
              </Link>
            </div>
            <div className="w-full bg-white/20 rounded-full h-2">
              <div className="bg-white rounded-full h-2 transition-all" style={{ width: `${profilePercent}%` }} />
            </div>
          </div>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <Link to="/schemes">
            <Card hover className="text-center">
              <FileText className="w-8 h-8 text-primary-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-gray-900">
                {schemesLoading ? '...' : eligibleSchemes.length}
              </p>
              <p className="text-sm text-gray-500">{t('home.eligible_schemes')}</p>
            </Card>
          </Link>

          <Link to="/subsidies">
            <Card hover className="text-center">
              <Calendar className="w-8 h-8 text-accent-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-gray-900">
                {subsidiesLoading ? '...' : upcomingDeadlines.length}
              </p>
              <p className="text-sm text-gray-500">{t('home.upcoming_deadlines')}</p>
            </Card>
          </Link>

          <Link to="/insurance" className="col-span-2 md:col-span-1">
            <Card hover className="text-center">
              <Shield className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-gray-900">
                <TrendingUp className="w-5 h-5 inline text-green-500" />
              </p>
              <p className="text-sm text-gray-500">{t('home.insurance_status')}</p>
            </Card>
          </Link>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardTitle className="mb-4">{t('home.quick_actions')}</CardTitle>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <Link to="/schemes">
              <div className="flex items-center gap-3 p-3 rounded-xl border border-gray-100 hover:border-primary-200 hover:bg-primary-50 transition-all">
                <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center flex-shrink-0">
                  <Sprout className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900">{t('home.find_schemes')}</p>
                  <p className="text-xs text-gray-500">Browse eligible schemes</p>
                </div>
                <ArrowRight className="w-4 h-4 text-gray-400 ml-auto" />
              </div>
            </Link>

            <Link to="/insurance">
              <div className="flex items-center gap-3 p-3 rounded-xl border border-gray-100 hover:border-primary-200 hover:bg-primary-50 transition-all">
                <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <Shield className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900">{t('home.view_insurance')}</p>
                  <p className="text-xs text-gray-500">Browse insurance plans</p>
                </div>
                <ArrowRight className="w-4 h-4 text-gray-400 ml-auto" />
              </div>
            </Link>

            <Link to="/schemes">
              <div className="flex items-center gap-3 p-3 rounded-xl border border-gray-100 hover:border-primary-200 hover:bg-primary-50 transition-all">
                <div className="w-10 h-10 rounded-lg bg-accent-100 flex items-center justify-center flex-shrink-0">
                  <Download className="w-5 h-5 text-accent-600" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900">{t('home.download_form')}</p>
                  <p className="text-xs text-gray-500">Auto-filled PDFs</p>
                </div>
                <ArrowRight className="w-4 h-4 text-gray-400 ml-auto" />
              </div>
            </Link>
          </div>
        </Card>

        {/* Upcoming Deadlines */}
        {upcomingDeadlines.length > 0 && (
          <Card>
            <CardTitle className="mb-4">{t('home.upcoming_deadlines')}</CardTitle>
            <div className="space-y-3">
              {upcomingDeadlines.map((item, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-gray-50 border border-gray-100">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-900 truncate">
                      {item.name_en || item.name}
                    </p>
                    <p className="text-xs text-gray-500 truncate">
                      {item.ministry || item.category}
                    </p>
                  </div>
                  <CountdownTimer date={item.deadline || item.close_date} />
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Service Center Note */}
        <div className="bg-primary-50 border border-primary-200 rounded-2xl p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-primary-800 font-medium">{t('home.visit_center')}</p>
            <p className="text-xs text-primary-600 mt-1 font-mono">{farmer.farmer_id}</p>
          </div>
        </div>
      </div>
  );
}
