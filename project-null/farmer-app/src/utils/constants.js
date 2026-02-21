export const SEASONS = [
  { value: 'kharif', label_en: 'Kharif', label_hi: 'खरीफ़' },
  { value: 'rabi', label_en: 'Rabi', label_hi: 'रबी' },
  { value: 'zaid', label_en: 'Zaid', label_hi: 'ज़ायद' },
];

export const LAND_UNITS = [
  { value: 'acre', label_en: 'Acres', label_hi: 'एकड़' },
  { value: 'hectare', label_en: 'Hectares', label_hi: 'हेक्टेयर' },
  { value: 'bigha', label_en: 'Bigha', label_hi: 'बीघा' },
];

export const CROPS = [
  'Wheat', 'Rice', 'Maize', 'Sugarcane', 'Cotton', 'Soybean',
  'Groundnut', 'Mustard', 'Jowar', 'Bajra', 'Ragi', 'Barley',
  'Gram (Chana)', 'Tur (Arhar)', 'Moong', 'Urad', 'Masoor',
  'Potato', 'Onion', 'Tomato', 'Brinjal', 'Okra',
  'Banana', 'Mango', 'Coconut', 'Tea', 'Coffee', 'Jute',
  'Turmeric', 'Chilli', 'Cumin', 'Coriander',
];

export const DOC_TYPES = [
  { value: 'aadhaar', label_en: 'Aadhaar Card', label_hi: 'आधार कार्ड' },
  { value: 'ration_card', label_en: 'Ration Card', label_hi: 'राशन कार्ड' },
  { value: 'land_proof', label_en: 'Land Ownership Proof', label_hi: 'भूमि स्वामित्व प्रमाण' },
  { value: 'bank_passbook', label_en: 'Bank Passbook', label_hi: 'बैंक पासबुक' },
  { value: 'photo', label_en: 'Passport Photo', label_hi: 'पासपोर्ट फोटो' },
];

export const IRRIGATION_TYPES = [
  { value: 'rainfed', label_en: 'Rain-fed', label_hi: 'वर्षा आधारित' },
  { value: 'canal', label_en: 'Canal', label_hi: 'नहर' },
  { value: 'borewell', label_en: 'Borewell', label_hi: 'बोरवेल' },
  { value: 'drip', label_en: 'Drip Irrigation', label_hi: 'ड्रिप सिंचाई' },
  { value: 'sprinkler', label_en: 'Sprinkler', label_hi: 'स्प्रिंकलर' },
];

export const OWNERSHIP_TYPES = [
  { value: 'owned', label_en: 'Owned', label_hi: 'स्वामित्व' },
  { value: 'leased', label_en: 'Leased', label_hi: 'पट्टे पर' },
  { value: 'shared', label_en: 'Shared', label_hi: 'साझा' },
];

export const INCOME_RANGES = [
  { value: 50000, label_en: 'Up to ₹50,000', label_hi: '₹50,000 तक' },
  { value: 100000, label_en: 'Up to ₹1,00,000', label_hi: '₹1,00,000 तक' },
  { value: 200000, label_en: 'Up to ₹2,00,000', label_hi: '₹2,00,000 तक' },
  { value: 300000, label_en: '₹2,00,000 - ₹3,00,000', label_hi: '₹2,00,000 - ₹3,00,000' },
  { value: 500000, label_en: '₹3,00,000 - ₹5,00,000', label_hi: '₹3,00,000 - ₹5,00,000' },
  { value: 800000, label_en: '₹5,00,000 - ₹8,00,000', label_hi: '₹5,00,000 - ₹8,00,000' },
  { value: 1000000, label_en: 'Above ₹8,00,000', label_hi: '₹8,00,000 से अधिक' },
];

export const SUBSIDY_CATEGORIES = [
  { value: 'seed', label_en: 'Seeds', label_hi: 'बीज' },
  { value: 'fertilizer', label_en: 'Fertilizer', label_hi: 'उर्वरक' },
  { value: 'equipment', label_en: 'Equipment', label_hi: 'उपकरण' },
  { value: 'irrigation', label_en: 'Irrigation', label_hi: 'सिंचाई' },
  { value: 'organic', label_en: 'Organic Farming', label_hi: 'जैविक खेती' },
  { value: 'credit', label_en: 'Credit / Loan', label_hi: 'ऋण' },
];

export const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
  'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu',
  'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry',
];

export const BENEFIT_TYPES = {
  cash: { label: 'Cash Transfer', color: 'text-green-700 bg-green-100' },
  subsidy: { label: 'Subsidy', color: 'text-blue-700 bg-blue-100' },
  insurance: { label: 'Insurance', color: 'text-purple-700 bg-purple-100' },
  equipment: { label: 'Equipment', color: 'text-orange-700 bg-orange-100' },
};

export const ELIGIBILITY_STATUS = {
  eligible: { label: 'Eligible', color: 'bg-green-100 text-green-800 border-green-300' },
  partial: { label: 'Partial Match', color: 'bg-yellow-100 text-yellow-800 border-yellow-300' },
  not_eligible: { label: 'Not Eligible', color: 'bg-red-100 text-red-800 border-red-300' },
};
