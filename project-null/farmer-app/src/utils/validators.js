/**
 * Validate Indian phone number (10 digits, starts with 6-9)
 */
export function isValidPhone(phone) {
  if (!phone) return false;
  const digits = phone.replace(/\D/g, '');
  return /^[6-9]\d{9}$/.test(digits) || /^91[6-9]\d{9}$/.test(digits);
}

/**
 * Validate Indian PIN code (6 digits, first digit 1-9)
 */
export function isValidPinCode(pin) {
  if (!pin) return false;
  return /^[1-9]\d{5}$/.test(pin.trim());
}

/**
 * Validate email (basic)
 */
export function isValidEmail(email) {
  if (!email) return true; // email is optional
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
}

/**
 * Validate Aadhaar (12 digits)
 */
export function isValidAadhaar(aadhaar) {
  if (!aadhaar) return false;
  return /^\d{12}$/.test(aadhaar.replace(/\s/g, ''));
}

/**
 * Validate name (at least 2 chars, letters and spaces only)
 */
export function isValidName(name) {
  if (!name) return false;
  return /^[\p{L}\s.]{2,100}$/u.test(name.trim());
}

/**
 * Validate land area (positive number)
 */
export function isValidLandArea(area) {
  const num = Number(area);
  return !isNaN(num) && num > 0 && num < 10000;
}

/**
 * Validate IFSC code
 */
export function isValidIFSC(ifsc) {
  if (!ifsc) return false;
  return /^[A-Z]{4}0[A-Z0-9]{6}$/.test(ifsc.toUpperCase());
}

/**
 * Validate OTP (6 digits)
 */
export function isValidOTP(otp) {
  return /^\d{6}$/.test(otp);
}

/**
 * Normalize phone — extract 10 digit number
 */
export function normalizePhone(phone) {
  const digits = phone.replace(/\D/g, '');
  if (digits.length === 10) return digits;
  if (digits.length === 12 && digits.startsWith('91')) return digits.slice(2);
  return digits;
}
