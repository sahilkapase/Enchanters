import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  lookupFarmer,
  requestAccess,
  verifyAccess,
  endSession,
  getSessionFarmer,
  generateFormForSession,
} from '../services/api';
import {
  User, MapPin, Phone, Droplets, FileText, Shield,
  AlertCircle, Download, ArrowLeft,
  Clock, Loader2, Play, Square,
} from 'lucide-react';
import toast from 'react-hot-toast';

/* ── Tab definitions ── */
const TABS = [
  { key: 'overview', label: 'Overview', icon: User },
  { key: 'schemes', label: 'Schemes', icon: Shield },
  { key: 'documents', label: 'Documents', icon: FileText },
];

export default function FarmerView() {
  const { farmerId } = useParams();
  const navigate = useNavigate();
  const [tab, setTab] = useState('overview');
  const [sessionId, setSessionId] = useState(null);
  const [purpose, setPurpose] = useState('');
  const [showPurpose, setShowPurpose] = useState(false);
  const [awaitingOtp, setAwaitingOtp] = useState(false);
  const [otp, setOtp] = useState('');

  /* ── Data queries ── */
  const { data: farmer, isLoading } = useQuery({
    queryKey: ['agent-farmer', farmerId],
    queryFn: () => lookupFarmer(farmerId),
  });

  /* Session-based farmer data (schemes, docs, etc.) */
  const { data: sessionFarmer } = useQuery({
    queryKey: ['agent-session-farmer', sessionId],
    queryFn: () => getSessionFarmer(sessionId),
    enabled: !!sessionId,
  });

  const schemes = sessionFarmer?.schemes || [];
  const documents = sessionFarmer?.documents || [];

  /* ── Session management (consent-based) ── */
  const requestMutation = useMutation({
    mutationFn: () => requestAccess(farmerId, purpose),
    onSuccess: () => {
      setAwaitingOtp(true);
      toast.success('OTP sent to farmer\'s phone for consent');
    },
    onError: () => toast.error('Failed to request access'),
  });

  const verifyMutation = useMutation({
    mutationFn: () => verifyAccess(farmerId, otp),
    onSuccess: (data) => {
      setSessionId(data.session_id);
      setAwaitingOtp(false);
      setShowPurpose(false);
      setOtp('');
      toast.success('Session started — farmer data is now accessible');
    },
    onError: () => toast.error('Invalid OTP — please try again'),
  });

  const endMutation = useMutation({
    mutationFn: () => endSession(sessionId),
    onSuccess: () => {
      setSessionId(null);
      toast.success('Session ended');
    },
    onError: () => toast.error('Failed to end session'),
  });

  /* ── Form generation ── */
  const generateForm = useMutation({
    mutationFn: (payload) => generateFormForSession(sessionId, payload),
    onSuccess: () => {
      toast.success('Form generated');
    },
    onError: () => toast.error('Failed to generate form'),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
      </div>
    );
  }

  if (!farmer) {
    return (
      <div className="text-center py-20">
        <User className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">Farmer not found.</p>
        <button onClick={() => navigate('/lookup')} className="text-primary-600 text-sm mt-2 hover:underline">
          Go back to search
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header + Back */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/lookup')}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{farmer.name}</h1>
          <p className="font-mono text-sm text-primary-600">{farmer.farmer_id}</p>
        </div>

        {/* Session control */}
        {!sessionId ? (
          showPurpose ? (
            <div className="flex items-center gap-2">
              {!awaitingOtp ? (
                <>
                  <input
                    className="rounded-lg border border-gray-300 px-3 py-2 text-sm w-60 focus:ring-2 focus:ring-primary-500 outline-none"
                    placeholder="Purpose of access (e.g., scheme application)"
                    value={purpose}
                    onChange={(e) => setPurpose(e.target.value)}
                  />
                  <button
                    onClick={() => requestMutation.mutate()}
                    disabled={!purpose.trim() || requestMutation.isPending}
                    className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 flex items-center gap-1"
                  >
                    {requestMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                    Request
                  </button>
                </>
              ) : (
                <>
                  <input
                    className="rounded-lg border border-gray-300 px-3 py-2 text-sm w-40 font-mono tracking-widest focus:ring-2 focus:ring-primary-500 outline-none"
                    placeholder="Enter OTP"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    maxLength={6}
                  />
                  <button
                    onClick={() => verifyMutation.mutate()}
                    disabled={otp.length < 4 || verifyMutation.isPending}
                    className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 flex items-center gap-1"
                  >
                    {verifyMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                    Verify
                  </button>
                </>
              )}
              <button
                onClick={() => { setShowPurpose(false); setAwaitingOtp(false); setOtp(''); }}
                className="text-gray-400 hover:text-gray-600 text-sm"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowPurpose(true)}
              className="bg-primary-600 hover:bg-primary-700 text-white px-5 py-2 rounded-lg text-sm font-medium flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              Start Session
            </button>
          )
        ) : (
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1 text-sm text-green-600 font-medium">
              <Clock className="w-4 h-4" /> Session Active
            </span>
            <button
              onClick={() => endMutation.mutate()}
              disabled={endMutation.isPending}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-1"
            >
              <Square className="w-4 h-4" /> End Session
            </button>
          </div>
        )}
      </div>

      {/* No session notice */}
      {!sessionId && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <p className="text-sm text-amber-800">
            <strong>Start a session</strong> to access farmer's schemes, insurance, and documents.
            All access is logged for the farmer's transparency.
          </p>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              tab === key
                ? 'bg-white text-primary-700 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        {tab === 'overview' && <OverviewTab farmer={farmer} />}
        {tab === 'schemes' && (
          sessionId
            ? <SchemesTab schemes={schemes} onGenerate={(s) => generateForm.mutate({ scheme_id: s.id })} generating={generateForm.isPending} />
            : <SessionRequired />
        )}
        {tab === 'documents' && (
          sessionId
            ? <DocumentsTab documents={documents} />
            : <SessionRequired />
        )}
      </div>
    </div>
  );
}

/* ── Sub-components ── */

function SessionRequired() {
  return (
    <div className="text-center py-12">
      <Shield className="w-10 h-10 text-amber-400 mx-auto mb-3" />
      <p className="text-gray-600 font-medium">Session required</p>
      <p className="text-sm text-gray-400 mt-1">Start a session to access this data.</p>
    </div>
  );
}

function OverviewTab({ farmer }) {
  const rows = [
    { label: 'Phone', value: farmer.phone, icon: Phone },
    { label: 'PIN Code', value: farmer.pin_code },
    { label: 'District', value: farmer.district, icon: MapPin },
    { label: 'State', value: farmer.state },
    { label: 'Land Area', value: farmer.land_area ? `${farmer.land_area} ${farmer.land_unit || 'acre'}` : '—' },
    { label: 'Irrigation', value: farmer.profile?.irrigation_type || '—', icon: Droplets },
    { label: 'Ownership', value: farmer.profile?.ownership_type || '—' },
    { label: 'Crops', value: farmer.crops?.map(c => c.crop_name).join(', ') || '—' },
    { label: 'Registered', value: farmer.created_at ? new Date(farmer.created_at).toLocaleDateString('en-IN') : '—' },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {rows.map(({ label, value }) => (
        <div key={label} className="flex justify-between items-center py-2 border-b border-gray-50">
          <span className="text-sm text-gray-500">{label}</span>
          <span className="text-sm font-medium text-gray-900">{value || '—'}</span>
        </div>
      ))}
    </div>
  );
}

function SchemesTab({ schemes, onGenerate, generating }) {
  if (!schemes || schemes.length === 0) {
    return <p className="text-sm text-gray-500 text-center py-8">No eligible schemes found.</p>;
  }
  return (
    <div className="space-y-4">
      {schemes.map((s) => (
        <div key={s.id} className="border border-gray-200 rounded-lg p-4">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold text-gray-900">{s.name_en}</h3>
              <p className="text-sm text-gray-500 mt-1">{s.description_en}</p>
              <div className="flex gap-2 mt-2">
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                  s.eligibility_status === 'eligible' ? 'bg-green-100 text-green-700' :
                  s.eligibility_status === 'partial' ? 'bg-amber-100 text-amber-700' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {s.eligibility_status === 'eligible' ? 'Eligible' : s.eligibility_status === 'partial' ? 'Partial' : 'Check'}
                </span>
                {s.deadline && (
                  <span className="text-xs text-gray-400">Deadline: {new Date(s.deadline).toLocaleDateString('en-IN')}</span>
                )}
              </div>
            </div>
            <button
              onClick={() => onGenerate(s)}
              disabled={generating}
              className="text-primary-600 hover:text-primary-700 flex items-center gap-1 text-sm font-medium"
            >
              <Download className="w-4 h-4" /> Form
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

function DocumentsTab({ documents }) {
  if (!documents || documents.length === 0) {
    return <p className="text-sm text-gray-500 text-center py-8">No documents uploaded by farmer.</p>;
  }
  return (
    <div className="space-y-3">
      {documents.map((doc) => (
        <div key={doc.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900">{doc.doc_type}</p>
              <p className="text-xs text-gray-500">
                Uploaded {new Date(doc.uploaded_at).toLocaleDateString('en-IN')}
              </p>
            </div>
          </div>
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
            doc.verified ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
          }`}>
            {doc.verified ? 'Verified' : 'Pending'}
          </span>
        </div>
      ))}
    </div>
  );
}
