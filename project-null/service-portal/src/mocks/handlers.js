import { http, HttpResponse, delay } from 'msw';

/* ── Mock agent ── */
const MOCK_AGENT = {
  id: 'agent-1',
  name: 'Sunil Verma',
  username: 'sunil.verma',
  center_name: 'Jan Suvidha Kendra — Indore, Vijay Nagar',
  center_id: 'CSC-IND-042',
};

/* ── Mock farmer for lookup ── */
const MOCK_FARMER = {
  farmer_id: 'KSXR7BM2QAL',
  name: 'Rajesh Kumar',
  phone: '9876543210',
  pin_code: '452001',
  district: 'Indore',
  state: 'Madhya Pradesh',
  land_area: 5.5,
  land_unit: 'acre',
  profile: {
    irrigation_type: 'tubewell',
    ownership_type: 'owned',
  },
  crops: [
    { id: 'c-1', crop_name: 'Wheat', season: 'rabi', year: 2026, is_active: true },
    { id: 'c-2', crop_name: 'Soybean', season: 'kharif', year: 2025, is_active: true },
  ],
  created_at: '2025-08-15T10:30:00Z',
};

const MOCK_FARMER_2 = {
  farmer_id: 'KS4NJP8XWQT',
  name: 'Meena Devi',
  phone: '9012345678',
  pin_code: '452002',
  district: 'Indore',
  state: 'Madhya Pradesh',
  land_area: 3,
  land_unit: 'acre',
  profile: {
    irrigation_type: 'canal',
    ownership_type: 'owned',
  },
  crops: [{ id: 'c-3', crop_name: 'Rice', season: 'kharif', year: 2025, is_active: true }],
  created_at: '2025-10-22T08:00:00Z',
};

const allFarmers = [MOCK_FARMER, MOCK_FARMER_2];

let sessionCounter = 100;
const sessions = [
  {
    id: 'sess-1', farmer_id: 'KSXR7BM2QAL', farmer_name: 'Rajesh Kumar',
    purpose: 'PM-KISAN registration', session_start: '2026-02-21T09:30:00Z',
    session_end: '2026-02-21T10:00:00Z', status: 'ended',
  },
  {
    id: 'sess-2', farmer_id: 'KS4NJP8XWQT', farmer_name: 'Meena Devi',
    purpose: 'PMFBY form generation', session_start: '2026-02-21T11:00:00Z',
    session_end: null, status: 'active',
  },
  {
    id: 'sess-3', farmer_id: 'KSXR7BM2QAL', farmer_name: 'Rajesh Kumar',
    purpose: 'Subsidy inquiry', session_start: '2026-02-20T14:00:00Z',
    session_end: '2026-02-20T14:25:00Z', status: 'ended',
  },
];

const fakeToken = 'mock-agent-jwt';
const fakeRefresh = 'mock-agent-refresh';

export const handlers = [
  /* ═══════ AGENT AUTH ═══════ */
  http.post('/api/v1/service/auth/login', async ({ request }) => {
    await delay(500);
    const body = await request.json();
    if (!body.username || !body.password) {
      return HttpResponse.json({ detail: 'Missing credentials' }, { status: 400 });
    }
    return HttpResponse.json({
      agent: MOCK_AGENT,
      access_token: fakeToken,
      refresh_token: fakeRefresh,
      token_type: 'bearer',
    });
  }),

  http.post('/api/v1/service/auth/logout', () =>
    HttpResponse.json({ message: 'Logged out successfully' }),
  ),

  http.post('/api/v1/service/auth/refresh', () =>
    HttpResponse.json({ access_token: fakeToken, refresh_token: fakeRefresh, token_type: 'bearer' }),
  ),

  /* ═══════ FARMER LOOKUP ═══════ */
  http.post('/api/v1/service/lookup', async ({ request }) => {
    await delay(400);
    const body = await request.json();
    const q = (body.query || '').toLowerCase();
    const found = allFarmers.filter(
      (f) =>
        f.farmer_id.toLowerCase().includes(q) ||
        f.name.toLowerCase().includes(q) ||
        f.phone.includes(q),
    );
    if (found.length === 0) return HttpResponse.json({ detail: 'No farmers found' }, { status: 404 });
    return HttpResponse.json(found.length === 1 ? found[0] : { items: found, total: found.length });
  }),

  /* ═══════ ACCESS REQUEST / SESSION ═══════ */
  http.post('/api/v1/service/request-access', async ({ request }) => {
    await delay(400);
    const body = await request.json();
    const farmer = allFarmers.find((f) => f.farmer_id === body.farmer_id);
    if (!farmer) return HttpResponse.json({ detail: 'Farmer not found' }, { status: 404 });
    return HttpResponse.json({
      message: `OTP sent to farmer's phone ending ****${farmer.phone.slice(-4)}`,
      farmer_id: farmer.farmer_id,
    });
  }),

  http.post('/api/v1/service/verify-access', async ({ request }) => {
    await delay(500);
    const body = await request.json();
    const farmer = allFarmers.find((f) => f.farmer_id === body.farmer_id);
    const newSession = {
      id: `sess-${++sessionCounter}`,
      farmer_id: body.farmer_id,
      farmer_name: farmer?.name || 'Unknown',
      purpose: 'Service center visit',
      session_start: new Date().toISOString(),
      session_end: null,
      status: 'active',
    };
    sessions.unshift(newSession);
    return HttpResponse.json({ session_id: newSession.id, verified: true });
  }),

  http.get('/api/v1/service/session/:sessionId', async ({ params }) => {
    await delay(300);
    const s = sessions.find((s) => s.id === params.sessionId);
    if (!s) return HttpResponse.json({ detail: 'Session not found' }, { status: 404 });
    return HttpResponse.json(s);
  }),

  http.post('/api/v1/service/session/:sessionId/end', async ({ params }) => {
    await delay(300);
    const s = sessions.find((s) => s.id === params.sessionId);
    if (s) {
      s.session_end = new Date().toISOString();
      s.status = 'ended';
    }
    return HttpResponse.json({ message: 'Session ended' });
  }),

  /* ═══════ SESSION-BASED FARMER DATA ═══════ */
  http.get('/api/v1/service/session/:sessionId/farmer', async ({ params }) => {
    await delay(500);
    const s = sessions.find((s) => s.id === params.sessionId);
    if (!s) return HttpResponse.json({ detail: 'Session not found' }, { status: 404 });
    const farmer = allFarmers.find((f) => f.farmer_id === s.farmer_id);
    if (!farmer) return HttpResponse.json({ detail: 'Farmer not found' }, { status: 404 });
    return HttpResponse.json({
      ...farmer,
      schemes: [
        {
          id: 'sch-1', name_en: 'PM-KISAN Samman Nidhi',
          description_en: '₹6,000/year direct benefit transfer',
          eligibility_status: 'eligible', benefit_type: 'dbt',
        },
        {
          id: 'sch-2', name_en: 'PMFBY — Kharif 2026',
          description_en: 'Crop insurance at subsidized premiums',
          eligibility_status: 'eligible', benefit_type: 'insurance',
        },
        {
          id: 'sch-5', name_en: 'Mukhyamantri Kisan Kalyan Yojana',
          description_en: '₹4,000/year additional for MP farmers',
          eligibility_status: 'partial', benefit_type: 'dbt',
        },
      ],
      documents: [
        { id: 'doc-1', doc_type: 'aadhaar', file_name: 'aadhaar.pdf', uploaded_at: '2025-08-20T00:00:00Z', verified: true },
        { id: 'doc-2', doc_type: 'land_record', file_name: 'khasra.pdf', uploaded_at: '2025-08-22T00:00:00Z', verified: false },
      ],
    });
  }),

  http.post('/api/v1/service/session/:sessionId/generate-form', async () => {
    await delay(800);
    return HttpResponse.json({
      file_key: 'forms/generated/mock_form.pdf',
      file_name: 'scheme_application.pdf',
      message: 'Form generated successfully',
    });
  }),

  /* ═══════ ACTIVITY LOG ═══════ */
  http.get('/api/v1/service/activity', async ({ request }) => {
    await delay(400);
    const url = new URL(request.url);
    const q = (url.searchParams.get('q') || '').toLowerCase();
    const page = Number(url.searchParams.get('page')) || 1;
    const limit = Number(url.searchParams.get('limit')) || 20;

    let filtered = sessions;
    if (q) {
      filtered = sessions.filter(
        (s) =>
          s.farmer_id.toLowerCase().includes(q) ||
          s.purpose.toLowerCase().includes(q) ||
          (s.farmer_name || '').toLowerCase().includes(q),
      );
    }
    const start = (page - 1) * limit;
    return HttpResponse.json({
      items: filtered.slice(start, start + limit),
      total: filtered.length,
    });
  }),
];
