export default function Card({ children, className = '', padding = 'p-5', hover = false, ...props }) {
  return (
    <div
      className={`
        bg-white rounded-2xl border border-gray-100 shadow-sm
        ${hover ? 'hover:shadow-md hover:border-primary-200 transition-all duration-200' : ''}
        ${padding} ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = '' }) {
  return <div className={`mb-3 ${className}`}>{children}</div>;
}

export function CardTitle({ children, className = '' }) {
  return <h3 className={`text-lg font-bold text-gray-900 ${className}`}>{children}</h3>;
}

export function CardDescription({ children, className = '' }) {
  return <p className={`text-sm text-gray-500 ${className}`}>{children}</p>;
}
