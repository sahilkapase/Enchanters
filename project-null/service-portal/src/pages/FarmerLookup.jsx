import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { lookupFarmer } from '../services/api';
import { Search, User, MapPin, Phone, ArrowRight, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

export default function FarmerLookup() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;

    setLoading(true);
    setResults(null);

    try {
      const data = await lookupFarmer(q);
      /* Backend returns single farmer object or {items, total} for multiple matches */
      if (data.items) {
        setResults(data.items);
      } else {
        setResults([data]);
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setResults([]);
        toast.error('No farmer found');
      } else {
        toast.error('Search failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const openFarmer = (farmerId) => {
    navigate(`/farmer/${farmerId}`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Farmer Lookup</h1>
        <p className="text-sm text-gray-500 mt-1">
          Search by Farmer ID, phone number, or name
        </p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            className="w-full rounded-lg border border-gray-300 pl-10 pr-4 py-2.5 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. KSXR7BM2QAL, 9876543210, or farmer name"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-primary-600 hover:bg-primary-700 text-white font-semibold px-6 py-2.5 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
          Search
        </button>
      </form>

      {/* Scan hint */}
      <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
        <p className="text-sm text-primary-800">
          <strong>Tip:</strong> You can scan the farmer's QR code or ask them for
          their 11-character Farmer ID (starts with <span className="font-mono">KS</span>).
        </p>
      </div>

      {/* Results */}
      {results !== null && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            {results.length === 0
              ? 'No Results'
              : `Found ${results.length} farmer${results.length > 1 ? 's' : ''}`}
          </h2>

          {results.length === 0 ? (
            <div className="bg-white rounded-xl p-8 text-center shadow-sm border border-gray-100">
              <User className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No farmer matches your search.</p>
              <p className="text-sm text-gray-400 mt-1">Check the ID or phone number and try again.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {results.map((f) => (
                <button
                  key={f.farmer_id}
                  onClick={() => openFarmer(f.farmer_id)}
                  className="w-full bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:border-primary-300 hover:shadow-md transition-all text-left flex items-center justify-between group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                      <User className="w-6 h-6 text-primary-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{f.name}</p>
                      <p className="font-mono text-sm text-primary-600">{f.farmer_id}</p>
                      <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                        {f.phone && (
                          <span className="flex items-center gap-1">
                            <Phone className="w-3 h-3" /> {f.phone}
                          </span>
                        )}
                        {f.district && (
                          <span className="flex items-center gap-1">
                            <MapPin className="w-3 h-3" /> {f.district}, {f.state}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <ArrowRight className="w-5 h-5 text-gray-300 group-hover:text-primary-500 transition-colors" />
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
