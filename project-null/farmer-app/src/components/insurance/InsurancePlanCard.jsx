import Card from '../common/Card';
import Button from '../common/Button';
import { Shield, ArrowRight } from 'lucide-react';

export default function InsurancePlanCard({ plan, onViewDetail }) {
  return (
    <Card hover className="space-y-3">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0">
          <Shield className="w-5 h-5 text-blue-600" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-bold text-gray-900">{plan.name_en}</h3>
          {plan.name_hi && <p className="text-sm text-gray-500">{plan.name_hi}</p>}
        </div>
        <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
          plan.plan_type === 'pmfby' ? 'bg-green-100 text-green-700' :
          plan.plan_type === 'rwbci' ? 'bg-blue-100 text-blue-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {plan.plan_type?.toUpperCase()}
        </span>
      </div>

      {plan.description_en && (
        <p className="text-sm text-gray-600 leading-relaxed line-clamp-2">{plan.description_en}</p>
      )}

      {plan.coverage && (
        <p className="text-xs text-gray-500"><span className="font-medium">Coverage:</span> {plan.coverage}</p>
      )}

      <div className="pt-2 border-t border-gray-50 flex items-center justify-between">
        {plan.premium_info && <p className="text-xs text-gray-500">{plan.premium_info}</p>}
        <Button variant="ghost" size="sm" onClick={() => onViewDetail?.(plan)}>
          Details <ArrowRight className="w-3 h-3" />
        </Button>
      </div>
    </Card>
  );
}
