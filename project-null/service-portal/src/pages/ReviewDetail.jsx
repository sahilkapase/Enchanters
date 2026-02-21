import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateStagedItem } from '../services/api';
import {
  ArrowLeft, Check, X, Save, Bot, PenTool,
  FileText, Tag, MapPin, Calendar, Shield,
} from 'lucide-react';
import toast from 'react-hot-toast';

const BENEFIT_TYPES = ['cash', 'subsidy', 'insurance', 'equipment'];
const SUBSIDY_CATEGORIES = ['seed', 'fertilizer', 'equipment', 'irrigation', 'organic', 'credit'];
const RULE_TYPES = ['state', 'crop', 'land_min', 'land_max', 'income_max', 'season', 'ownership', 'irrigation'];

export default function ReviewDetail({
  item,
  onBack,
  onApprove,
  onReject,
  isApproving,
  isRejecting,
  agentName,
}) {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [rejectNotes, setRejectNotes] = useState('');
  const [showRejectForm, setShowRejectForm] = useState(false);

  const [form, setForm] = useState({
    name_en: item.name_en || '',
    name_hi: item.name_hi || '',
    ministry: item.ministry || '',
    description_en: item.description_en || '',
    description_hi: item.description_hi || '',
    benefit_type: item.benefit_type || '',
    benefit_amount: item.benefit_amount || '',
    subsidy_category: item.subsidy_category || '',
    apply_url: item.apply_url || '',
    how_to_apply: item.how_to_apply || '',
    target_state: item.target_state || '',
    item_type: item.item_type || 'scheme',
    eligibility_rules: item.eligibility_rules || [],
  });

  const [newRule, setNewRule] = useState({ rule_type: 'state', rule_value: '', is_mandatory: true });

  const saveMutation = useMutation({
    mutationFn: (data) => updateStagedItem(item.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staged-items'] });
      toast.success('Item updated');
      setEditing(false);
    },
    onError: () => toast.error('Failed to save changes'),
  });

  const handleSave = () => {
    saveMutation.mutate(form);
  };

  const addRule = () => {
    if (!newRule.rule_value.trim()) return;
    setForm((f) => ({
      ...f,
      eligibility_rules: [...f.eligibility_rules, { ...newRule }],
    }));
    setNewRule({ rule_type: 'state', rule_value: '', is_mandatory: true });
  };

  const removeRule = (idx) => {
    setForm((f) => ({
      ...f,
      eligibility_rules: f.eligibility_rules.filter((_, i) => i !== idx),
    }));
  };

  const isPending = item.status === 'pending';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Queue
        </button>

        {isPending && (
          <div className="flex items-center gap-2">
            {!editing ? (
              <button
                onClick={() => setEditing(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
              >
                <PenTool className="w-3.5 h-3.5" />
                Edit
              </button>
            ) : (
              <button
                onClick={handleSave}
                disabled={saveMutation.isPending}
                className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 cursor-pointer"
              >
                <Save className="w-3.5 h-3.5" />
                Save
              </button>
            )}
            <button
              onClick={() => onApprove(item.id)}
              disabled={isApproving}
              className="flex items-center gap-1.5 px-4 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 cursor-pointer"
            >
              <Check className="w-4 h-4" />
              {isApproving ? 'Publishing...' : 'Approve & Publish'}
            </button>
            <button
              onClick={() => setShowRejectForm(!showRejectForm)}
              className="flex items-center gap-1.5 px-4 py-1.5 text-sm bg-red-50 text-red-600 rounded-lg hover:bg-red-100 cursor-pointer"
            >
              <X className="w-4 h-4" />
              Reject
            </button>
          </div>
        )}
      </div>

      {/* Reject Form */}
      {showRejectForm && (
        <div className="bg-red-50 rounded-xl p-4 border border-red-100">
          <label className="text-sm font-medium text-red-700 block mb-2">Reason for rejection</label>
          <textarea
            value={rejectNotes}
            onChange={(e) => setRejectNotes(e.target.value)}
            className="w-full border border-red-200 rounded-lg p-2 text-sm mb-3"
            rows={2}
            placeholder="Optional: why is this item being rejected?"
          />
          <button
            onClick={() => { onReject(item.id, rejectNotes); setShowRejectForm(false); }}
            disabled={isRejecting}
            className="px-4 py-1.5 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 disabled:opacity-50 cursor-pointer"
          >
            {isRejecting ? 'Rejecting...' : 'Confirm Reject'}
          </button>
        </div>
      )}

      {/* Source info */}
      <div className="bg-gray-50 rounded-xl p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {item.source === 'manual' ? (
            <PenTool className="w-5 h-5 text-primary-600" />
          ) : (
            <Bot className="w-5 h-5 text-amber-600" />
          )}
          <div>
            <p className="text-sm font-medium text-gray-900">
              {item.source === 'manual' ? 'Manually entered' : `Scraped from ${item.source}`}
            </p>
            <p className="text-xs text-gray-500">
              Added {item.created_at ? new Date(item.created_at).toLocaleString('en-IN') : '—'}
            </p>
          </div>
        </div>
        <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${
          item.status === 'pending' ? 'bg-amber-100 text-amber-700'
          : item.status === 'approved' ? 'bg-green-100 text-green-700'
          : 'bg-red-100 text-red-700'
        }`}>
          {item.status.toUpperCase()}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Content */}
        <div className="space-y-5">
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-4 flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Content
            </h3>
            <div className="space-y-4">
              <Field label="Title (English)" value={form.name_en} field="name_en" editing={editing} onChange={setForm} />
              <Field label="Title (Hindi)" value={form.name_hi} field="name_hi" editing={editing} onChange={setForm} />
              <Field label="Ministry" value={form.ministry} field="ministry" editing={editing} onChange={setForm} />
              <TextArea label="Description (English)" value={form.description_en} field="description_en" editing={editing} onChange={setForm} />
              <TextArea label="Description (Hindi)" value={form.description_hi} field="description_hi" editing={editing} onChange={setForm} />
              <TextArea label="How to Apply" value={form.how_to_apply} field="how_to_apply" editing={editing} onChange={setForm} />
            </div>
          </div>
        </div>

        {/* Right: Metadata + Rules */}
        <div className="space-y-5">
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-4 flex items-center gap-2">
              <Tag className="w-4 h-4" />
              Classification
            </h3>
            <div className="space-y-4">
              <SelectField label="Type" value={form.item_type} field="item_type" options={['scheme', 'subsidy']} editing={editing} onChange={setForm} />
              <SelectField label="Benefit Type" value={form.benefit_type} field="benefit_type" options={BENEFIT_TYPES} editing={editing} onChange={setForm} />
              <Field label="Benefit Amount" value={form.benefit_amount} field="benefit_amount" editing={editing} onChange={setForm} />
              {form.item_type === 'subsidy' && (
                <SelectField label="Subsidy Category" value={form.subsidy_category} field="subsidy_category" options={SUBSIDY_CATEGORIES} editing={editing} onChange={setForm} />
              )}
              <Field label="Apply URL" value={form.apply_url} field="apply_url" editing={editing} onChange={setForm} />
              <Field label="Target State" value={form.target_state} field="target_state" editing={editing} onChange={setForm} />
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-4 flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Eligibility Rules
            </h3>

            {form.eligibility_rules.length === 0 ? (
              <p className="text-sm text-gray-400 mb-3">No rules defined. Add rules to target specific farmers.</p>
            ) : (
              <div className="space-y-2 mb-4">
                {form.eligibility_rules.map((rule, idx) => (
                  <div key={idx} className="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono bg-primary-100 text-primary-700 px-1.5 py-0.5 rounded">
                        {rule.rule_type}
                      </span>
                      <span className="text-sm text-gray-700">{rule.rule_value}</span>
                      {rule.is_mandatory && (
                        <span className="text-xs text-red-500">required</span>
                      )}
                    </div>
                    {editing && (
                      <button
                        onClick={() => removeRule(idx)}
                        className="text-gray-400 hover:text-red-500 cursor-pointer"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}

            {editing && (
              <div className="flex gap-2 items-end">
                <div className="flex-1">
                  <select
                    value={newRule.rule_type}
                    onChange={(e) => setNewRule((r) => ({ ...r, rule_type: e.target.value }))}
                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm"
                  >
                    {RULE_TYPES.map((rt) => (
                      <option key={rt} value={rt}>{rt}</option>
                    ))}
                  </select>
                </div>
                <div className="flex-1">
                  <input
                    value={newRule.rule_value}
                    onChange={(e) => setNewRule((r) => ({ ...r, rule_value: e.target.value }))}
                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm"
                    placeholder="Value"
                  />
                </div>
                <label className="flex items-center gap-1 text-xs text-gray-500">
                  <input
                    type="checkbox"
                    checked={newRule.is_mandatory}
                    onChange={(e) => setNewRule((r) => ({ ...r, is_mandatory: e.target.checked }))}
                  />
                  Req
                </label>
                <button
                  onClick={addRule}
                  className="px-3 py-1.5 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 cursor-pointer"
                >
                  Add
                </button>
              </div>
            )}
          </div>

          {/* Raw Data (for scraped items) */}
          {item.raw_data && Object.keys(item.raw_data).length > 0 && (
            <details className="bg-white rounded-xl shadow-sm border border-gray-100">
              <summary className="p-4 text-sm font-medium text-gray-500 cursor-pointer hover:text-gray-700">
                Raw Scraped Data
              </summary>
              <pre className="p-4 pt-0 text-xs text-gray-500 overflow-auto max-h-60">
                {JSON.stringify(item.raw_data, null, 2)}
              </pre>
            </details>
          )}

          {/* Review history */}
          {item.reviewed_by && (
            <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <p className="text-sm text-gray-500">
                Reviewed by <span className="font-medium text-gray-900">{item.reviewed_by}</span>
                {item.reviewed_at && (
                  <> on {new Date(item.reviewed_at).toLocaleString('en-IN')}</>
                )}
              </p>
              {item.review_notes && (
                <p className="text-sm text-gray-600 mt-1 italic">"{item.review_notes}"</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ── Reusable form fields ── */

function Field({ label, value, field, editing, onChange }) {
  if (!editing) {
    return (
      <div>
        <label className="text-xs text-gray-500 block mb-0.5">{label}</label>
        <p className="text-sm text-gray-900">{value || '—'}</p>
      </div>
    );
  }
  return (
    <div>
      <label className="text-xs text-gray-500 block mb-0.5">{label}</label>
      <input
        value={value}
        onChange={(e) => onChange((f) => ({ ...f, [field]: e.target.value }))}
        className="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
      />
    </div>
  );
}

function TextArea({ label, value, field, editing, onChange }) {
  if (!editing) {
    return (
      <div>
        <label className="text-xs text-gray-500 block mb-0.5">{label}</label>
        <p className="text-sm text-gray-900 whitespace-pre-wrap">{value || '—'}</p>
      </div>
    );
  }
  return (
    <div>
      <label className="text-xs text-gray-500 block mb-0.5">{label}</label>
      <textarea
        value={value}
        onChange={(e) => onChange((f) => ({ ...f, [field]: e.target.value }))}
        rows={3}
        className="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
      />
    </div>
  );
}

function SelectField({ label, value, field, options, editing, onChange }) {
  if (!editing) {
    return (
      <div>
        <label className="text-xs text-gray-500 block mb-0.5">{label}</label>
        <p className="text-sm text-gray-900">{value || '—'}</p>
      </div>
    );
  }
  return (
    <div>
      <label className="text-xs text-gray-500 block mb-0.5">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange((f) => ({ ...f, [field]: e.target.value }))}
        className="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
      >
        <option value="">—</option>
        {options.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </div>
  );
}
