import { useState, useEffect } from 'react';
import { usePinCodeLookup } from '../../hooks/useLocation';
import { MapPin, Loader2, CheckCircle2, XCircle } from 'lucide-react';

export default function LocationPicker({ value, onChange, onLocationResolved }) {
  const [pinCode, setPinCode] = useState(value || '');
  const { data: location, isLoading, isError } = usePinCodeLookup(pinCode);

  useEffect(() => {
    if (location) {
      onLocationResolved?.(location);
    }
  }, [location, onLocationResolved]);

  const handleChange = (e) => {
    const val = e.target.value.replace(/\D/g, '').slice(0, 6);
    setPinCode(val);
    onChange?.(val);
  };

  return (
    <div className="space-y-2">
      <div className="relative">
        <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          inputMode="numeric"
          maxLength={6}
          value={pinCode}
          onChange={handleChange}
          placeholder="Enter 6-digit PIN code"
          className="w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-xl text-base
                     focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
        />
        <div className="absolute right-3 top-1/2 -translate-y-1/2">
          {isLoading && <Loader2 className="w-4 h-4 text-primary-500 animate-spin" />}
          {location && !isLoading && <CheckCircle2 className="w-4 h-4 text-green-500" />}
          {isError && pinCode.length === 6 && <XCircle className="w-4 h-4 text-red-500" />}
        </div>
      </div>

      {location && (
        <div className="flex items-center gap-2 text-sm text-primary-700 bg-primary-50 px-3 py-2 rounded-lg">
          <MapPin className="w-3.5 h-3.5" />
          <span>{location.district}, {location.state}</span>
        </div>
      )}

      {isError && pinCode.length === 6 && (
        <p className="text-sm text-red-500">Could not resolve PIN code. Please check and try again.</p>
      )}
    </div>
  );
}
