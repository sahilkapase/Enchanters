import { Phone } from 'lucide-react';

export default function PhoneInput({ value, onChange, disabled = false, error = '' }) {
  const handleChange = (e) => {
    const val = e.target.value.replace(/\D/g, '').slice(0, 10);
    onChange?.(val);
  };

  return (
    <div className="space-y-1">
      <div className="relative">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 flex items-center gap-1.5 text-gray-500">
          <Phone className="w-4 h-4" />
          <span className="text-sm font-medium">+91</span>
        </div>
        <input
          type="tel"
          inputMode="numeric"
          maxLength={10}
          value={value}
          onChange={handleChange}
          disabled={disabled}
          placeholder="98765 43210"
          className={`w-full pl-20 pr-4 py-2.5 border rounded-xl text-base
                     focus:ring-2 focus:ring-primary-500 outline-none transition-all
                     ${error ? 'border-red-400 focus:border-red-500' : 'border-gray-300 focus:border-primary-500'}
                     disabled:bg-gray-100 disabled:text-gray-500`}
        />
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  );
}
