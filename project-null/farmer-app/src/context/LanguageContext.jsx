import { createContext, useContext, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

const LanguageContext = createContext(null);

const LANGUAGES = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'hi', label: 'Hindi', native: 'हिन्दी' },
];

export function LanguageProvider({ children }) {
  const { i18n } = useTranslation();
  const [language, setLanguageState] = useState(i18n.language || 'en');

  const setLanguage = useCallback(
    (code) => {
      i18n.changeLanguage(code);
      setLanguageState(code);
      localStorage.setItem('language', code);
    },
    [i18n]
  );

  return (
    <LanguageContext.Provider value={{ language, setLanguage, languages: LANGUAGES }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
