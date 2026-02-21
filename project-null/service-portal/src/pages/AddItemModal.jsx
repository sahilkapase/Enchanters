import { useState } from 'react';
import { X } from 'lucide-react';

const BENEFIT_TYPES = ['cash', 'subsidy', 'insurance', 'equipment'];
const SUBSIDY_CATEGORIES = ['seed', 'fertilizer', 'equipment', 'irrigation', 'organic', 'credit'];

export default function AddItemModal({ onClose, onSubmit, isSubmitting }) {
  const [form, setForm] = useState({
    item_type: 'scheme',
    name_en: '',
    name_hi: '',
    ministry: '',
    description_en: '',
    description_hi: '',
    benefit_type: 'cash',
    benefit_amount: '',
    subsidy_category: '',
    apply_url: '',
    how_to_apply: '',
    target_state: '',
    source_url: '',
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.name_en.trim()) return;
    onSubmit(form);
  };

  const set = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">Add New Entry</h2>
          <button onClick={onClose} className="p-1 text-gray-400 hover:text-gray-600 cursor-pointer">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {/* Type */}
          <div className="flex gap-3">
            {['scheme', 'subsidy'].map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setForm((f) => ({ ...f, item_type: t }))}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer ${
                  form.item_type === t
                    ? 'bg-primary-100 text-primary-700 border-2 border-primary-300'
                    : 'bg-gray-50 text-gray-500 border-2 border-transparent'
                }`}
              >
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>

          {/* Name */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-500 block mb-1">Title (English) *</label>
              <input
                value={form.name_en}
                onChange={set('name_en')}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                required
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-1">Title (Hindi)</label>
              <input
                value={form.name_hi}
                onChange={set('name_hi')}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
              />
            </div>
          </div>

          <div>
            <label className="text-xs text-gray-500 block mb-1">Ministry / Department</label>
            <input
              value={form.ministry}
              onChange={set('ministry')}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="text-xs text-gray-500 block mb-1">Description (English)</label>
            <textarea
              value={form.description_en}
              onChange={set('description_en')}
              rows={3}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="text-xs text-gray-500 block mb-1">Description (Hindi)</label>
            <textarea
              value={form.description_hi}
              onChange={set('description_hi')}
              rows={2}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-500 block mb-1">Benefit Type</label>
              <select
                value={form.benefit_type}
                onChange={set('benefit_type')}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
              >
                {BENEFIT_TYPES.map((bt) => (
                  <option key={bt} value={bt}>{bt}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-1">Benefit Amount</label>
              <input
                value={form.benefit_amount}
                onChange={set('benefit_amount')}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                placeholder="e.g. ₹6,000 per year"
              />
            </div>
          </div>

          {form.item_type === 'subsidy' && (
            <div>
              <label className="text-xs text-gray-500 block mb-1">Subsidy Category</label>
              <select
                value={form.subsidy_category}
                onChange={set('subsidy_category')}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
              >
                <option value="">—</option>
                {SUBSIDY_CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-500 block mb-1">Apply URL</label>
              <input
                value={form.apply_url}
                onChange={set('apply_url')}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                placeholder="https://..."
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-1">Target State</label>
              <input
                value={form.target_state}
                onChange={set('target_state')}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                placeholder="Leave blank for all-India"
              />
            </div>
          </div>

          <div>
            <label className="text-xs text-gray-500 block mb-1">How to Apply</label>
            <textarea
              value={form.how_to_apply}
              onChange={set('how_to_apply')}
              rows={2}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700 cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !form.name_en.trim()}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50 cursor-pointer"
            >
              {isSubmitting ? 'Adding...' : 'Add to Queue'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
