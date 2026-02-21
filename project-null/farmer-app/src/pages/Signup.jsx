import { useState, useCallback } from 'react';
import { useNavigate, Link, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../services/authApi';
import toast from 'react-hot-toast';
import { QRCodeSVG } from 'qrcode.react';
import { Copy, Share2, ArrowLeft, X } from 'lucide-react';

import SignupStepper from '../components/auth/SignupStepper';
import OTPInput from '../components/auth/OTPInput';
import PhoneInput from '../components/auth/PhoneInput';
import LocationPicker from '../components/common/LocationPicker';
import Button from '../components/common/Button';
import {
  LAND_UNITS, CROPS, SEASONS, IRRIGATION_TYPES, OWNERSHIP_TYPES, INCOME_RANGES,
} from '../utils/constants';
import { isValidPhone, isValidName, isValidLandArea, isValidEmail, normalizePhone } from '../utils/validators';

const STEPS = ['Basic Info', 'Farm Details', 'Verify OTP', 'Welcome'];

/* ── Auto-detect current season ── */
function getCurrentSeason() {
  const month = new Date().getMonth() + 1;
  if (month >= 6 && month <= 10) return 'kharif';
  if (month >= 11 || month <= 3) return 'rabi';
  return 'zaid';
}

/* ── Popular crops shown first ── */
const POPULAR_CROPS = ['Rice', 'Wheat', 'Maize', 'Sugarcane', 'Cotton', 'Soybean', 'Groundnut', 'Mustard'];

export default function Signup() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated, setFarmerAfterSignup } = useAuth();

  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [farmerId, setFarmerId] = useState('');

  // Step 1 fields — Basic Info
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [pinCode, setPinCode] = useState('');
  const [location, setLocation] = useState(null);

  // Step 2 fields — Farm Details
  const [landArea, setLandArea] = useState('');
  const [landUnit, setLandUnit] = useState('acre');
  const [annualIncome, setAnnualIncome] = useState('');
  const [selectedCrops, setSelectedCrops] = useState([]);
  const [cropSeason, setCropSeason] = useState(getCurrentSeason());
  const [irrigationType, setIrrigationType] = useState('');
  const [ownershipType, setOwnershipType] = useState('');
  const [cropSearch, setCropSearch] = useState('');

  // Errors
  const [errors, setErrors] = useState({});

  const handleLocationResolved = useCallback((loc) => {
    setLocation(loc);
  }, []);

  if (isAuthenticated && step !== 4) return <Navigate to="/home" replace />;

  /* ── Crop management ── */
  const toggleCrop = (crop) => {
    setSelectedCrops((prev) =>
      prev.includes(crop) ? prev.filter((c) => c !== crop) : [...prev, crop]
    );
  };

  const filteredCrops = cropSearch
    ? CROPS.filter((c) => c.toLowerCase().includes(cropSearch.toLowerCase()))
    : [...POPULAR_CROPS, ...CROPS.filter((c) => !POPULAR_CROPS.includes(c))];

  /* ── Validation ── */
  const validateStep1 = () => {
    const newErrors = {};
    if (!isValidName(name)) newErrors.name = 'Please enter a valid name';
    if (!isValidPhone(phone)) newErrors.phone = 'Please enter a valid 10-digit phone number';
    if (email && !isValidEmail(email)) newErrors.email = 'Please enter a valid email';
    if (!pinCode || pinCode.length !== 6) newErrors.pinCode = 'Please enter a valid 6-digit PIN code';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    const newErrors = {};
    if (!isValidLandArea(landArea)) newErrors.landArea = 'Please enter a valid land area';
    if (selectedCrops.length === 0) newErrors.crops = 'Please select at least one crop';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleStep1Next = () => {
    if (validateStep1()) setStep(2);
  };

  const handleStep2Submit = async () => {
    if (!validateStep2()) return;

    setLoading(true);
    try {
      const cropsPayload = selectedCrops.map((crop) => ({
        crop_name: crop.toLowerCase(),
        season: cropSeason,
      }));

      const res = await authApi.signup({
        name: name.trim(),
        phone: normalizePhone(phone),
        email: email.trim() || undefined,
        pin_code: pinCode,
        land_area: parseFloat(landArea),
        land_unit: landUnit,
        annual_income: annualIncome ? parseFloat(annualIncome) : undefined,
        crops: cropsPayload,
        irrigation_type: irrigationType || undefined,
        ownership_type: ownershipType || undefined,
      });

      setFarmerId(res.data.farmer_id);
      toast.success(t('auth.otp_sent'));
      setStep(3);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Signup failed. Please try again.';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleOTPComplete = async (otpValue) => {
    setLoading(true);
    try {
      const verifyRes = await authApi.verifyOtp({
        phone: normalizePhone(phone),
        otp: otpValue,
        type: 'phone',
      });

      const tokens = verifyRes.data;

      setFarmerAfterSignup(
        {
          farmer_id: tokens.farmer_id || farmerId,
          name: name.trim(),
          phone: normalizePhone(phone),
          email: email.trim() || null,
          pin_code: pinCode,
          district: location?.district || '',
          state: location?.state || '',
          land_area: parseFloat(landArea),
          land_unit: landUnit,
          annual_income: annualIncome ? parseFloat(annualIncome) : null,
          crops: selectedCrops.map((c) => ({
            crop_name: c.toLowerCase(),
            season: cropSeason,
            is_active: true,
          })),
        },
        {
          access_token: tokens.access_token,
          refresh_token: tokens.refresh_token,
        }
      );

      toast.success('Phone verified successfully!');
      setStep(4);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Invalid OTP. Please try again.';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    try {
      await authApi.login({ phone: normalizePhone(phone) });
      toast.success('OTP resent!');
    } catch {
      toast.error('Failed to resend OTP. Try again later.');
    }
  };

  const copyFarmerId = () => {
    navigator.clipboard.writeText(farmerId);
    toast.success('Farmer ID copied!');
  };

  const shareOnWhatsApp = () => {
    const text = `My KisaanSeva Farmer ID: ${farmerId}\nSave this ID for accessing government schemes at service centers.`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white flex flex-col">
      {/* Header */}
      <header className="flex items-center gap-3 px-4 py-4">
        <button
          onClick={() => (step > 1 && step < 4 ? setStep(step - 1) : navigate('/'))}
          className="p-2 rounded-lg hover:bg-white/80 transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <h1 className="text-lg font-bold text-gray-900">{t('auth.signup_title')}</h1>
      </header>

      <div className="flex-1 flex items-start justify-center px-4 pt-4 pb-8">
        <div className="w-full max-w-md">
          <SignupStepper currentStep={step} steps={STEPS} />

          {/* ──────── Step 1: Basic Info ──────── */}
          {step === 1 && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">{t('auth.name')}</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter your full name"
                  className={`w-full px-4 py-2.5 border rounded-xl text-base focus:ring-2 focus:ring-primary-500 outline-none transition-all
                    ${errors.name ? 'border-red-400' : 'border-gray-300 focus:border-primary-500'}`}
                />
                {errors.name && <p className="text-sm text-red-500 mt-1">{errors.name}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">{t('auth.phone')}</label>
                <PhoneInput value={phone} onChange={setPhone} error={errors.phone} />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">{t('auth.email')}</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="email@example.com (optional)"
                  className={`w-full px-4 py-2.5 border rounded-xl text-base focus:ring-2 focus:ring-primary-500 outline-none transition-all
                    ${errors.email ? 'border-red-400' : 'border-gray-300 focus:border-primary-500'}`}
                />
                {errors.email && <p className="text-sm text-red-500 mt-1">{errors.email}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">{t('auth.pin_code')}</label>
                <LocationPicker value={pinCode} onChange={setPinCode} onLocationResolved={handleLocationResolved} />
                {errors.pinCode && <p className="text-sm text-red-500 mt-1">{errors.pinCode}</p>}
              </div>

              <Button onClick={handleStep1Next} className="w-full" size="lg">
                Next — Farm Details
              </Button>

              <p className="text-center text-sm text-gray-500">
                Already have an account?{' '}
                <Link to="/login" className="text-primary-600 font-medium hover:underline">Log in</Link>
              </p>
            </div>
          )}

          {/* ──────── Step 2: Farm Details ──────── */}
          {step === 2 && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-5">
              {/* Land Area */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">{t('auth.land_area')}</label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    value={landArea}
                    onChange={(e) => setLandArea(e.target.value)}
                    placeholder="e.g., 5"
                    min="0"
                    step="0.1"
                    className={`flex-1 px-4 py-2.5 border rounded-xl text-base focus:ring-2 focus:ring-primary-500 outline-none transition-all
                      ${errors.landArea ? 'border-red-400' : 'border-gray-300 focus:border-primary-500'}`}
                  />
                  <select
                    value={landUnit}
                    onChange={(e) => setLandUnit(e.target.value)}
                    className="px-3 py-2.5 border border-gray-300 rounded-xl text-sm font-medium bg-white focus:ring-2 focus:ring-primary-500 outline-none cursor-pointer"
                  >
                    {LAND_UNITS.map((u) => (
                      <option key={u.value} value={u.value}>{u.label_en}</option>
                    ))}
                  </select>
                </div>
                {errors.landArea && <p className="text-sm text-red-500 mt-1">{errors.landArea}</p>}
              </div>

              {/* Annual Income */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Annual Household Income
                  <span className="text-gray-400 font-normal ml-1">(helps match schemes)</span>
                </label>
                <select
                  value={annualIncome}
                  onChange={(e) => setAnnualIncome(e.target.value)}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-base bg-white focus:ring-2 focus:ring-primary-500 outline-none cursor-pointer"
                >
                  <option value="">Select income range</option>
                  {INCOME_RANGES.map((r) => (
                    <option key={r.value} value={r.value}>{r.label_en}</option>
                  ))}
                </select>
              </div>

              {/* Ownership Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Land Ownership</label>
                <div className="flex gap-2 flex-wrap">
                  {OWNERSHIP_TYPES.map((o) => (
                    <button
                      key={o.value}
                      type="button"
                      onClick={() => setOwnershipType(ownershipType === o.value ? '' : o.value)}
                      className={`px-4 py-2 rounded-xl text-sm font-medium border transition-all cursor-pointer
                        ${ownershipType === o.value
                          ? 'bg-primary-600 text-white border-primary-600'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-primary-300'}`}
                    >
                      {o.label_en}
                    </button>
                  ))}
                </div>
              </div>

              {/* Irrigation Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Irrigation Type</label>
                <div className="flex gap-2 flex-wrap">
                  {IRRIGATION_TYPES.map((i) => (
                    <button
                      key={i.value}
                      type="button"
                      onClick={() => setIrrigationType(irrigationType === i.value ? '' : i.value)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-all cursor-pointer
                        ${irrigationType === i.value
                          ? 'bg-primary-600 text-white border-primary-600'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-primary-300'}`}
                    >
                      {i.label_en}
                    </button>
                  ))}
                </div>
              </div>

              {/* Season (auto-detected) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Current Season
                  <span className="text-gray-400 font-normal ml-1">(auto-detected)</span>
                </label>
                <div className="flex gap-2">
                  {SEASONS.map((s) => (
                    <button
                      key={s.value}
                      type="button"
                      onClick={() => setCropSeason(s.value)}
                      className={`flex-1 py-2 rounded-xl text-sm font-medium border transition-all cursor-pointer
                        ${cropSeason === s.value
                          ? 'bg-primary-600 text-white border-primary-600'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-primary-300'}`}
                    >
                      {s.label_en}
                    </button>
                  ))}
                </div>
              </div>

              {/* Crop Selection — Multi-select */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Your Crops
                  <span className="text-gray-400 font-normal ml-1">(select all that apply)</span>
                </label>

                {/* Selected crops tags */}
                {selectedCrops.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-3">
                    {selectedCrops.map((crop) => (
                      <span
                        key={crop}
                        className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium"
                      >
                        {crop}
                        <button type="button" onClick={() => toggleCrop(crop)} className="hover:text-primary-600 cursor-pointer">
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}

                {/* Search */}
                <input
                  type="text"
                  value={cropSearch}
                  onChange={(e) => setCropSearch(e.target.value)}
                  placeholder="Search crops..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 outline-none mb-2"
                />

                {/* Crop grid */}
                <div className="max-h-40 overflow-y-auto border border-gray-200 rounded-xl p-2">
                  <div className="grid grid-cols-3 gap-1.5">
                    {filteredCrops.map((crop) => (
                      <button
                        key={crop}
                        type="button"
                        onClick={() => toggleCrop(crop)}
                        className={`px-2 py-1.5 rounded-lg text-xs font-medium border transition-all cursor-pointer truncate
                          ${selectedCrops.includes(crop)
                            ? 'bg-primary-600 text-white border-primary-600'
                            : 'bg-gray-50 text-gray-700 border-gray-200 hover:border-primary-300'}`}
                      >
                        {crop}
                      </button>
                    ))}
                  </div>
                </div>
                {errors.crops && <p className="text-sm text-red-500 mt-1">{errors.crops}</p>}
              </div>

              <Button onClick={handleStep2Submit} loading={loading} className="w-full" size="lg">
                {t('auth.signup')}
              </Button>
            </div>
          )}

          {/* ──────── Step 3: OTP Verification ──────── */}
          {step === 3 && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-6 text-center">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">{t('auth.enter_otp')}</h2>
                <p className="text-sm text-gray-500">
                  {t('auth.otp_sent')} <span className="font-medium text-gray-700">+91 {phone}</span>
                </p>
              </div>

              <OTPInput onComplete={handleOTPComplete} disabled={loading} />

              <Button variant="ghost" size="sm" onClick={handleResendOTP}>
                {t('auth.resend_otp')}
              </Button>
            </div>
          )}

          {/* ──────── Step 4: Welcome — Farmer ID ──────── */}
          {step === 4 && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-6 text-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('auth.welcome_title')}</h2>
                <p className="text-sm text-gray-500">{t('auth.save_id_note')}</p>
              </div>

              {/* Farmer ID Card */}
              <div className="bg-gradient-to-br from-primary-600 to-primary-800 rounded-2xl p-6 text-white shadow-lg">
                <p className="text-sm opacity-80 mb-1">{t('auth.your_farmer_id')}</p>
                <p className="text-3xl font-mono font-bold tracking-wider mb-4">{farmerId}</p>
                <div className="bg-white rounded-xl p-3 inline-block">
                  <QRCodeSVG value={farmerId} size={120} level="M" />
                </div>
                <p className="text-sm opacity-70 mt-3">{name}</p>
              </div>

              <div className="flex gap-3 justify-center">
                <Button variant="secondary" size="sm" icon={Copy} onClick={copyFarmerId}>
                  {t('auth.download_id')}
                </Button>
                <Button variant="secondary" size="sm" icon={Share2} onClick={shareOnWhatsApp}>
                  {t('auth.share_whatsapp')}
                </Button>
              </div>

              <Button onClick={() => navigate('/home')} className="w-full" size="lg">
                {t('auth.continue')}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
