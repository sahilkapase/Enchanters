import { useState, useRef, useEffect } from 'react';

export default function OTPInput({ length = 6, onComplete, disabled = false }) {
  const [values, setValues] = useState(new Array(length).fill(''));
  const inputsRef = useRef([]);

  useEffect(() => {
    inputsRef.current[0]?.focus();
  }, []);

  const handleChange = (index, e) => {
    const val = e.target.value;
    if (!/^\d*$/.test(val)) return;

    const newValues = [...values];
    newValues[index] = val.slice(-1);
    setValues(newValues);

    // Move to next input
    if (val && index < length - 1) {
      inputsRef.current[index + 1]?.focus();
    }

    // Check if complete
    const otp = newValues.join('');
    if (otp.length === length && !newValues.includes('')) {
      onComplete?.(otp);
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !values[index] && index > 0) {
      inputsRef.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, length);
    if (!pasted) return;

    const newValues = [...values];
    for (let i = 0; i < pasted.length; i++) {
      newValues[i] = pasted[i];
    }
    setValues(newValues);

    const nextEmpty = newValues.findIndex((v) => !v);
    const focusIndex = nextEmpty === -1 ? length - 1 : nextEmpty;
    inputsRef.current[focusIndex]?.focus();

    if (pasted.length === length) {
      onComplete?.(pasted);
    }
  };

  return (
    <div className="flex gap-2 justify-center">
      {values.map((val, i) => (
        <input
          key={i}
          ref={(el) => (inputsRef.current[i] = el)}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={val}
          onChange={(e) => handleChange(i, e)}
          onKeyDown={(e) => handleKeyDown(i, e)}
          onPaste={i === 0 ? handlePaste : undefined}
          disabled={disabled}
          className="w-12 h-14 text-center text-xl font-bold border-2 border-gray-300 rounded-xl
                     focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none
                     transition-all disabled:bg-gray-100 disabled:text-gray-400"
        />
      ))}
    </div>
  );
}
