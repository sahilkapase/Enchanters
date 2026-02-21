import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSubsidyCalendar } from '../../hooks/useSubsidies';
import Card, { CardTitle } from '../common/Card';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { formatDate, deadlineColor } from '../../utils/formatters';

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

export default function DeadlineCalendar() {
  const { t } = useTranslation();
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());

  const { data: deadlines, isLoading } = useSubsidyCalendar({ month, year });

  const prevMonth = () => {
    if (month === 1) { setMonth(12); setYear(year - 1); }
    else setMonth(month - 1);
  };

  const nextMonth = () => {
    if (month === 12) { setMonth(1); setYear(year + 1); }
    else setMonth(month + 1);
  };

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <CardTitle>{t('subsidies.calendar_view')}</CardTitle>
        <div className="flex items-center gap-2">
          <button onClick={prevMonth} className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
            <ChevronLeft className="w-4 h-4 text-gray-600" />
          </button>
          <span className="text-sm font-semibold text-gray-900 min-w-[140px] text-center">
            {MONTH_NAMES[month - 1]} {year}
          </span>
          <button onClick={nextMonth} className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
            <ChevronRight className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-8 text-sm text-gray-400">Loading...</div>
      ) : deadlines?.length > 0 ? (
        <div className="space-y-2">
          {deadlines.map((dl, i) => (
            <div
              key={i}
              className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 border border-gray-100"
            >
              <div className="w-12 h-12 rounded-xl bg-white border border-gray-200 flex flex-col items-center justify-center flex-shrink-0">
                <span className="text-xs text-gray-500">{MONTH_NAMES[month - 1].slice(0, 3)}</span>
                <span className="text-lg font-bold text-gray-900">
                  {new Date(dl.close_date || dl.date).getDate()}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">{dl.name_en || dl.name}</p>
                <p className={`text-xs font-medium ${deadlineColor(dl.close_date || dl.date)}`}>
                  {formatDate(dl.close_date || dl.date)}
                </p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-sm text-gray-400">
          No deadlines this month
        </div>
      )}
    </Card>
  );
}
