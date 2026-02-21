import { useAccessLog } from '../../hooks/useFarmer';
import Card, { CardTitle } from '../common/Card';
import EmptyState from '../common/EmptyState';
import { Shield, Loader2 } from 'lucide-react';
import { formatDate } from '../../utils/formatters';
import { useTranslation } from 'react-i18next';

export default function AccessLog() {
  const { t } = useTranslation();
  const { data: logs = [], isLoading } = useAccessLog();

  return (
    <Card>
      <CardTitle className="mb-4">{t('profile.access_log')}</CardTitle>

      {isLoading ? (
        <div className="flex justify-center py-6">
          <Loader2 className="w-6 h-6 text-primary-600 animate-spin" />
        </div>
      ) : logs.length === 0 ? (
        <EmptyState
          icon={Shield}
          title="No access records"
          description="When an agent accesses your data at a service center, it will be logged here."
        />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3 text-xs font-medium text-gray-500">Date</th>
                <th className="text-left py-2 px-3 text-xs font-medium text-gray-500">Agent / Center</th>
                <th className="text-left py-2 px-3 text-xs font-medium text-gray-500">Purpose</th>
                <th className="text-left py-2 px-3 text-xs font-medium text-gray-500">Status</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-2 px-3 text-gray-700">{formatDate(log.session_start)}</td>
                  <td className="py-2 px-3 text-gray-700">{log.agent_name || 'Agent'}</td>
                  <td className="py-2 px-3 text-gray-600">{log.purpose}</td>
                  <td className="py-2 px-3">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                      log.status === 'active' ? 'bg-green-100 text-green-700' :
                      log.status === 'ended' ? 'bg-gray-100 text-gray-600' :
                      'bg-red-100 text-red-600'
                    }`}>
                      {log.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
