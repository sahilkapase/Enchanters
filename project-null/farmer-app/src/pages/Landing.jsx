import { Link, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { FileText, Shield, FileDown, ShieldCheck, IndianRupee, Lock } from 'lucide-react';
import Button from '../components/common/Button';
import LanguageSwitcher from '../components/layout/LanguageSwitcher';

export default function Landing() {
  const { t } = useTranslation();
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) return <Navigate to="/home" replace />;

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 via-white to-white">
      {/* Header */}
      <header className="flex items-center justify-between px-4 md:px-8 py-4">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-primary-600 flex items-center justify-center">
            <span className="text-white font-bold text-lg">KS</span>
          </div>
          <span className="font-bold text-2xl text-primary-800">{t('app_name')}</span>
        </div>
        <div className="flex items-center gap-4">
          <LanguageSwitcher />
          <Link to="/login">
            <Button variant="ghost" size="sm">{t('auth.login')}</Button>
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-4 pt-12 pb-16 md:pt-20 md:pb-24 text-center">
        <div className="inline-block px-4 py-1.5 rounded-full bg-primary-100 text-primary-700 text-sm font-medium mb-6">
          {t('tagline')}
        </div>
        <h1 className="text-4xl md:text-6xl font-extrabold text-gray-900 leading-tight mb-6">
          {t('landing.hero_title')}
        </h1>
        <p className="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto mb-10">
          {t('landing.hero_subtitle')}
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/signup">
            <Button size="lg" className="w-full sm:w-auto text-lg px-8">
              {t('landing.cta_signup')}
            </Button>
          </Link>
          <Link to="/login">
            <Button variant="secondary" size="lg" className="w-full sm:w-auto">
              {t('landing.cta_login')}
            </Button>
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-5xl mx-auto px-4 pb-16">
        <div className="grid md:grid-cols-3 gap-6">
          <FeatureCard
            icon={FileText}
            title={t('landing.feature_schemes')}
            description={t('landing.feature_schemes_desc')}
          />
          <FeatureCard
            icon={Shield}
            title={t('landing.feature_insurance')}
            description={t('landing.feature_insurance_desc')}
          />
          <FeatureCard
            icon={FileDown}
            title={t('landing.feature_forms')}
            description={t('landing.feature_forms_desc')}
          />
        </div>
      </section>

      {/* Trust Badges */}
      <section className="max-w-3xl mx-auto px-4 pb-20">
        <div className="flex flex-wrap justify-center gap-6">
          <TrustBadge icon={ShieldCheck} text={t('landing.trust_1')} />
          <TrustBadge icon={IndianRupee} text={t('landing.trust_2')} />
          <TrustBadge icon={Lock} text={t('landing.trust_3')} />
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-50 border-t border-gray-100 py-6 text-center text-sm text-gray-500">
        {t('app_name')} &copy; {new Date().getFullYear()} &mdash; Built for Indian Farmers
      </footer>
    </div>
  );
}

function FeatureCard({ icon: Icon, title, description }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 hover:shadow-md hover:border-primary-200 transition-all">
      <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center mb-4">
        <Icon className="w-6 h-6 text-primary-600" />
      </div>
      <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600 leading-relaxed">{description}</p>
    </div>
  );
}

function TrustBadge({ icon: Icon, text }) {
  return (
    <div className="flex items-center gap-2 text-gray-600">
      <Icon className="w-5 h-5 text-primary-600" />
      <span className="text-sm font-medium">{text}</span>
    </div>
  );
}
