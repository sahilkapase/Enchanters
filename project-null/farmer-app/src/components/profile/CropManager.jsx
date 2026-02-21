import { useState } from 'react';
import { useFarmerCrops, useAddCrop, useRemoveCrop } from '../../hooks/useFarmer';
import Card, { CardTitle } from '../common/Card';
import Button from '../common/Button';
import { CROPS, SEASONS } from '../../utils/constants';
import { Plus, X, Sprout, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

export default function CropManager() {
  const { data: crops = [], isLoading } = useFarmerCrops();
  const addCrop = useAddCrop();
  const removeCrop = useRemoveCrop();

  const [showAdd, setShowAdd] = useState(false);
  const [newCrop, setNewCrop] = useState('');
  const [newSeason, setNewSeason] = useState('kharif');

  const handleAdd = () => {
    if (!newCrop) return;
    addCrop.mutate(
      { crop_name: newCrop, season: newSeason, year: new Date().getFullYear(), is_active: true },
      {
        onSuccess: () => {
          toast.success('Crop added!');
          setNewCrop('');
          setShowAdd(false);
        },
        onError: () => toast.error('Failed to add crop'),
      }
    );
  };

  const handleRemove = (cropId) => {
    removeCrop.mutate(cropId, {
      onSuccess: () => toast.success('Crop removed'),
      onError: () => toast.error('Failed to remove crop'),
    });
  };

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <CardTitle>My Crops</CardTitle>
        <Button variant="secondary" size="sm" icon={Plus} onClick={() => setShowAdd(!showAdd)}>
          Add Crop
        </Button>
      </div>

      {/* Add form */}
      {showAdd && (
        <div className="flex flex-col sm:flex-row items-end gap-2 mb-4 p-3 bg-primary-50 rounded-xl">
          <div className="flex-1 w-full">
            <label className="block text-xs text-gray-500 mb-1">Crop</label>
            <select
              value={newCrop}
              onChange={(e) => setNewCrop(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 outline-none cursor-pointer"
            >
              <option value="">Select crop</option>
              {CROPS.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="w-full sm:w-32">
            <label className="block text-xs text-gray-500 mb-1">Season</label>
            <select
              value={newSeason}
              onChange={(e) => setNewSeason(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary-500 outline-none cursor-pointer"
            >
              {SEASONS.map((s) => <option key={s.value} value={s.value}>{s.label_en}</option>)}
            </select>
          </div>
          <Button size="sm" onClick={handleAdd} loading={addCrop.isPending}>Add</Button>
        </div>
      )}

      {/* Crop list */}
      {isLoading ? (
        <div className="flex justify-center py-6">
          <Loader2 className="w-6 h-6 text-primary-600 animate-spin" />
        </div>
      ) : crops.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-6">No crops added yet. Add your crops to get better scheme recommendations.</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {crops.map((crop) => (
            <div key={crop.id} className="inline-flex items-center gap-2 px-3 py-1.5 bg-primary-50 border border-primary-200 rounded-full">
              <Sprout className="w-3.5 h-3.5 text-primary-600" />
              <span className="text-sm font-medium text-primary-800">{crop.crop_name}</span>
              <span className="text-xs text-primary-500 capitalize">{crop.season}</span>
              <button
                onClick={() => handleRemove(crop.id)}
                className="p-0.5 rounded-full hover:bg-primary-200 transition-colors cursor-pointer"
              >
                <X className="w-3 h-3 text-primary-500" />
              </button>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
