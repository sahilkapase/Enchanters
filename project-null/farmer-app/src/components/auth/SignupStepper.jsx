import { Check } from 'lucide-react';

export default function SignupStepper({ currentStep, steps }) {
  return (
    <div className="flex items-center justify-center gap-2 mb-8">
      {steps.map((step, index) => {
        const stepNum = index + 1;
        const isActive = stepNum === currentStep;
        const isCompleted = stepNum < currentStep;

        return (
          <div key={stepNum} className="flex items-center gap-2">
            <div
              className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all
                ${isCompleted
                  ? 'bg-primary-600 text-white'
                  : isActive
                  ? 'bg-primary-100 text-primary-700 ring-2 ring-primary-500'
                  : 'bg-gray-100 text-gray-400'
                }
              `}
            >
              {isCompleted ? <Check className="w-4 h-4" /> : stepNum}
            </div>
            <span
              className={`text-sm font-medium hidden sm:inline ${
                isActive ? 'text-primary-700' : isCompleted ? 'text-primary-600' : 'text-gray-400'
              }`}
            >
              {step}
            </span>
            {index < steps.length - 1 && (
              <div className={`w-8 h-0.5 ${isCompleted ? 'bg-primary-500' : 'bg-gray-200'}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
