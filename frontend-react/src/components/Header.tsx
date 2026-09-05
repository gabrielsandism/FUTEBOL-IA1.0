import Link from 'next/link';
import { useRouter } from 'next/router';
import { Activity, BarChart3, AlertCircle, Settings, Zap } from 'lucide-react';

export const Header = () => {
  const router = useRouter();

  const isActive = (path: string) => router.pathname === path;

  return (
    <header className="bg-dark-800 border-b border-dark-700 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <div className="w-8 h-8 bg-success rounded-lg flex items-center justify-center">
              <span className="text-dark-900 font-bold text-lg">⚽</span>
            </div>
            <div>
              <div className="font-bold text-dark-50">Football Scanner AI</div>
              <div className="text-xs text-dark-400">Real-time Analysis</div>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {[
              { href: '/', label: 'Dashboard', icon: Activity },
              { href: '/matches', label: 'Matches', icon: Zap },
              { href: '/rules', label: 'Rules', icon: Settings },
              { href: '/alerts', label: 'Alerts', icon: AlertCircle },
              { href: '/stats', label: 'Stats', icon: BarChart3 },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                    isActive(item.href)
                      ? 'bg-success text-dark-900 font-semibold'
                      : 'text-dark-300 hover:text-dark-50 hover:bg-dark-700'
                  }`}
                >
                  <Icon size={18} />
                  <span className="text-sm">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Mobile Menu Button */}
          <button className="md:hidden p-2 rounded-lg hover:bg-dark-700">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
};
