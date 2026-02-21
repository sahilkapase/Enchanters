import { QRCodeSVG } from 'qrcode.react';
import Button from '../common/Button';
import { Copy, Share2 } from 'lucide-react';
import toast from 'react-hot-toast';

export default function FarmerIDCard({ farmerId, name, district, state }) {
  const copyId = () => {
    navigator.clipboard.writeText(farmerId);
    toast.success('Farmer ID copied!');
  };

  const shareWhatsApp = () => {
    const text = `My KisaanSeva Farmer ID: ${farmerId}\nUse this at any Jan Suvidha Kendra or CSC center.`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
  };

  return (
    <div className="bg-gradient-to-br from-primary-600 to-primary-800 rounded-2xl p-6 text-white shadow-lg">
      <div className="flex flex-col sm:flex-row items-center gap-5">
        <div className="bg-white rounded-xl p-2.5 flex-shrink-0">
          <QRCodeSVG value={farmerId} size={100} level="M" />
        </div>
        <div className="text-center sm:text-left flex-1">
          <p className="text-primary-200 text-xs uppercase tracking-wider mb-1">Farmer ID</p>
          <p className="text-2xl font-mono font-bold tracking-wider mb-1">{farmerId}</p>
          <p className="text-white font-medium">{name}</p>
          {district && (
            <p className="text-primary-200 text-sm">{district}{state ? `, ${state}` : ''}</p>
          )}
        </div>
      </div>
      <div className="flex gap-2 mt-4 pt-4 border-t border-white/20">
        <Button variant="ghost" size="sm" icon={Copy} onClick={copyId} className="text-white hover:bg-white/10">
          Copy ID
        </Button>
        <Button variant="ghost" size="sm" icon={Share2} onClick={shareWhatsApp} className="text-white hover:bg-white/10">
          Share
        </Button>
      </div>
    </div>
  );
}
