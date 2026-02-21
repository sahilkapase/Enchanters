import { http, HttpResponse, delay } from 'msw';
import {
  MOCK_FARMER,
  MOCK_CROPS,
  MOCK_DOCUMENTS,
  MOCK_SCHEMES,
  MOCK_INSURANCE_PLANS,
  MOCK_SUBSIDIES,
  MOCK_ACCESS_LOG,
  MOCK_FORMS,
  MOCK_SUBSIDY_CALENDAR,
} from './data';

/* ── Mutable state so CRUD operations reflect in UI ── */
let farmer = { ...MOCK_FARMER };
let crops = [...MOCK_CROPS];
let documents = [...MOCK_DOCUMENTS];
let nextCropId = 10;
let nextDocId = 10;

/* ── Fake tokens ── */
const fakeToken = 'mock-jwt-access-token';
const fakeRefresh = 'mock-jwt-refresh-token';

/** Helper — full FarmerResponse shape */
const farmerResponse = () => ({ ...farmer, crops });

export const handlers = [
  /* ═══════════ AUTH ═══════════ */

  // Signup → sends OTP, returns message + farmer_id
  http.post('/api/v1/auth/signup', async ({ request }) => {
    await delay(400);
    const body = await request.json();
    farmer = {
      ...farmer,
      name: body.name || farmer.name,
      phone: body.phone || farmer.phone,
      email: body.email || '',
      pin_code: body.pin_code || farmer.pin_code,
      land_area: body.land_area ?? farmer.land_area,
      land_unit: body.land_unit || 'acre',
    };
    return HttpResponse.json({
      message: 'OTP sent to registered phone number',
      farmer_id: farmer.farmer_id,
    });
  }),

  // Verify OTP (signup flow) → returns verified + tokens on first phone verification
  http.post('/api/v1/auth/verify-otp', async () => {
    await delay(500);
    farmer = { ...farmer, phone_verified: true };
    return HttpResponse.json({
      verified: true,
      access_token: fakeToken,
      refresh_token: fakeRefresh,
      token_type: 'bearer',
      farmer_id: farmer.farmer_id,
    });
  }),

  // Login → sends OTP
  http.post('/api/v1/auth/login', async () => {
    await delay(400);
    return HttpResponse.json({ message: 'OTP sent to registered phone number' });
  }),

  // Login verify → returns tokens (flat, no wrapped farmer object)
  http.post('/api/v1/auth/login/verify', async () => {
    await delay(500);
    return HttpResponse.json({
      access_token: fakeToken,
      refresh_token: fakeRefresh,
      token_type: 'bearer',
      farmer_id: farmer.farmer_id,
    });
  }),

  // Refresh token
  http.post('/api/v1/auth/refresh', async () => {
    await delay(100);
    return HttpResponse.json({
      access_token: fakeToken,
      refresh_token: fakeRefresh,
      token_type: 'bearer',
      farmer_id: farmer.farmer_id,
    });
  }),

  // Logout
  http.post('/api/v1/auth/logout', () =>
    HttpResponse.json({ message: 'Logged out successfully' }),
  ),

  /* ═══════════ FARMER PROFILE ═══════════ */

  http.get('/api/v1/farmers/me', async () => {
    await delay(300);
    return HttpResponse.json(farmerResponse());
  }),

  // PATCH — basic info (name, email, pin_code, land_area, land_unit)
  http.patch('/api/v1/farmers/me', async ({ request }) => {
    await delay(300);
    const body = await request.json();
    farmer = { ...farmer, ...body, updated_at: new Date().toISOString() };
    return HttpResponse.json(farmerResponse());
  }),

  // PUT — extended profile (irrigation_type, ownership_type, aadhaar_linked, bank_account_linked)
  http.put('/api/v1/farmers/me/profile', async ({ request }) => {
    await delay(300);
    const body = await request.json();
    farmer = {
      ...farmer,
      profile: { ...(farmer.profile || {}), ...body },
      updated_at: new Date().toISOString(),
    };
    return HttpResponse.json(farmer.profile);
  }),

  /* ── Crops ── */
  http.get('/api/v1/farmers/me/crops', async () => {
    await delay(200);
    return HttpResponse.json(crops);
  }),

  http.post('/api/v1/farmers/me/crops', async ({ request }) => {
    await delay(300);
    const body = await request.json();
    const newCrop = {
      id: `crop-${nextCropId++}`,
      crop_name: body.crop_name,
      season: body.season,
      year: body.year || new Date().getFullYear(),
      is_active: true,
      created_at: new Date().toISOString(),
    };
    crops.push(newCrop);
    return HttpResponse.json(newCrop, { status: 201 });
  }),

  http.delete('/api/v1/farmers/me/crops/:cropId', async ({ params }) => {
    await delay(200);
    crops = crops.filter((c) => String(c.id) !== String(params.cropId));
    return HttpResponse.json({ message: 'Crop deleted' });
  }),

  /* ── Documents ── */
  http.get('/api/v1/farmers/me/documents', async () => {
    await delay(200);
    return HttpResponse.json(documents);
  }),

  http.post('/api/v1/farmers/me/documents', async ({ request }) => {
    await delay(600);
    const formData = await request.formData();
    const docType = formData.get('doc_type');
    const file = formData.get('file');
    const fileName = file?.name || 'document.pdf';
    const newDoc = {
      id: `doc-${nextDocId++}`,
      doc_type: docType,
      file_name: fileName,
      file_key: `documents/${farmer.farmer_id}/${docType}/${fileName}`,
      uploaded_at: new Date().toISOString(),
      verified: false,
    };
    documents.push(newDoc);
    return HttpResponse.json(newDoc, { status: 201 });
  }),

  http.delete('/api/v1/farmers/me/documents/:docId', async ({ params }) => {
    await delay(200);
    documents = documents.filter((d) => String(d.id) !== String(params.docId));
    return HttpResponse.json({ message: 'Document deleted' });
  }),

  /* ── Access log ── */
  http.get('/api/v1/farmers/me/access-log', async () => {
    await delay(300);
    return HttpResponse.json(MOCK_ACCESS_LOG);
  }),

  /* ── Generated forms ── */
  http.get('/api/v1/farmers/me/forms', async () => {
    await delay(200);
    return HttpResponse.json(MOCK_FORMS);
  }),

  /* ═══════════ SCHEMES ═══════════ */

  http.get('/api/v1/schemes', async ({ request }) => {
    await delay(400);
    const url = new URL(request.url);
    let filtered = [...MOCK_SCHEMES];
    const benefitType = url.searchParams.get('benefit_type');

    if (benefitType) {
      filtered = filtered.filter((s) => s.benefit_type === benefitType);
    }
    return HttpResponse.json(filtered);
  }),

  http.get('/api/v1/schemes/:id', async ({ params }) => {
    await delay(300);
    const scheme = MOCK_SCHEMES.find((s) => String(s.id) === String(params.id));
    if (!scheme) return HttpResponse.json({ detail: 'Not found' }, { status: 404 });
    return HttpResponse.json(scheme);
  }),

  // Eligibility breakdown — matches EligibilityBreakdown schema
  http.get('/api/v1/schemes/:id/eligibility', async ({ params }) => {
    await delay(600);
    const scheme = MOCK_SCHEMES.find((s) => String(s.id) === String(params.id));
    const matchedRules = (scheme?.matched_rules || []).map((r) => ({ ...r, met: true }));
    const unmatchedRules = (scheme?.unmatched_rules || []).map((r) => ({ ...r, met: false }));
    const missingDocs = (scheme?.documents_required || []).filter(
      (d) => !documents.some((doc) => doc.doc_type === d),
    );
    return HttpResponse.json({
      eligible: scheme?.eligibility_status === 'eligible',
      match_score: scheme?.match_score ?? 100,
      matched_rules: matchedRules,
      unmatched_rules: unmatchedRules,
      missing_documents: missingDocs,
    });
  }),

  http.post('/api/v1/schemes/:id/generate-form', async () => {
    await delay(800);
    return new HttpResponse(new Blob(['mock-pdf-content'], { type: 'application/pdf' }), {
      headers: { 'Content-Type': 'application/pdf' },
    });
  }),

  http.post('/api/v1/schemes/:id/remind', async () => {
    await delay(300);
    return HttpResponse.json({ message: 'Reminder set successfully' });
  }),

  /* ═══════════ INSURANCE ═══════════ */

  http.get('/api/v1/insurance/plans', async () => {
    await delay(400);
    return HttpResponse.json(MOCK_INSURANCE_PLANS);
  }),

  http.get('/api/v1/insurance/plans/:id', async ({ params }) => {
    await delay(300);
    const plan = MOCK_INSURANCE_PLANS.find((p) => String(p.id) === String(params.id));
    if (!plan) return HttpResponse.json({ detail: 'Not found' }, { status: 404 });
    return HttpResponse.json(plan);
  }),

  /* ═══════════ SUBSIDIES ═══════════ */

  http.get('/api/v1/subsidies', async ({ request }) => {
    await delay(400);
    const url = new URL(request.url);
    let filtered = [...MOCK_SUBSIDIES];
    const category = url.searchParams.get('category');

    if (category) {
      filtered = filtered.filter((s) => s.category === category);
    }
    return HttpResponse.json(filtered);
  }),

  http.get('/api/v1/subsidies/calendar', async () => {
    await delay(300);
    return HttpResponse.json(MOCK_SUBSIDY_CALENDAR);
  }),

  http.get('/api/v1/subsidies/:id', async ({ params }) => {
    await delay(300);
    const sub = MOCK_SUBSIDIES.find((s) => String(s.id) === String(params.id));
    if (!sub) return HttpResponse.json({ detail: 'Not found' }, { status: 404 });
    return HttpResponse.json(sub);
  }),

  http.post('/api/v1/subsidies/:id/remind', async () => {
    await delay(300);
    return HttpResponse.json({ message: 'Reminder set successfully' });
  }),

  /* ═══════════ LOCATION ═══════════ */

  http.get('/api/v1/location/pin/:pincode', async ({ params }) => {
    await delay(300);
    const pin = params.pincode;
    const pinMap = {
      '452001': { district: 'Indore', state: 'Madhya Pradesh' },
      '110001': { district: 'New Delhi', state: 'Delhi' },
      '400001': { district: 'Mumbai', state: 'Maharashtra' },
      '560001': { district: 'Bangalore Urban', state: 'Karnataka' },
      '600001': { district: 'Chennai', state: 'Tamil Nadu' },
      '700001': { district: 'Kolkata', state: 'West Bengal' },
      '302001': { district: 'Jaipur', state: 'Rajasthan' },
      '226001': { district: 'Lucknow', state: 'Uttar Pradesh' },
    };
    const loc = pinMap[pin] || { district: 'Sample District', state: 'Sample State' };
    return HttpResponse.json({ pincode: pin, ...loc });
  }),

  http.get('/api/v1/location/states', async () => {
    await delay(200);
    return HttpResponse.json({
      states: [
        'Andhra Pradesh', 'Bihar', 'Chhattisgarh', 'Delhi', 'Goa', 'Gujarat',
        'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala',
        'Madhya Pradesh', 'Maharashtra', 'Odisha', 'Punjab', 'Rajasthan',
        'Tamil Nadu', 'Telangana', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
      ],
    });
  }),

  http.get('/api/v1/location/districts/:state', async ({ params }) => {
    await delay(200);
    const state = decodeURIComponent(params.state);
    const districtMap = {
      'Madhya Pradesh': ['Indore', 'Bhopal', 'Ujjain', 'Dewas', 'Ratlam', 'Jabalpur', 'Gwalior'],
      'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Aurangabad', 'Solapur'],
      'Uttar Pradesh': ['Lucknow', 'Agra', 'Varanasi', 'Kanpur', 'Meerut', 'Prayagraj'],
    };
    const districts = districtMap[state] || ['District 1', 'District 2', 'District 3'];
    return HttpResponse.json({ state, districts });
  }),
];
