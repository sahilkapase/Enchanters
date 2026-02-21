import { ELIGIBILITY_STATUS, BENEFIT_TYPES } from '../../utils/constants';

export function EligibilityBadge({ status }) {
  const config = ELIGIBILITY_STATUS[status] || ELIGIBILITY_STATUS.not_eligible;
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${config.color}`}>
      {config.label}
    </span>
  );
}

export function BenefitBadge({ type }) {
  const config = BENEFIT_TYPES[type];
  if (!config) return null;
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${config.color}`}>
      {config.label}
    </span>
  );
}

export function StatusBadge({ status }) {
  const colors = {
    open: 'bg-green-100 text-green-800',
    closing_soon: 'bg-amber-100 text-amber-800',
    closed: 'bg-gray-100 text-gray-600',
    active: 'bg-blue-100 text-blue-800',
    expired: 'bg-gray-100 text-gray-600',
  };

  const labels = {
    open: 'Open',
    closing_soon: 'Closing Soon',
    closed: 'Closed',
    active: 'Active',
    expired: 'Expired',
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${colors[status] || colors.closed}`}>
      {labels[status] || status}
    </span>
  );
}

export default function Badge({ children, color = 'gray', className = '' }) {
  const colors = {
    gray: 'bg-gray-100 text-gray-700',
    green: 'bg-green-100 text-green-700',
    red: 'bg-red-100 text-red-700',
    yellow: 'bg-yellow-100 text-yellow-700',
    blue: 'bg-blue-100 text-blue-700',
    purple: 'bg-purple-100 text-purple-700',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colors[color]} ${className}`}>
      {children}
    </span>
  );
}
