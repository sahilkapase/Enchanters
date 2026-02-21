import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { useUnreadCount } from '../../hooks/useNotifications';
import LanguageSwitcher from './LanguageSwitcher';
import {
  Home, FileText, Shield, Coins, User, Bell,
  Menu, X, LogOut, ChevronLeft,
} from 'lucide-react';

const navItems = [
  { to: '/home', icon: Home, labelKey: 'nav.home' },
  { to: '/schemes', icon: FileText, labelKey: 'nav.schemes' },
  { to: '/insurance', icon: Shield, labelKey: 'nav.insurance' },
  { to: '/subsidies', icon: Coins, labelKey: 'nav.subsidies' },
  { to: '/notifications', icon: Bell, labelKey: 'nav.notifications', badge: true },
  { to: '/profile', icon: User, labelKey: 'nav.profile' },
];

export default function Sidebar({ expanded, setExpanded }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { farmer, logout } = useAuth();
  const { data: unreadCount = 0 } = useUnreadCount();

  // Mobile: overlay drawer open/closed
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  /* ── Shared nav link renderer ── */
  const renderNavItem = ({ to, icon: Icon, labelKey, badge }, showLabel) => (
    <NavLink
      key={to}
      to={to}
      onClick={() => setMobileOpen(false)}
      className={({ isActive }) =>
        `group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all
        ${isActive
          ? 'bg-primary-100 text-primary-700'
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
        }`
      }
    >
      <span className="relative shrink-0">
        <Icon className="w-5 h-5" />
        {badge && unreadCount > 0 && (
          <span className="absolute -top-1.5 -right-1.5 bg-red-500 text-white text-[9px] font-bold leading-none min-w-[16px] h-4 flex items-center justify-center rounded-full px-1">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </span>
      {showLabel && <span className="truncate">{t(labelKey)}</span>}
    </NavLink>
  );

  /* ───────── Desktop Sidebar ───────── */
  const desktopSidebar = (
    <aside
      className={`hidden md:flex flex-col fixed top-0 left-0 h-screen bg-white border-r border-gray-200 z-30
                  transition-all duration-300 ease-in-out
                  ${expanded ? 'w-60' : 'w-[68px]'}`}
    >
      {/* Logo + collapse toggle */}
      <div className="flex items-center justify-between px-3 py-4 border-b border-gray-100">
        <NavLink to="/home" className="flex items-center gap-2 overflow-hidden">
          <div className="w-9 h-9 rounded-lg bg-primary-600 flex items-center justify-center shrink-0">
            <span className="text-white font-bold text-sm">KS</span>
          </div>
          {expanded && (
            <span className="font-bold text-lg text-primary-800 whitespace-nowrap">
              KisaanSeva
            </span>
          )}
        </NavLink>
        <button
          onClick={() => setExpanded(!expanded)}
          className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer shrink-0"
          title={expanded ? 'Collapse' : 'Expand'}
        >
          <ChevronLeft
            className={`w-4 h-4 text-gray-500 transition-transform duration-300 ${!expanded ? 'rotate-180' : ''}`}
          />
        </button>
      </div>

      {/* Nav links */}
      <nav className="flex-1 flex flex-col gap-1 px-2 py-4 overflow-y-auto">
        {navItems.map((item) => renderNavItem(item, expanded))}
      </nav>

      {/* Bottom section */}
      <div className="px-2 py-3 border-t border-gray-100 space-y-2">
        {expanded && <LanguageSwitcher />}

        {/* Farmer mini-card */}
        {farmer && expanded && (
          <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-gray-50">
            <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center shrink-0">
              <User className="w-4 h-4 text-primary-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-900 truncate">
                {farmer.name}
              </p>
              <p className="text-[10px] text-gray-500 font-mono truncate">
                {farmer.farmer_id}
              </p>
            </div>
          </div>
        )}

        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium
                     text-gray-600 hover:bg-red-50 hover:text-red-600 transition-all cursor-pointer"
        >
          <LogOut className="w-5 h-5 shrink-0" />
          {expanded && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );

  /* ───────── Mobile overlay sidebar ───────── */
  const mobileSidebar = (
    <>
      {/* Hamburger trigger (top bar on mobile) */}
      <div className="md:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-gray-100 sticky top-0 z-30">
        <button
          onClick={() => setMobileOpen(true)}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
        >
          <Menu className="w-5 h-5 text-gray-700" />
        </button>
        <NavLink to="/home" className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-primary-600 flex items-center justify-center">
            <span className="text-white font-bold text-xs">KS</span>
          </div>
          <span className="font-bold text-lg text-primary-800">KisaanSeva</span>
        </NavLink>
        <div className="w-9" /> {/* spacer for centering */}
      </div>

      {/* Backdrop */}
      {mobileOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/40 z-40"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Drawer */}
      <aside
        className={`md:hidden fixed top-0 left-0 h-full w-72 bg-white z-50
                    transform transition-transform duration-300 ease-in-out shadow-xl
                    ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        {/* Drawer header */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-gray-100">
          <NavLink to="/home" className="flex items-center gap-2" onClick={() => setMobileOpen(false)}>
            <div className="w-9 h-9 rounded-lg bg-primary-600 flex items-center justify-center">
              <span className="text-white font-bold text-sm">KS</span>
            </div>
            <span className="font-bold text-lg text-primary-800">KisaanSeva</span>
          </NavLink>
          <button
            onClick={() => setMobileOpen(false)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Farmer info */}
        {farmer && (
          <div className="flex items-center gap-3 px-4 py-4 border-b border-gray-100 bg-gray-50">
            <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center shrink-0">
              <User className="w-5 h-5 text-primary-600" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-gray-900 truncate">{farmer.name}</p>
              <p className="text-xs text-gray-500 font-mono truncate">{farmer.farmer_id}</p>
            </div>
          </div>
        )}

        {/* Nav */}
        <nav className="flex-1 flex flex-col gap-1 px-3 py-4">
          {navItems.map((item) => renderNavItem(item, true))}
        </nav>

        {/* Bottom */}
        <div className="absolute bottom-0 left-0 right-0 px-3 py-4 border-t border-gray-100 space-y-3">
          <LanguageSwitcher />
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium
                       text-gray-600 hover:bg-red-50 hover:text-red-600 transition-all cursor-pointer"
          >
            <LogOut className="w-5 h-5 shrink-0" />
            <span>Logout</span>
          </button>
        </div>
      </aside>
    </>
  );

  return (
    <>
      {desktopSidebar}
      {mobileSidebar}
    </>
  );
}
