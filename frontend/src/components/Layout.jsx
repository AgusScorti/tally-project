// src/components/Layout.jsx
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/auth';
import { motion } from 'framer-motion';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: 'home' },
  { path: '/expenses', label: 'Expenses', icon: 'trending' },
  { path: '/payments', label: 'Payments', icon: 'send' },
  { path: '/reports', label: 'Reports', icon: 'chart' },
];

export default function Layout({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-tally-light">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 w-64 h-screen bg-white border-r border-tally-border px-6 py-8 flex flex-col hidden md:flex">
        {/* Logo */}
        <Link to="/dashboard" className="flex items-center gap-3 mb-12 hover:opacity-80 transition-opacity">
          <div className="w-10 h-10 bg-tally-500 rounded-lg flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold text-lg">T</span>
          </div>
          <h1 className="text-xl font-bold text-tally-text">Tally</h1>
        </Link>

        {/* Navigation */}
        <nav className="flex-1 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`block px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                location.pathname === item.path
                  ? 'bg-tally-50 text-tally-600'
                  : 'text-tally-text/70 hover:bg-tally-hover'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* User Profile */}
        <div className="pt-6 border-t border-tally-border">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm font-medium text-tally-text">{user?.full_name || user?.username}</p>
              <p className="text-xs text-tally-text/50">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full px-4 py-2 text-sm font-medium text-tally-text/70 hover:text-tally-text hover:bg-tally-hover rounded-lg transition-all duration-200"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="md:ml-64 min-h-screen">
        {/* Mobile Header */}
        <div className="md:hidden bg-white border-b border-tally-border px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-tally-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <h1 className="text-lg font-bold text-tally-text">Tally</h1>
          </div>
          <button className="text-tally-text/60 hover:text-tally-text">Menu</button>
        </div>

        {/* Page Content */}
        <div className="px-6 md:px-8 py-8">
          {children}
        </div>
      </main>
    </div>
  );
}
