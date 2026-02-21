import { useState } from 'react';
import { useNavigate, Link, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../services/authApi';
import toast from 'react-hot-toast';
import { ArrowLeft } from 'lucide-react';

import PhoneInput from '../components/auth/PhoneInput';
import OTPInput from '../components/auth/OTPInput';
import Button from '../components/common/Button';
import { isValidPhone, normalizePhone } from '../utils/validators';

export default function Login() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated, loginWithTokens } = useAuth();

  const [step, setStep] = useState('phone'); // 'phone' | 'otp'
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) return <Navigate to="/home" replace />;

  const handleRequestOTP = async () => {
    if (!isValidPhone(phone)) {
      toast.error('Please enter a valid 10-digit phone number');
      return;
    }

    setLoading(true);
    try {
      await authApi.login({ phone: normalizePhone(phone) });
      toast.success(t('auth.otp_sent'));
      setStep('otp');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to send OTP. Please try again.';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleOTPComplete = async (otp) => {
    setLoading(true);
    try {
      const res = await authApi.loginVerify({
        phone: normalizePhone(phone),
        otp,
      });

      await loginWithTokens(res.data);
      toast.success('Welcome back!');
      navigate('/home', { replace: true });
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
      toast.error('Failed to resend OTP.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white flex flex-col">
      {/* Header */}
      <header className="flex items-center gap-3 px-4 py-4">
        <Link to="/" className="p-2 rounded-lg hover:bg-white/80 transition-colors">
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <h1 className="text-lg font-bold text-gray-900">{t('auth.login_title')}</h1>
      </header>

      <div className="flex-1 flex items-center justify-center px-4 pb-8">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-primary-600 flex items-center justify-center mx-auto mb-3">
              <span className="text-white font-bold text-2xl">KS</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">{t('auth.login_title')}</h2>
          </div>

          {step === 'phone' && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  {t('auth.login_with_phone')}
                </label>
                <PhoneInput value={phone} onChange={setPhone} />
              </div>

              <Button onClick={handleRequestOTP} loading={loading} className="w-full" size="lg">
                {t('auth.login')}
              </Button>

              <p className="text-center text-sm text-gray-500">
                Don&apos;t have an account?{' '}
                <Link to="/signup" className="text-primary-600 font-medium hover:underline">Sign up</Link>
              </p>
            </div>
          )}

          {step === 'otp' && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-6 text-center">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{t('auth.enter_otp')}</h3>
                <p className="text-sm text-gray-500">
                  {t('auth.otp_sent')} <span className="font-medium text-gray-700">+91 {phone}</span>
                </p>
              </div>

              <OTPInput onComplete={handleOTPComplete} disabled={loading} />

              <div className="flex items-center justify-center gap-4">
                <Button variant="ghost" size="sm" onClick={handleResendOTP}>
                  {t('auth.resend_otp')}
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setStep('phone')}>
                  Change Number
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
