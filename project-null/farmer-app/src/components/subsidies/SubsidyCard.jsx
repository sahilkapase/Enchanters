import Card from '../common/Card';
import { StatusBadge } from '../common/Badge';
import CountdownTimer from '../common/CountdownTimer';
import Button from '../common/Button';
import { Bell, Coins } from 'lucide-react';
import { daysUntil } from '../../utils/formatters';

export default function SubsidyCard({ subsidy, onSetReminder, onViewDetail }) {
  const days = daysUntil(subsidy.close_date);
  let status = 'open';
  if (days !== null && days < 0) status = 'closed';
  else if (days !== null && days <= 7) status = 'closing_soon';

  return (
    <Card hover className="space-y-3" onClick={() => onViewDetail?.(subsidy)}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <div className="w-10 h-10 rounded-xl bg-accent-100 flex items-center justify-center flex-shrink-0">
            <Coins className="w-5 h-5 text-accent-600" />
          </div>
          <div className="min-w-0">
            <h3 className="text-base font-bold text-gray-900 leading-snug">{subsidy.name_en}</h3>
            {subsidy.name_hi && <p className="text-sm text-gray-500">{subsidy.name_hi}</p>}
          </div>
        </div>
        <StatusBadge status={status} />
      </div>

      {subsidy.description_en && (
        <p className="text-sm text-gray-600 leading-relaxed line-clamp-2">{subsidy.description_en}</p>
      )}

      <div className="flex flex-wrap items-center gap-2 text-xs">
        {subsidy.category && (
          <span className="px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 capitalize">{subsidy.category}</span>
        )}
        {subsidy.state && (
          <span className="px-2 py-0.5 rounded-full bg-blue-50 text-blue-600">{subsidy.state}</span>
        )}
        {subsidy.benefit_amount && (
          <span className="px-2 py-0.5 rounded-full bg-green-50 text-green-700 font-semibold">{subsidy.benefit_amount}</span>
        )}
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-gray-50">
        <CountdownTimer date={subsidy.close_date} />
        {status !== 'closed' && (
          <Button
            variant="ghost"
            size="sm"
            icon={Bell}
            onClick={(e) => {
              e.stopPropagation();
              onSetReminder?.(subsidy.id);
            }}
          >
            Remind
          </Button>
        )}
      </div>
    </Card>
  );
}
