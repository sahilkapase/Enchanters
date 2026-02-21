import { NavLink, useLocation } from 'react-router-dom';
import { Home, FileText, Shield, Coins, User } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';

const navItems = [
  { to: '/home', icon: Home, labelKey: 'nav.home' },
  { to: '/schemes', icon: FileText, labelKey: 'nav.schemes' },
  { to: '/insurance', icon: Shield, labelKey: 'nav.insurance' },
  { to: '/subsidies', icon: Coins, labelKey: 'nav.subsidies' },
  { to: '/profile', icon: User, labelKey: 'nav.profile' },
];

export default function Navbar() {
  const { t } = useTranslation();
  const location = useLocation();

  // Hide navbar on landing / signup / login
  const hiddenPaths = ['/', '/signup', '/login'];
  if (hiddenPaths.includes(location.pathname)) return null;

  return (
    <>
      {/* Desktop top navbar */}
      <nav className="hidden md:flex items-center justify-between px-6 py-3 bg-white border-b border-gray-100 shadow-sm sticky top-0 z-40">
        <NavLink to="/home" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
            <span className="text-white font-bold text-sm">KS</span>
          </div>
          <span className="font-bold text-xl text-primary-800">KisaanSeva</span>
        </NavLink>

        <div className="flex items-center gap-1">
          {navItems.map(({ to, icon: Icon, labelKey }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all
                ${isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:text-primary-700 hover:bg-gray-50'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              {t(labelKey)}
            </NavLink>
          ))}
        </div>

        <LanguageSwitcher />
      </nav>

      {/* Mobile bottom tab bar */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-40 safe-area-bottom">
        <div className="flex items-center justify-around py-2">
          {navItems.map(({ to, icon: Icon, labelKey }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex flex-col items-center gap-0.5 px-3 py-1 rounded-lg transition-all min-w-[56px]
                ${isActive
                  ? 'text-primary-600'
                  : 'text-gray-400'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px] font-medium">{t(labelKey)}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </>
  );
}
