import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { useFarmerProfile, useUpdateProfile, useUpdateExtendedProfile, useGeneratedForms } from '../hooks/useFarmer';
import Card, { CardTitle, CardDescription } from '../components/common/Card';
import Button from '../components/common/Button';
import { PageLoader } from '../components/common/Loader';
import FarmerIDCard from '../components/profile/FarmerIDCard';
import DocumentUpload from '../components/profile/DocumentUpload';
import CropManager from '../components/profile/CropManager';
import AccessLog from '../components/profile/AccessLog';
import {
  User, MapPin, Droplets, Landmark, FileText,
  Save, LogOut, ChevronDown, ChevronUp, Globe, Bell, Download
} from 'lucide-react';
import { LAND_UNITS, IRRIGATION_TYPES, OWNERSHIP_TYPES, INDIAN_STATES, INCOME_RANGES } from '../utils/constants';
import { formatDate } from '../utils/formatters';
import toast from 'react-hot-toast';

/* ── Section Accordion ── */
function Section({ title, icon: Icon, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <Card>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between"
      >
        <div className="flex items-center gap-2">
          {Icon && <Icon className="w-5 h-5 text-primary-600" />}
          <CardTitle>{title}</CardTitle>
        </div>
        {open ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
      </button>
      {open && <div className="mt-4 pt-4 border-t border-gray-100">{children}</div>}
    </Card>
  );
}

/* ── Form field helper ── */
function Field({ label, children, className = '' }) {
  return (
    <label className={`block ${className}`}>
      <span className="text-sm font-medium text-gray-700">{label}</span>
      <div className="mt-1">{children}</div>
    </label>
  );
}

const inputCls = 'w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none';
const selectCls = inputCls;

/* ── Main Profile Page ── */
export default function Profile() {
  const { t } = useTranslation();
  const { farmer, logout } = useAuth();
  const { language, setLanguage, languages } = useLanguage();
  const { data: profile, isLoading } = useFarmerProfile();
  const { data: forms = [] } = useGeneratedForms();
  const updateProfile = useUpdateProfile();
  const updateExtendedProfile = useUpdateExtendedProfile();

  /* editable personal fields */
  const [editing, setEditing] = useState(false);
  const [personal, setPersonal] = useState(null);

  /* editable farm fields */
  const [editingFarm, setEditingFarm] = useState(false);
  const [farm, setFarm] = useState(null);

  /* notifications preference (local only for now) */
  const [smsNotif, setSmsNotif] = useState(true);

  if (isLoading) return <PageLoader />;

  const p = profile || farmer;

  /* ── init personal form state ── */
  const startEditPersonal = () => {
    setPersonal({
      name: p.name || '',
      email: p.email || '',
      pin_code: p.pin_code || '',
      state: p.state || '',
      district: p.district || '',
    });
    setEditing(true);
  };

  const savePersonal = async () => {
    try {
      await updateProfile.mutateAsync(personal);
      toast.success('Profile updated');
      setEditing(false);
    } catch {
      toast.error('Failed to update profile');
    }
  };

  /* ── init farm form state ── */
  const startEditFarm = () => {
    setFarm({
      land_area: p.land_area ?? '',
      land_unit: p.land_unit || 'acre',
      annual_income: p.annual_income ?? '',
      irrigation_type: p.profile?.irrigation_type || '',
      ownership_type: p.profile?.ownership_type || '',
    });
    setEditingFarm(true);
  };

  const saveFarm = async () => {
    try {
      // Basic land info + income → PATCH /farmers/me
      await updateProfile.mutateAsync({
        land_area: parseFloat(farm.land_area) || 0,
        land_unit: farm.land_unit,
        annual_income: farm.annual_income ? parseFloat(farm.annual_income) : undefined,
      });
      // Extended profile → PUT /farmers/me/profile
      if (farm.irrigation_type || farm.ownership_type) {
        await updateExtendedProfile.mutateAsync({
          irrigation_type: farm.irrigation_type || undefined,
          ownership_type: farm.ownership_type || undefined,
        });
      }
      toast.success('Farm details updated');
      setEditingFarm(false);
    } catch {
      toast.error('Failed to update farm details');
    }
  };

  return (
    <div className="space-y-5 pb-24">
      {/* ── Header ── */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('profile.title')}</h1>
        <p className="text-sm text-gray-500 mt-1">{t('profile.subtitle')}</p>
      </div>

      {/* ── Farmer ID Card ── */}
      <FarmerIDCard farmerId={p.farmer_id} name={p.name} />

      {/* ── Personal Details ── */}
      <Section title={t('profile.personal_details')} icon={User} defaultOpen>
        {editing ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Field label={t('profile.full_name')}>
                <input
                  className={inputCls}
                  value={personal.name}
                  onChange={(e) => setPersonal({ ...personal, name: e.target.value })}
                />
              </Field>
              <Field label={t('profile.phone')}>
                <input className={`${inputCls} bg-gray-50`} value={p.phone} disabled />
              </Field>
              <Field label={t('profile.email')}>
                <input
                  type="email"
                  className={inputCls}
                  value={personal.email}
                  onChange={(e) => setPersonal({ ...personal, email: e.target.value })}
                  placeholder="optional"
                />
              </Field>
              <Field label={t('profile.pin_code')}>
                <input
                  className={inputCls}
                  value={personal.pin_code}
                  maxLength={6}
                  onChange={(e) => setPersonal({ ...personal, pin_code: e.target.value.replace(/\D/g, '') })}
                />
              </Field>
              <Field label={t('profile.state')}>
                <select
                  className={selectCls}
                  value={personal.state}
                  onChange={(e) => setPersonal({ ...personal, state: e.target.value })}
                >
                  <option value="">Select</option>
                  {INDIAN_STATES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </Field>
              <Field label={t('profile.district')}>
                <input
                  className={inputCls}
                  value={personal.district}
                  onChange={(e) => setPersonal({ ...personal, district: e.target.value })}
                />
              </Field>
            </div>
            <div className="flex gap-3">
              <Button onClick={savePersonal} loading={updateProfile.isPending}>
                <Save className="w-4 h-4 mr-1" /> Save
              </Button>
              <Button variant="ghost" onClick={() => setEditing(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <InfoRow label={t('profile.full_name')} value={p.name} />
            <InfoRow label={t('profile.phone')} value={p.phone} />
            <InfoRow label={t('profile.email')} value={p.email || '—'} />
            <InfoRow label={t('profile.pin_code')} value={p.pin_code} />
            <InfoRow label={t('profile.state')} value={p.state || '—'} />
            <InfoRow label={t('profile.district')} value={p.district || '—'} />
            <Button variant="secondary" size="sm" onClick={startEditPersonal}>Edit</Button>
          </div>
        )}
      </Section>

      {/* ── Farm Details ── */}
      <Section title={t('profile.farm_details')} icon={MapPin}>
        {editingFarm ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Field label={t('profile.land_area')}>
                <div className="flex gap-2">
                  <input
                    type="number"
                    className={`${inputCls} flex-1`}
                    value={farm.land_area}
                    onChange={(e) => setFarm({ ...farm, land_area: e.target.value })}
                    min="0"
                    step="0.01"
                  />
                  <select
                    className={`${selectCls} w-28`}
                    value={farm.land_unit}
                    onChange={(e) => setFarm({ ...farm, land_unit: e.target.value })}
                  >
                    {LAND_UNITS.map((u) => <option key={u.value} value={u.value}>{u.label_en}</option>)}
                  </select>
                </div>
              </Field>
              <Field label={t('profile.irrigation')}>
                <select
                  className={selectCls}
                  value={farm.irrigation_type}
                  onChange={(e) => setFarm({ ...farm, irrigation_type: e.target.value })}
                >
                  <option value="">Select</option>
                  {IRRIGATION_TYPES.map((i) => <option key={i.value} value={i.value}>{i.label_en}</option>)}
                </select>
              </Field>
              <Field label="Annual Income">
                <select
                  className={selectCls}
                  value={farm.annual_income}
                  onChange={(e) => setFarm({ ...farm, annual_income: e.target.value })}
                >
                  <option value="">Select</option>
                  {INCOME_RANGES.map((r) => <option key={r.value} value={r.value}>{r.label_en}</option>)}
                </select>
              </Field>
              <Field label={t('profile.ownership')}>
                <select
                  className={selectCls}
                  value={farm.ownership_type}
                  onChange={(e) => setFarm({ ...farm, ownership_type: e.target.value })}
                >
                  <option value="">Select</option>
                  {OWNERSHIP_TYPES.map((o) => <option key={o.value} value={o.value}>{o.label_en}</option>)}
                </select>
              </Field>
            </div>
            <div className="flex gap-3">
              <Button onClick={saveFarm} loading={updateProfile.isPending}>
                <Save className="w-4 h-4 mr-1" /> Save
              </Button>
              <Button variant="ghost" onClick={() => setEditingFarm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <InfoRow label={t('profile.land_area')} value={p.land_area ? `${p.land_area} ${p.land_unit || 'acre'}` : '—'} />
            <InfoRow label="Annual Income" value={p.annual_income ? `₹${Number(p.annual_income).toLocaleString('en-IN')}` : '—'} />
            <InfoRow label={t('profile.irrigation')} value={p.profile?.irrigation_type || '—'} />
            <InfoRow label={t('profile.ownership')} value={p.profile?.ownership_type || '—'} />
            <Button variant="secondary" size="sm" onClick={startEditFarm}>Edit</Button>
          </div>
        )}
      </Section>

      {/* ── Crops ── */}
      <Section title={t('profile.crops')} icon={Droplets}>
        <CropManager />
      </Section>

      {/* ── Documents ── */}
      <Section title={t('profile.documents')} icon={FileText}>
        <DocumentUpload />
      </Section>

      {/* ── Generated Forms ── */}
      <Section title={t('profile.generated_forms')} icon={Landmark}>
        {forms.length === 0 ? (
          <p className="text-sm text-gray-500">No forms generated yet. Check scheme eligibility to generate pre-filled forms.</p>
        ) : (
          <div className="space-y-2">
            {forms.map((f) => (
              <div key={f.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-gray-800">{f.file_name || 'Form'}</p>
                  <p className="text-xs text-gray-500">{formatDate(f.generated_at)}</p>
                </div>
                <a
                  href={f.download_url || `/api/v1/files/${f.file_key}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:text-primary-700"
                  title="Download"
                >
                  <Download className="w-5 h-5" />
                </a>
              </div>
            ))}
          </div>
        )}
      </Section>

      {/* ── Access Log ── */}
      <Section title={t('profile.access_log')} icon={Landmark}>
        <AccessLog />
      </Section>

      {/* ── Preferences ── */}
      <Section title={t('profile.preferences')} icon={Globe}>
        <div className="space-y-4">
          <Field label={t('profile.language')}>
            <select
              className={selectCls}
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              {languages.map((l) => (
                <option key={l.code} value={l.code}>{l.label}</option>
              ))}
            </select>
          </Field>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bell className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-700">SMS Notifications</span>
            </div>
            <button
              onClick={() => setSmsNotif(!smsNotif)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                smsNotif ? 'bg-primary-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  smsNotif ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </Section>

      {/* ── Logout ── */}
      <div className="pt-2">
        <Button variant="danger" className="w-full" onClick={logout}>
          <LogOut className="w-4 h-4 mr-2" />
          {t('profile.logout')}
        </Button>
      </div>
    </div>
  );
}

/* small read-only row */
function InfoRow({ label, value }) {
  return (
    <div className="flex justify-between items-center text-sm">
      <span className="text-gray-500">{label}</span>
      <span className="text-gray-900 font-medium">{value}</span>
    </div>
  );
}
