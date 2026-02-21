import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Card from '../common/Card';
import { EligibilityBadge, BenefitBadge } from '../common/Badge';
import CountdownTimer from '../common/CountdownTimer';
import { ArrowRight, Building2 } from 'lucide-react';
import { truncate } from '../../utils/formatters';

export default function SchemeCard({ scheme }) {
  const { t } = useTranslation();

  return (
    <Link to={`/schemes/${scheme.id}`}>
      <Card hover className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-base font-bold text-gray-900 leading-snug">
              {scheme.name_en}
            </h3>
            {scheme.name_hi && scheme.name_hi !== scheme.name_en && (
              <p className="text-sm text-gray-500">{scheme.name_hi}</p>
            )}
          </div>
          <EligibilityBadge status={scheme.eligibility_status || 'not_eligible'} />
        </div>

        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Building2 className="w-3.5 h-3.5" />
          <span>{scheme.ministry}</span>
        </div>

        {scheme.description_en && (
          <p className="text-sm text-gray-600 leading-relaxed">
            {truncate(scheme.description_en, 120)}
          </p>
        )}

        <div className="flex items-center justify-between pt-2 border-t border-gray-50">
          <div className="flex items-center gap-2">
            <BenefitBadge type={scheme.benefit_type} />
            {scheme.benefit_amount && (
              <span className="text-sm font-semibold text-primary-700">{scheme.benefit_amount}</span>
            )}
          </div>

          <div className="flex items-center gap-3">
            {scheme.deadline && <CountdownTimer date={scheme.deadline} showDate={false} />}
            <ArrowRight className="w-4 h-4 text-gray-400" />
          </div>
        </div>
      </Card>
    </Link>
  );
}
