import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useInsurancePlans, useGenerateInsuranceForm } from '../hooks/useInsurance';
import InsurancePlanCard from '../components/insurance/InsurancePlanCard';
import Card, { CardTitle } from '../components/common/Card';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import EmptyState from '../components/common/EmptyState';
import { PageLoader } from '../components/common/Loader';
import { Download, ChevronDown, ChevronUp, Shield } from 'lucide-react';
import toast from 'react-hot-toast';

const FAQ_ITEMS = [
  {
    q: 'What to do after crop damage?',
    a: 'Report crop damage to your insurance company or nearest agriculture office within 72 hours. You can also report on the PMFBY app or by calling the crop insurance helpline 1800-180-1551.',
  },
  {
    q: 'Documents needed for claim',
    a: 'You will need: 1) Insurance policy copy, 2) Aadhaar card, 3) Bank passbook, 4) Land records, 5) Crop damage photos, 6) Loss assessment report from agriculture officer.',
  },
  {
    q: 'How long does claim settlement take?',
    a: 'Insurance companies are required to settle claims within 2 months of harvesting. For prevented sowing, claims should be settled within 45 days of the season end.',
  },
  {
    q: 'Helpline numbers',
    a: 'PMFBY Helpline: 1800-180-1551 (toll-free). You can also contact your district agriculture officer or visit the nearest CSC center.',
  },
];

export default function Insurance() {
  const { t } = useTranslation();
  const { data: plans, isLoading } = useInsurancePlans();
  const generateForm = useGenerateInsuranceForm();

  const [selectedPlan, setSelectedPlan] = useState(null);
  const [expandedFaq, setExpandedFaq] = useState(null);

  const handleDownloadForm = (planId) => {
    generateForm.mutate(planId, {
      onSuccess: () => toast.success('Form downloaded!'),
      onError: () => toast.error('Failed to generate form'),
    });
  };

  return (
      <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">{t('insurance.title')}</h1>

        {/* Insurance Plans */}
        <div>
          <h2 className="text-lg font-bold text-gray-900 mb-4">{t('insurance.plans')}</h2>

          {isLoading && <PageLoader />}

          {!isLoading && plans?.length === 0 && (
            <EmptyState icon={Shield} title="No insurance plans available" />
          )}

          {!isLoading && plans?.length > 0 && (
            <div className="grid md:grid-cols-2 gap-4">
              {plans.map((plan) => (
                <InsurancePlanCard
                  key={plan.id}
                  plan={plan}
                  onViewDetail={setSelectedPlan}
                />
              ))}
            </div>
          )}
        </div>

        {/* How to Claim — FAQ */}
        <Card>
          <CardTitle className="mb-4">{t('insurance.how_to_claim')}</CardTitle>
          <div className="space-y-2">
            {FAQ_ITEMS.map((item, i) => (
              <div key={i} className="border border-gray-100 rounded-xl overflow-hidden">
                <button
                  onClick={() => setExpandedFaq(expandedFaq === i ? null : i)}
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors cursor-pointer"
                >
                  <span className="text-sm font-semibold text-gray-900">{item.q}</span>
                  {expandedFaq === i ? (
                    <ChevronUp className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  )}
                </button>
                {expandedFaq === i && (
                  <div className="px-4 pb-4 text-sm text-gray-600 leading-relaxed">
                    {item.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>

        {/* Plan Detail Modal */}
        <Modal isOpen={!!selectedPlan} onClose={() => setSelectedPlan(null)} title={selectedPlan?.name_en} size="lg">
          {selectedPlan && (
            <div className="space-y-4">
              {selectedPlan.description_en && (
                <p className="text-sm text-gray-700 leading-relaxed">{selectedPlan.description_en}</p>
              )}
              {selectedPlan.coverage && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-1">Coverage</h4>
                  <p className="text-sm text-gray-600">{selectedPlan.coverage}</p>
                </div>
              )}
              {selectedPlan.eligibility && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-1">Eligibility</h4>
                  <p className="text-sm text-gray-600">{selectedPlan.eligibility}</p>
                </div>
              )}
              {selectedPlan.how_to_enroll && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-1">How to Enroll</h4>
                  <p className="text-sm text-gray-600 whitespace-pre-line">{selectedPlan.how_to_enroll}</p>
                </div>
              )}
              <Button
                onClick={() => handleDownloadForm(selectedPlan.id)}
                loading={generateForm.isPending}
                icon={Download}
                className="w-full"
              >
                {t('insurance.download_form')}
              </Button>
            </div>
          )}
        </Modal>
      </div>
  );
}
