import { useParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useSchemeDetail, useSchemeEligibility, useGenerateSchemeForm, useSetSchemeReminder } from '../hooks/useSchemes';
import Card, { CardTitle } from '../components/common/Card';
import Button from '../components/common/Button';
import { EligibilityBadge, BenefitBadge } from '../components/common/Badge';
import CountdownTimer from '../components/common/CountdownTimer';
import { PageLoader } from '../components/common/Loader';
import toast from 'react-hot-toast';
import {
  ArrowLeft, Building2, Download, ExternalLink, Bell,
  CheckCircle2, XCircle, FileText,
} from 'lucide-react';

export default function SchemeDetail() {
  const { id } = useParams();
  const { t } = useTranslation();

  const { data: scheme, isLoading } = useSchemeDetail(id);
  const { data: eligibility } = useSchemeEligibility(id);
  const generateForm = useGenerateSchemeForm();
  const setReminder = useSetSchemeReminder();

  if (isLoading) return <PageLoader />;
  if (!scheme) return <div className="p-8 text-center text-gray-500">Scheme not found</div>;

  const handleDownloadForm = () => {
    generateForm.mutate(id, {
      onSuccess: () => toast.success('Form downloaded!'),
      onError: () => toast.error('Failed to generate form'),
    });
  };

  const handleSetReminder = () => {
    setReminder.mutate(
      { id, data: { channel: 'sms' } },
      {
        onSuccess: () => toast.success('Reminder set!'),
        onError: () => toast.error('Failed to set reminder'),
      }
    );
  };

  return (
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-5">
        {/* Back */}
        <Link to="/schemes" className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-primary-600 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          {t('common.back')} to Schemes
        </Link>

        {/* Header */}
        <Card>
          <div className="space-y-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h1 className="text-xl md:text-2xl font-bold text-gray-900">{scheme.name_en}</h1>
                {scheme.name_hi && <p className="text-base text-gray-500 mt-1">{scheme.name_hi}</p>}
              </div>
              <EligibilityBadge status={eligibility?.status || scheme.eligibility_status || 'not_eligible'} />
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-1.5 text-sm text-gray-500">
                <Building2 className="w-4 h-4" />
                {scheme.ministry}
              </div>
              <BenefitBadge type={scheme.benefit_type} />
              {scheme.benefit_amount && (
                <span className="text-sm font-bold text-primary-700">{scheme.benefit_amount}</span>
              )}
            </div>

            {scheme.deadline && (
              <CountdownTimer date={scheme.deadline} />
            )}
          </div>
        </Card>

        {/* Description */}
        <Card>
          <CardTitle className="mb-3">About This Scheme</CardTitle>
          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{scheme.description_en}</p>
          {scheme.description_hi && (
            <p className="text-sm text-gray-500 leading-relaxed whitespace-pre-line mt-3 pt-3 border-t border-gray-100">
              {scheme.description_hi}
            </p>
          )}
        </Card>

        {/* Eligibility Criteria */}
        {eligibility && (
          <Card>
            <CardTitle className="mb-3">{t('schemes.eligibility_criteria')}</CardTitle>
            <div className="space-y-2">
              {eligibility.matched_rules?.map((rule, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0" />
                  <span className="text-gray-700">
                    <span className="font-medium capitalize">{rule.rule_type}:</span> {rule.rule_value}
                  </span>
                </div>
              ))}
              {eligibility.unmatched_rules?.map((rule, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <XCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
                  <span className="text-gray-500">
                    <span className="font-medium capitalize">{rule.rule_type}:</span> {rule.rule_value}
                    {rule.is_mandatory && <span className="text-red-500 ml-1">(Required)</span>}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Documents Required */}
        {scheme.documents_required?.length > 0 && (
          <Card>
            <CardTitle className="mb-3">{t('schemes.documents_required')}</CardTitle>
            <div className="space-y-2">
              {scheme.documents_required.map((doc, i) => (
                <div key={i} className="flex items-center gap-2 text-sm text-gray-700">
                  <FileText className="w-4 h-4 text-gray-400" />
                  <span className="capitalize">{doc.replace(/_/g, ' ')}</span>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* How to Apply */}
        {scheme.how_to_apply && (
          <Card>
            <CardTitle className="mb-3">{t('schemes.how_to_apply')}</CardTitle>
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{scheme.how_to_apply}</p>
          </Card>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            onClick={handleDownloadForm}
            loading={generateForm.isPending}
            icon={Download}
            className="flex-1"
            size="lg"
          >
            {t('schemes.download_form')}
          </Button>

          {scheme.apply_url && (
            <a href={scheme.apply_url} target="_blank" rel="noopener noreferrer" className="flex-1">
              <Button variant="secondary" icon={ExternalLink} className="w-full" size="lg">
                {t('schemes.apply_online')}
              </Button>
            </a>
          )}

          <Button variant="ghost" icon={Bell} onClick={handleSetReminder} loading={setReminder.isPending}>
            {t('schemes.set_reminder')}
          </Button>
        </div>

        {/* Source */}
        {scheme.source_url && (
          <p className="text-xs text-gray-400 text-center">
            Source:{' '}
            <a href={scheme.source_url} target="_blank" rel="noopener noreferrer" className="underline hover:text-primary-500">
              {scheme.source_url}
            </a>
          </p>
        )}
      </div>
  );
}
