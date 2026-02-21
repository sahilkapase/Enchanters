/**
 * Format phone number for display: +91 98765 43210
 */
export function formatPhone(phone) {
  if (!phone) return '';
  const digits = phone.replace(/\D/g, '');
  if (digits.length === 10) {
    return `+91 ${digits.slice(0, 5)} ${digits.slice(5)}`;
  }
  if (digits.length === 12 && digits.startsWith('91')) {
    return `+91 ${digits.slice(2, 7)} ${digits.slice(7)}`;
  }
  return phone;
}

/**
 * Mask phone: +91 987** ***10
 */
export function maskPhone(phone) {
  if (!phone) return '';
  const digits = phone.replace(/\D/g, '');
  const last2 = digits.slice(-2);
  const first3 = digits.length >= 10 ? digits.slice(digits.length - 10, digits.length - 7) : '***';
  return `+91 ${first3}** ***${last2}`;
}

/**
 * Format land area with unit
 */
export function formatLandArea(area, unit) {
  if (!area) return '';
  const unitLabels = { acre: 'acres', hectare: 'hectares', bigha: 'bigha' };
  return `${Number(area).toFixed(2)} ${unitLabels[unit] || unit}`;
}

/**
 * Format date to DD MMM YYYY
 */
export function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

/**
 * Days remaining until a date
 */
export function daysUntil(dateStr) {
  if (!dateStr) return null;
  const target = new Date(dateStr);
  const now = new Date();
  const diff = Math.ceil((target - now) / (1000 * 60 * 60 * 24));
  return diff;
}

/**
 * Deadline urgency color
 */
export function deadlineColor(dateStr) {
  const days = daysUntil(dateStr);
  if (days === null) return 'text-gray-500';
  if (days < 0) return 'text-gray-400';
  if (days <= 7) return 'text-red-600';
  if (days <= 30) return 'text-amber-600';
  return 'text-green-600';
}

/**
 * Format currency (INR)
 */
export function formatCurrency(amount) {
  if (!amount && amount !== 0) return '';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Truncate text
 */
export function truncate(text, maxLength = 100) {
  if (!text || text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + '...';
}
