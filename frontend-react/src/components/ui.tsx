import { ReactNode } from 'react';

// Card Component
export const Card = ({ children, className = '' }: { children: ReactNode; className?: string }) => (
  <div className={`bg-dark-800 border border-dark-700 rounded-lg p-4 ${className}`}>
    {children}
  </div>
);

// Badge Component
const BADGE_COLORS: Record<string, string> = {
  success: 'bg-green-900/30 text-success border border-success/30',
  warning: 'bg-yellow-900/30 text-warning border border-warning/30',
  danger: 'bg-red-900/30 text-danger border border-danger/30',
  info: 'bg-blue-900/30 text-info border border-info/30',
  purple: 'bg-purple-900/30 text-purple border border-purple/30',
};

export const Badge = ({ children, variant = 'info' }: { children: ReactNode; variant?: string }) => (
  <span className={`inline-block px-3 py-1 rounded text-xs font-semibold ${BADGE_COLORS[variant] || BADGE_COLORS.info}`}>
    {children}
  </span>
);

// Metric Component
export const Metric = ({ label, value, subtext = '' }: { label: string; value: string | number; subtext?: string }) => (
  <div className="bg-dark-800 border border-dark-700 rounded-lg p-4">
    <div className="text-dark-400 text-sm mb-2">{label}</div>
    <div className="text-2xl font-bold text-dark-50">{value}</div>
    {subtext && <div className="text-xs text-dark-500 mt-1">{subtext}</div>}
  </div>
);

// Loading Spinner
export const Spinner = () => (
  <div className="flex items-center justify-center">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-success"></div>
  </div>
);

// Alert Box
export const AlertBox = ({ type = 'info', children }: { type?: 'info' | 'warning' | 'error' | 'success'; children: ReactNode }) => {
  const colors: Record<string, string> = {
    info: 'bg-blue-900/30 border-blue-700/50 text-info',
    warning: 'bg-yellow-900/30 border-yellow-700/50 text-warning',
    error: 'bg-red-900/30 border-red-700/50 text-danger',
    success: 'bg-green-900/30 border-green-700/50 text-success',
  };
  return (
    <div className={`border rounded-lg p-4 ${colors[type]}`}>
      {children}
    </div>
  );
};

// Button Component
export const Button = ({
  children,
  onClick,
  variant = 'primary',
  className = '',
  disabled = false,
}: {
  children: ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  className?: string;
  disabled?: boolean;
}) => {
  const variants: Record<string, string> = {
    primary: 'bg-success hover:bg-green-600 text-dark-900 font-semibold',
    secondary: 'bg-dark-700 hover:bg-dark-600 text-dark-50 border border-dark-600',
    danger: 'bg-danger hover:bg-red-600 text-dark-50',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2 rounded-lg transition-colors ${variants[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
    >
      {children}
    </button>
  );
};

// Table Component
export const Table = ({ headers, rows }: { headers: string[]; rows: ReactNode[][] }) => (
  <div className="overflow-x-auto">
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b border-dark-700">
          {headers.map((h, i) => (
            <th key={i} className="text-left py-3 px-4 text-dark-400 font-semibold text-xs uppercase">
              {h}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i} className="border-b border-dark-700 hover:bg-dark-700/50">
            {row.map((cell, j) => (
              <td key={j} className="py-3 px-4">
                {cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
