import { daysUntil, deadlineColor, formatDate } from '../../utils/formatters';
import { Clock } from 'lucide-react';

export default function CountdownTimer({ date, showDate = true }) {
  const days = daysUntil(date);
  const colorClass = deadlineColor(date);

  if (days === null) return null;

  let label;
  if (days < 0) {
    label = 'Expired';
  } else if (days === 0) {
    label = 'Today!';
  } else if (days === 1) {
    label = '1 day left';
  } else {
    label = `${days} days left`;
  }

  return (
    <div className={`flex items-center gap-1.5 text-sm font-medium ${colorClass}`}>
      <Clock className="w-3.5 h-3.5" />
      <span>{label}</span>
      {showDate && <span className="text-gray-400 font-normal">({formatDate(date)})</span>}
    </div>
  );
}
