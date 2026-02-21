import { NavLink, useNavigate } from 'react-router-dom';
import { useAgent } from '../context/AgentAuthContext';
import { LayoutDashboard, Search, ClipboardList, LogOut, Shield, Inbox } from 'lucide-react';

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/review', label: 'Review Queue', icon: Inbox },
  { to: '/lookup', label: 'Farmer Lookup', icon: Search },
  { to: '/activity', label: 'Activity Log', icon: ClipboardList },
];

export default function Sidebar() {
  const { agent, logout } = useAgent();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <aside className="w-64 bg-primary-900 text-white min-h-screen flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-primary-800">
        <div className="flex items-center gap-2">
          <Shield className="w-7 h-7 text-accent-400" />
          <div>
            <h1 className="font-bold text-lg leading-tight">KisaanSeva</h1>
            <p className="text-xs text-primary-300">Service Portal</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3 space-y-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-primary-700 text-white'
                  : 'text-primary-200 hover:bg-primary-800 hover:text-white'
              }`
            }
          >
            <Icon className="w-5 h-5" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Agent Info + Logout */}
      <div className="p-4 border-t border-primary-800">
        <div className="mb-3">
          <p className="text-sm font-medium">{agent?.name || 'Agent'}</p>
          <p className="text-xs text-primary-300">{agent?.center_name || 'Jan Suvidha Kendra'}</p>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 text-sm text-primary-300 hover:text-white transition-colors w-full"
        >
          <LogOut className="w-4 h-4" />
          Log Out
        </button>
      </div>
    </aside>
  );
}
