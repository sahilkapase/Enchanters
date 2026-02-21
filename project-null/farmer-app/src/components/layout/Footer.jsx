import { useTranslation } from 'react-i18next';

export default function Footer() {
  const { t } = useTranslation();

  return (
    <footer className="hidden md:block bg-white border-t border-gray-100 mt-auto">
      <div className="max-w-7xl mx-auto px-6 py-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-primary-600 flex items-center justify-center">
            <span className="text-white font-bold text-[10px]">KS</span>
          </div>
          <span className="text-sm text-gray-600">
            {t('app_name')} &copy; {new Date().getFullYear()}
          </span>
        </div>
        <div className="flex items-center gap-6 text-sm text-gray-500">
          <a href="#" className="hover:text-primary-600 transition-colors">Help</a>
          <a href="#" className="hover:text-primary-600 transition-colors">Privacy</a>
          <a href="#" className="hover:text-primary-600 transition-colors">Terms</a>
        </div>
      </div>
    </footer>
  );
}
